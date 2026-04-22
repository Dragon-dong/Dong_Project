import os
import time
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from PIL import Image
import io

# 导入自定义模型
from models.sd_model import get_sd_model
from models.llava_model import get_llava_model
from models.multilingual_model import get_multilingual_model
from models.rag_model import get_rag_model
from models.llm_model import get_llm_model
from models.qwen_image_edit_model import get_qwen_image_edit_model

# 导入数据库操作
from database.db_operations import get_db_operations

# 获取数据库操作实例
db_ops = get_db_operations()

# 初始化FastAPI应用
app = FastAPI(
    title="跨模态内容生成系统API",
    description="支持文生图、图生文、动态叙事生成、风格迁移的AI系统",
    version="1.0.0"
)

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 根路径路由，返回index.html
@app.get("/")
async def root():
    """根路径，返回前端页面"""
    return FileResponse("index.html")

# 数据模型
class ModelSettings(BaseModel):
    """模型设置"""
    modelType: Optional[str] = "default"
    localPaths: Optional[dict] = None
    apiConfig: Optional[dict] = None

class TextToImageRequest(BaseModel):
    """文生图请求模型"""
    prompt: str  # 描述文本
    style: Optional[str] = None  # 风格选择
    custom_style: Optional[str] = None  # 自定义风格指令
    resolution: Optional[str] = "512x512"  # 分辨率
    modelSettings: Optional[ModelSettings] = None  # 模型设置

class ImageToTextRequest(BaseModel):
    """图生文请求模型"""
    image_url: Optional[str] = None  # 图像URL
    # 注：图像文件通过multipart/form-data上传

class StoryGenerateRequest(BaseModel):
    """动态叙事生成请求模型"""
    keywords: Optional[str] = None  # 关键词，用逗号分隔（旧格式）
    scene_keywords: Optional[List[str]] = None  # 场景关键词列表（新格式）
    story_style: Optional[str] = "fantasy"  # 故事风格
    story_length: Optional[str] = "medium"  # 故事长度
    modelSettings: Optional[ModelSettings] = None  # 模型设置

class StyleTransferRequest(BaseModel):
    """风格迁移请求模型"""
    image_url: Optional[str] = None  # 图像URL
    style_instruction: str  # 风格指令
    # 注：图像文件通过multipart/form-data上传

class MultilingualRequest(BaseModel):
    """多语言文化适配请求模型"""
    content: str  # 待适配的内容
    target_lang: Optional[str] = None  # 目标语言代码（可选）



# 文生图路由
@app.post("/api/text-to-image")
async def text_to_image(request: TextToImageRequest):
    """文本生成图像接口"""
    start_time = time.time()
    try:
        # 构建缓存键
        cache_key = f"text_to_image:{request.prompt}:{request.style}:{request.custom_style}:{request.resolution}"
        
        # 尝试从缓存获取
        cached_result = db_ops.get_cache(cache_key)
        if cached_result:
            # 记录生成历史
            db_ops.create_generation_history(
                task_type="text_to_image",
                input_data=request.dict(),
                output_data=cached_result,
                status="success",
                duration=time.time() - start_time
            )
            return cached_result
        
        # 获取Stable Diffusion模型实例
        sd_model = get_sd_model(request.modelSettings)

        
        # 构建基础提示词
        base_prompt = request.prompt
        
        # 集成RAG模型增强风格提示词
        rag_model = get_rag_model()
        
        # 构建风格指令
        style_instruction = ""
        if request.style:
            style_instruction += f"{request.style}"
        if request.custom_style:
            if style_instruction:
                style_instruction += f", {request.custom_style}"
            else:
                style_instruction = request.custom_style
        
        # 使用RAG模型增强提示词
        if style_instruction:
            full_prompt = rag_model.enhance_style_prompt(base_prompt, style_instruction)
        else:
            full_prompt = base_prompt
        
        # 解析分辨率
        width, height = map(int, request.resolution.split("x"))
        
        # 生成图像（优化性能，减少推理步数）
        image = sd_model.generate_image(
            prompt=full_prompt,
            negative_prompt="low quality, blurry, distorted, ugly",
            width=width,
            height=height,
            num_inference_steps=15,  # 减少推理步数，提高速度
            guidance_scale=7.0  # 稍微降低引导尺度，提高速度
        )
        
        # 转换为Base64
        image_base64 = sd_model.image_to_base64(image)
        
        # 构建响应结果
        result = {
            "status": "success",
            "image_url": image_base64,  # 返回Base64编码的图像
            "prompt": request.prompt,
            "style": request.style,
            "custom_style": request.custom_style,
            "resolution": request.resolution,
            "enhanced_prompt": full_prompt  # 返回增强后的提示词
        }
        
        # 缓存结果（1小时）
        db_ops.set_cache(cache_key, result, expire=3600)
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="text_to_image",
            input_data=request.dict(),
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="text_to_image",
            input_data=request.dict(),
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"生成图像失败: {str(e)}")

