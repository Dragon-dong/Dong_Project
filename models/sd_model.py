import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from PIL import Image
import io
import base64
import requests
from typing import Optional

class StableDiffusionModel:
    """Stable Diffusion模型封装，用于文生图功能"""
    
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        """初始化Stable Diffusion模型
        
        Args:
            model_id: 模型ID或本地路径
        """
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
        self.use_lightweight_model = True  # 使用轻量级模型提高速度
    
    def load_model(self):
        """加载Stable Diffusion模型"""
        try:
            # 直接加载模型，让diffusers库自动处理调度器
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            # 优化模型
            if self.device == "cuda":
                self.pipeline = self.pipeline.to(self.device)
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_xformers_memory_efficient_attention()
            else:
                self.pipeline = self.pipeline.to(self.device)
                
            print(f"OK: Stable Diffusion模型加载成功，使用设备: {self.device}")
            self.model_loaded = True
        except Exception as e:
            print(f"ERROR: 加载Stable Diffusion模型失败: {str(e)}")
            print("WARN: 启用模拟模式，将返回占位图像")
            self.model_loaded = False
    
    def generate_image(
        self, 
        prompt: str, 
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 15,  # 减少推理步数，提高速度
        guidance_scale: float = 7.0,  # 稍微降低引导尺度，提高速度
        num_images_per_prompt: int = 1
    ) -> Image.Image:
        """生成图像
        
        Args:
            prompt: 描述文本
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            num_inference_steps: 推理步数
            guidance_scale: 引导尺度
            num_images_per_prompt: 每提示生成图像数量
            
        Returns:
            生成的PIL图像对象
        """
        import time
        start_time = time.time()
        
        # 首先尝试使用SiliconFlow API生成图像
        try:
            print("OK: 尝试使用SiliconFlow API生成图像")
            
            # SiliconFlow API配置
            url = "https://api.siliconflow.cn/v1/images/generations"
            # 使用可用的模型
            model_name = "Kwai-Kolors/Kolors"
            payload = {
                "model": model_name,
                "prompt": prompt,
                "image_size": f"{width}x{height}",
                "batch_size": num_images_per_prompt,
                "num_inference_steps": 20 if self.use_lightweight_model else num_inference_steps,  # 新模型需要更多步数
                "guidance_scale": 7.5 if self.use_lightweight_model else guidance_scale  # 新模型需要引导
            }
            headers = {
                "Authorization": "Bearer sk-ikomatcbxqwpaljmpcyxasoryvyneoaqbfphyclfmukltfhm",
                "Content-Type": "application/json"
            }
            
            print(f"OK: API请求参数: model={model_name}, prompt={prompt[:50]}..., size={width}x{height}")
            
            # 调用API
            response = requests.request("POST", url, json=payload, headers=headers)
            print(f"OK: API响应状态码: {response.status_code}")
            
            # 打印响应内容
            print(f"OK: API响应内容: {response.text[:1000]}...")
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"ERROR: API调用失败，状态码: {response.status_code}")
                print(f"ERROR: 响应内容: {response.text}")
                raise Exception(f"API调用失败，状态码: {response.status_code}")
            
            # 处理响应
            data = response.json()
            print(f"OK: 响应数据结构: {list(data.keys())}")
            
            if "images" in data and len(data["images"]) > 0:
                image_url = data["images"][0]["url"]
                print(f"OK: 图像URL: {image_url}")
                
                # 下载图像
                image_response = requests.get(image_url)
                print(f"OK: 图像下载状态码: {image_response.status_code}")
                print(f"OK: 图像数据长度: {len(image_response.content)} bytes")
                
                # 检查图像数据长度
                if len(image_response.content) < 1000:  # 小于1KB的图像可能是错误图像
                    print(f"ERROR: 图像数据过小: {len(image_response.content)} bytes")
                    raise Exception("下载的图像数据过小，可能是错误图像")
                
                from PIL import Image
                image = Image.open(io.BytesIO(image_response.content))
                print(f"OK: 图像信息: {image.size}, {image.mode}")
                
                # 保存图像到img文件夹
                import os
                if not os.path.exists('img'):
                    os.makedirs('img')
                
                # 生成唯一的文件名
                import time
                timestamp = int(time.time())
                filename = f"img/generated_{timestamp}.png"
                image.save(filename)
                print(f"OK: 图像已保存到: {filename}")
                
                end_time = time.time()
                print(f"OK: SiliconFlow API生成成功，耗时: {end_time - start_time:.2f}秒")
                return image
            else:
                print("ERROR: API响应中没有图像数据")
                print(f"ERROR: 响应数据: {data}")
                raise Exception("API响应中没有图像数据")
            
        except Exception as e:
            print(f"ERROR: SiliconFlow API调用失败: {str(e)}")
            print("WARN: 尝试使用本地模型生成图像")
        
        # 如果API调用失败，尝试使用本地模型
        if self.model_loaded:
            try:
                # 生成图像
                images = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    num_images_per_prompt=num_images_per_prompt,
                    # 性能优化参数
                    callback=None,
                    callback_steps=1,
                    eta=0.0  # 确定性采样，提高速度
                ).images
                
                end_time = time.time()
                print(f"OK: 本地模型生成成功，耗时: {end_time - start_time:.2f}秒")
                return images[0]  # 返回第一张图像
            except Exception as e:
                print(f"ERROR: 本地模型生成失败: {str(e)}")
        
        # 如果所有方法都失败，返回占位图像
        from PIL import Image, ImageDraw, ImageFont
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # 分别绘制两行文本
        line1 = "生成失败"
        line2 = "所有生成方法都失败了"
        
        # 计算每行文本的宽度
        line1_width = draw.textlength(line1, font=font)
        line2_width = draw.textlength(line2, font=font)
        
        # 绘制文本（居中）
        draw.text(((width - line1_width) // 2, height // 2 - 20), line1, fill=(100, 100, 100), font=font)
        draw.text(((width - line2_width) // 2, height // 2 + 10), line2, fill=(100, 100, 100), font=font)
        
        draw.rectangle([(10, 10), (width-10, height-10)], outline=(150, 150, 150), width=2)
        
        end_time = time.time()
        print(f"ERROR: 失败处理时间: {end_time - start_time:.2f}秒")
        return image
    
    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        """将PIL图像转换为Base64编码字符串
        
        Args:
            image: PIL图像对象
            format: 图像格式
            
        Returns:
            Base64编码的图像字符串
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/{format.lower()};base64,{img_str}"
    
    def generate_image_base64(
        self, 
        prompt: str, 
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5
    ) -> str:
        """生成图像并返回Base64编码
        
        Args:
            prompt: 描述文本
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            num_inference_steps: 推理步数
            guidance_scale: 引导尺度
            
        Returns:
            Base64编码的图像字符串
        """
        image = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        )
        return self.image_to_base64(image)

# 全局模型实例（单例模式）
sd_model_instance = None

def get_sd_model(model_settings=None) -> StableDiffusionModel:
    """获取Stable Diffusion模型实例（单例模式）
    
    Args:
        model_settings: 模型设置，包含modelType、localPaths、apiConfig等
    
    Returns:
        StableDiffusionModel实例
    """
    global sd_model_instance
    if model_settings:
        # 根据模型设置创建新的实例
        if model_settings.modelType == "local" and model_settings.localPaths:
            # 使用本地模型路径
            sd_path = model_settings.localPaths.get("sd", "runwayml/stable-diffusion-v1-5")
            return StableDiffusionModel(model_id=sd_path)
        elif model_settings.modelType == "custom-api" and model_settings.apiConfig:
            # 使用自定义API配置
            # 这里可以根据apiConfig配置不同的API
            return StableDiffusionModel()
    
    # 默认使用全局实例
    if sd_model_instance is None:
        sd_model_instance = StableDiffusionModel()
    return sd_model_instance