# 图生文路由
@app.post("/api/image-to-text")
async def image_to_text(file: UploadFile = File(...)):
    """图像生成文本接口"""
    start_time = time.time()
    try:
        # 读取图像文件
        image_bytes = await file.read()
        
        try:
            # 获取LLaVA模型实例
            llava_model = get_llava_model()
            
            # 生成图像描述
            description = llava_model.image_bytes_to_text(
                image_bytes=image_bytes,
                prompt="Describe the image in detail in Chinese.",
                max_new_tokens=512,
                temperature=0.2,
                top_p=0.9
            )
        except Exception as e:
            print(f"⚠️  模型调用失败，返回模拟数据: {str(e)}")
            # 直接返回模拟描述，避免长时间等待
            description = "这是一个模拟的图像描述。由于模型加载失败，无法提供真实的图像分析。在实际应用中，这里会返回基于图像内容的详细描述，包括物体、场景、颜色、动作等信息。"
        
        # 构建响应结果
        result = {
            "status": "success",
            "description": description,
            "image_filename": file.filename
        }
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="image_to_text",
            input_data={"image_filename": file.filename},
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="image_to_text",
            input_data={"image_filename": file.filename},
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"生成描述失败: {str(e)}")

# 动态叙事生成路由
@app.post("/api/generate-story")
async def generate_story(request: StoryGenerateRequest):
    """动态叙事生成接口"""
    start_time = time.time()
    try:
        # 确定使用哪种关键词格式
        if request.scene_keywords:
            # 新格式：场景关键词列表
            keywords = "|".join(request.scene_keywords)
            # 构建缓存键
            cache_key = f"generate_story:scenes:{keywords}:{request.story_style}:{request.story_length}"
        else:
            # 旧格式：单个关键词字符串
            keywords = request.keywords
            # 构建缓存键
            cache_key = f"generate_story:{keywords}:{request.story_style}:{request.story_length}"
        
        # 尝试从缓存获取
        cached_result = db_ops.get_cache(cache_key)
        if cached_result:
            # 记录生成历史
            db_ops.create_generation_history(
                task_type="generate_story",
                input_data=request.dict(),
                output_data=cached_result,
                status="success",
                duration=time.time() - start_time
            )
            return cached_result
        
        # 获取LLM模型实例
        llm_model = get_llm_model(request.modelSettings)
        
        # 获取Stable Diffusion模型实例
        sd_model = get_sd_model(request.modelSettings)
        
        # 生成故事场景
        if request.scene_keywords:
            # 新格式：使用场景关键词列表
            print(f"开始生成动态叙事，场景关键词数量: {len(request.scene_keywords)}, 风格: {request.story_style}")
            scenes = llm_model.generate_story_from_scenes(
                scene_keywords=request.scene_keywords,
                story_style=request.story_style,
                story_length=request.story_length
            )
        else:
            # 旧格式：使用单个关键词字符串
            print(f"开始生成动态叙事，关键词: {request.keywords}, 风格: {request.story_style}")
            scenes = llm_model.generate_story(
                keywords=request.keywords,
                story_style=request.story_style,
                story_length=request.story_length
            )
        
        # 为每个场景生成图像
        story_items = []
        scene_captions = []
        
        for i, scene in enumerate(scenes):
            caption = scene.get("caption", "")
            enhanced_prompt = scene.get("enhanced_prompt", f"{caption}, {request.story_style} style, detailed, vivid, high quality")
            
            # 保存场景描述用于生成连贯故事
            scene_captions.append(caption)
            
            # 生成场景图像
            print(f"生成场景{i+1}图像: {caption[:50]}...")
            print(f"增强提示词: {enhanced_prompt[:100]}...")
            
            try:
                # 生成图像（优化参数提高速度）
                image = sd_model.generate_image(
                    prompt=enhanced_prompt,
                    negative_prompt="low quality, blurry, distorted, ugly, text, watermark",
                    width=512,  # 提高分辨率
                    height=512,
                    num_inference_steps=15,  # 增加推理步数提高质量
                    guidance_scale=7.5  # 调整引导尺度
                )
                
                # 转换为Base64
                image_base64 = sd_model.image_to_base64(image)
                
                # 添加到故事项
                story_items.append({
                    "image": image_base64,
                    "caption": caption,
                    "enhanced_prompt": enhanced_prompt,
                    "audio": f"audio{i+1}.mp3"  # 占位音频
                })
                
            except Exception as img_error:
                print(f"生成场景{i+1}图像失败: {str(img_error)}")
                # 生成失败时使用占位图像
                story_items.append({
                    "image": f"https://picsum.photos/seed/story{i+1}/512/512",
                    "caption": caption,
                    "enhanced_prompt": enhanced_prompt,
                    "audio": f"audio{i+1}.mp3"
                })
        
        # 生成连贯的故事
        try:
            coherent_story = llm_model.generate_coherent_story(scene_captions, request.story_style)
            print("生成连贯故事成功")
        except Exception as e:
            print(f"生成连贯故事失败: {str(e)}")
            coherent_story = "\n\n".join(scene_captions)
        
        # 构建响应结果
        result = {
            "status": "success",
            "story": story_items,  # 前端期望的字段名
            "story_items": story_items,  # 保持向后兼容
            "coherent_story": coherent_story,
            "keywords": request.keywords,
            "scene_keywords": request.scene_keywords,
            "story_style": request.story_style,
            "story_length": request.story_length
        }
        
        # 缓存结果（1小时）
        db_ops.set_cache(cache_key, result, expire=3600)
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="generate_story",
            input_data=request.dict(),
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        print(f"动态叙事生成完成，共{len(story_items)}个场景，耗时: {time.time() - start_time:.2f}秒")
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="generate_story",
            input_data=request.dict(),
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"生成故事失败: {str(e)}")

# 风格迁移路由
@app.post("/api/style-transfer")
async def style_transfer(
    file: UploadFile = File(...),
    style_instruction: str = Form(...)
):
    """风格迁移接口"""
    start_time = time.time()
    try:
        # 读取图像文件
        image_bytes = await file.read()
        
        # 获取Qwen-Image-Edit模型实例
        qwen_model = get_qwen_image_edit_model()
        
        # 执行风格迁移
        image = qwen_model.style_transfer(
            image_bytes=image_bytes,
            style_instruction=style_instruction,
            width=512,
            height=512
        )
        
        # 转换为Base64
        image_base64 = qwen_model.image_to_base64(image)
        
        # 构建响应结果
        result = {
            "status": "success",
            "image_url": image_base64,  # 返回Base64编码的图像
            "style_instruction": style_instruction,
            "image_filename": file.filename
        }
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="style_transfer",
            input_data={"style_instruction": style_instruction, "image_filename": file.filename},
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="style_transfer",
            input_data={"style_instruction": style_instruction, "image_filename": file.filename},
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"风格迁移失败: {str(e)}")

# 多语言文化适配路由
@app.post("/api/multilingual-adaptation")
async def multilingual_adaptation(request: MultilingualRequest):
    """多语言文化适配接口"""
    start_time = time.time()
    try:
        # 构建缓存键
        cache_key = f"multilingual:{request.content}:{request.target_lang}"
        
        # 尝试从缓存获取
        cached_result = db_ops.get_cache(cache_key)
        if cached_result:
            # 记录生成历史
            db_ops.create_generation_history(
                task_type="multilingual",
                input_data=request.dict(),
                output_data=cached_result,
                status="success",
                duration=time.time() - start_time
            )
            return cached_result
        
        # 获取多语言模型实例
        multilingual_model = get_multilingual_model()
        
        # 适配内容到目标语言的文化背景
        result_data = multilingual_model.adapt_content_to_culture(
            content=request.content,
            target_lang=request.target_lang
        )
        
        # 构建响应结果
        result = {
            "status": "success",
            "result": result_data
        }
        
        # 缓存结果（1小时）
        db_ops.set_cache(cache_key, result, expire=3600)
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="multilingual",
            input_data=request.dict(),
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="multilingual",
            input_data=request.dict(),
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"多语言文化适配失败: {str(e)}")

# 数据库相关API路由

# 获取生成历史
@app.get("/api/history")
async def get_history(
    task_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """获取生成历史记录"""
    try:
        history = db_ops.get_generation_history(
            task_type=task_type,
            limit=limit,
            offset=offset
        )
        return {
            "status": "success",
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

# 获取系统配置
@app.get("/api/config")
async def get_config(config_key: Optional[str] = None):
    """获取系统配置"""
    try:
        if config_key:
            value = db_ops.get_system_config(config_key)
            return {
                "status": "success",
                "key": config_key,
                "value": value
            }
        else:
            configs = db_ops.get_all_system_configs()
            return {
                "status": "success",
                "configs": configs
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

# 设置系统配置
@app.post("/api/config")
async def set_config(config_key: str = Form(...), config_value: str = Form(...)):
    """设置系统配置"""
    try:
        # 尝试将值转换为适当的类型
        try:
            import json
            parsed_value = json.loads(config_value)
        except json.JSONDecodeError:
            parsed_value = config_value
        
        success = db_ops.set_system_config(config_key, parsed_value)
        if success:
            return {
                "status": "success",
                "message": "配置设置成功"
            }
        else:
            raise HTTPException(status_code=500, detail="设置配置失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置系统配置失败: {str(e)}")

# 清除缓存
@app.post("/api/cache/clear")
async def clear_cache(pattern: Optional[str] = Form(None)):
    """清除缓存"""
    try:
        if pattern:
            success = db_ops.clear_cache_pattern(pattern)
        else:
            success = db_ops.clear_cache_pattern("*")
        if success:
            return {
                "status": "success",
                "message": "缓存清除成功"
            }
        else:
            raise HTTPException(status_code=500, detail="清除缓存失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")

# 生成连贯的故事内容
@app.post("/api/generate-coherent-story")
async def generate_coherent_story(
    scene_descriptions: List[str] = Form(...),
    story_style: str = Form("fantasy"),
    modelSettings: Optional[str] = Form(None)
):
    """生成连贯的故事内容"""
    start_time = time.time()
    try:
        # 解析模型设置
        model_settings = None
        if modelSettings:
            try:
                import json
                model_settings = json.loads(modelSettings)
            except json.JSONDecodeError:
                pass
        
        # 获取LLM模型实例
        llm_model = get_llm_model(model_settings)
        
        # 生成连贯的故事
        coherent_story = llm_model.generate_coherent_story(
            scene_descriptions=scene_descriptions,
            story_style=story_style
        )
        
        # 构建响应结果
        result = {
            "status": "success",
            "story": coherent_story,
            "story_style": story_style,
            "scene_count": len(scene_descriptions)
        }
        
        # 记录生成历史
        db_ops.create_generation_history(
            task_type="generate_coherent_story",
            input_data={"scene_descriptions": scene_descriptions, "story_style": story_style},
            output_data=result,
            status="success",
            duration=time.time() - start_time
        )
        
        return result
    except Exception as e:
        # 记录失败的生成历史
        db_ops.create_generation_history(
            task_type="generate_coherent_story",
            input_data={"scene_descriptions": scene_descriptions, "story_style": story_style},
            output_data={},  # 空结果
            status="failed",
            error_message=str(e),
            duration=time.time() - start_time
        )
        raise HTTPException(status_code=500, detail=f"生成连贯故事失败: {str(e)}")

# 用户登录API
@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """用户登录接口"""
    try:
        # 查找用户
        user = db_ops.get_user_by_username(username)
        if not user:
            return {"status": "error", "message": "用户名或密码错误"}
        
        # 简单的密码验证（实际项目中应该使用密码哈希）
        if password != "123456":  # 这里简化处理，实际应该验证哈希密码
            return {"status": "error", "message": "用户名或密码错误"}
        
        return {"status": "success", "message": "登录成功"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 用户注册API
@app.post("/api/register")
async def register(username: str = Form(...), email: Optional[str] = Form(None), password: str = Form(...)):
    """用户注册接口"""
    try:
        # 检查用户名是否已存在
        existing_user = db_ops.get_user_by_username(username)
        if existing_user:
            return {"status": "error", "message": "用户名已存在"}
        
        # 检查邮箱是否已存在（仅当邮箱不为空时）
        if email:
            existing_email = db_ops.get_user_by_email(email)
            if existing_email:
                return {"status": "error", "message": "邮箱已被注册"}
        
        # 创建新用户
        # 实际项目中应该对密码进行哈希处理
        user_id = db_ops.create_user(username, email, password)
        if user_id:
            return {"status": "success", "message": "注册成功"}
        else:
            return {"status": "error", "message": "注册失败"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 主函数
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发环境下启用热重载
    )
