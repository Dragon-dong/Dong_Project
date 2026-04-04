import requests
import base64
from PIL import Image
import io
import os
import time
from typing import Optional, Dict, Any, List

class QwenImageEditModel:
    """Qwen-Image-Edit模型封装，用于风格迁移功能"""
    
    def __init__(self):
        """初始化Qwen-Image-Edit模型"""
        # 使用阿里云百炼API Key
        self.api_key = "sk-a2f939f05191490184744855395f348c"
        # 使用与LLaVA模型相同的API endpoint
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model_loaded = True
        # 风格参数映射表
        self.style_parameters = {
            "写实风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "卡通风格": {"num_inference_steps": 15, "guidance_scale": 6.5},
            "油画风格": {"num_inference_steps": 25, "guidance_scale": 8.0},
            "水彩风格": {"num_inference_steps": 18, "guidance_scale": 7.0},
            "赛博朋克风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "中国风": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "梵高风格": {"num_inference_steps": 25, "guidance_scale": 8.0},
            "宫崎骏风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "蒸汽朋克风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "水墨风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "印象派风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "抽象风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "哥特风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "波普艺术风格": {"num_inference_steps": 16, "guidance_scale": 6.8},
            "未来主义风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "复古风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "极简主义风格": {"num_inference_steps": 15, "guidance_scale": 6.5},
            "梦幻风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "科幻风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "手绘风格": {"num_inference_steps": 18, "guidance_scale": 7.0}
        }
        # 加载RAG模型
        from models.rag_model import get_rag_model
        self.rag_model = get_rag_model()
        
        # 预加载其他模型以提高性能
        try:
            from models.llava_model import get_llava_model
            from models.sd_model import get_sd_model
            # 预热模型实例
            get_llava_model()
            get_sd_model()
            print("OK: 模型预热完成")
        except Exception as e:
            print(f"WARN: 模型预热失败: {str(e)}")
        
        # 结果缓存
        self.result_cache = {}
        # 模型实例缓存
        self.model_cache = {}
        
        print("OK: 风格迁移模型初始化成功")
    
    def _generate_cache_key(self, image_bytes: bytes, style_instruction: str, width: int, height: int, style_strength: float, style_reference: Optional[bytes] = None) -> str:
        """生成缓存键
        
        Args:
            image_bytes: 原始图像字节数据
            style_instruction: 风格指令
            width: 输出图像宽度
            height: 输出图像高度
            style_strength: 风格强度
            style_reference: 风格参考图像（可选）
            
        Returns:
            缓存键字符串
        """
        import hashlib
        
        # 计算图像哈希
        image_hash = hashlib.md5(image_bytes).hexdigest()
        
        # 计算参考图像哈希（如果有）
        ref_hash = ""  
        if style_reference:
            ref_hash = hashlib.md5(style_reference).hexdigest()
        
        # 生成缓存键
        cache_key = f"{image_hash}_{style_instruction}_{width}_{height}_{style_strength:.2f}_{ref_hash}"
        return cache_key
    
    def style_transfer(
        self, 
        image_bytes: bytes, 
        style_instruction: str,
        width: int = 512,
        height: int = 512,
        style_reference: Optional[bytes] = None,
        style_strength: float = 0.7,
        evaluation: bool = False,
        max_retries: int = 2,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """执行风格迁移
        
        Args:
            image_bytes: 原始图像字节数据
            style_instruction: 风格指令
            width: 输出图像宽度
            height: 输出图像高度
            style_reference: 风格参考图像（可选）
            style_strength: 风格强度（0-1）
            evaluation: 是否返回评估结果
            max_retries: 最大重试次数
            use_cache: 是否使用缓存
            
        Returns:
            包含风格迁移后图像和评估结果的字典
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(
            image_bytes=image_bytes,
            style_instruction=style_instruction,
            width=width,
            height=height,
            style_strength=style_strength,
            style_reference=style_reference
        )
        
        # 检查缓存
        if use_cache and cache_key in self.result_cache:
            print("OK: 从缓存中获取结果")
            cached_result = self.result_cache[cache_key].copy()
            cached_result["from_cache"] = True
            return cached_result
        
        start_time = time.time()
        retries = 0
        
        while retries <= max_retries:
            try:
                # 首先使用LLaVA模型分析原始图像内容
                from models.llava_model import get_llava_model
                llava_model = get_llava_model()
                
                try:
                    # 生成详细的图像描述
                    image_description = llava_model.image_bytes_to_text(
                        image_bytes=image_bytes,
                        prompt="请详细描述这张图像的内容，包括人物、场景、物体、颜色、构图等主要元素，用中文描述。",
                        max_new_tokens=300,  # 更详细的描述
                        temperature=0.2,
                        top_p=0.9
                    )
                    print(f"OK: 图像内容分析成功: {image_description[:50]}...")
                except Exception as desc_error:
                    print(f"WARN: 图像内容分析失败: {str(desc_error)}")
                    image_description = "一个人物形象"
                
                # 处理风格参考图像
                style_reference_description = ""
                if style_reference:
                    try:
                        # 分析风格参考图像
                        style_ref_description = llava_model.image_bytes_to_text(
                            image_bytes=style_reference,
                            prompt="请详细描述这张图像的艺术风格，包括色彩特点、笔触风格、构图特征、光影处理等方面。",
                            max_new_tokens=300,
                            temperature=0.2,
                            top_p=0.9
                        )
                        style_reference_description = f"参考图像风格: {style_ref_description}"
                        print(f"OK: 风格参考图像分析成功")
                    except Exception as ref_error:
                        print(f"WARN: 风格参考图像分析失败: {str(ref_error)}")
                
                # 使用RAG模型增强风格提示词
                try:
                    enhanced_prompt = self.rag_model.enhance_style_prompt(
                        original_prompt=image_description,
                        style_instruction=style_instruction
                    )
                    # 添加风格强度参数和参考图像描述
                    enhanced_prompt += f", 风格强度: {style_strength}, 保留原始内容和构图，高质量，细节丰富"
                    if style_reference_description:
                        enhanced_prompt += f", {style_reference_description}"
                except Exception as rag_error:
                    print(f"WARN: RAG增强失败: {str(rag_error)}")
                    # 降级：使用基础提示词
                    enhanced_prompt = f"{image_description}，{style_instruction}风格，风格强度: {style_strength}"
                    if style_reference_description:
                        enhanced_prompt += f"，{style_reference_description}"
                
                # 确定生成参数
                try:
                    generation_params = self._get_style_parameters(style_instruction)
                    # 如果有风格参考图像，调整参数以更好地匹配参考风格
                    if style_reference:
                        generation_params["guidance_scale"] = min(8.5, generation_params["guidance_scale"] + 0.5)
                except Exception as params_error:
                    print(f"WARN: 参数获取失败: {str(params_error)}")
                    # 降级：使用默认参数
                    generation_params = {"num_inference_steps": 15, "guidance_scale": 7.0}
                    if style_reference:
                        generation_params["guidance_scale"] = 8.0
                
                # 使用SD模型生成图像
                from models.sd_model import get_sd_model
                sd_model = get_sd_model()
                
                try:
                    # 生成图像
                    image = sd_model.generate_image(
                        prompt=enhanced_prompt,
                        negative_prompt="低质量，模糊，扭曲，丑陋，改变原始内容，颜色失真，构图混乱",
                        width=width,
                        height=height,
                        num_inference_steps=generation_params["num_inference_steps"],
                        guidance_scale=generation_params["guidance_scale"]
                    )
                except Exception as gen_error:
                    print(f"WARN: 图像生成失败 (尝试 {retries+1}/{max_retries+1}): {str(gen_error)}")
                    retries += 1
                    if retries > max_retries:
                        # 最终降级：返回原始图像
                        raise Exception(f"图像生成失败，已达到最大重试次数: {str(gen_error)}")
                    # 等待一段时间后重试
                    time.sleep(1)
                    continue
                
                # 保存图像到img文件夹
                try:
                    if not os.path.exists('img'):
                        os.makedirs('img')
                    
                    # 生成唯一的文件名
                    timestamp = int(time.time())
                    filename = f"img/style_transferred_{timestamp}.png"
                    image.save(filename)
                    print(f"OK: 风格迁移图像已保存到: {filename}")
                except Exception as save_error:
                    print(f"WARN: 图像保存失败: {str(save_error)}")
                    # 继续执行，不影响返回结果
                    filename = None
                
                end_time = time.time()
                print(f"OK: 风格迁移成功，耗时: {end_time - start_time:.2f}秒")
                
                # 构建返回结果
                result = {
                    "image": image,
                    "filename": filename,
                    "prompt": enhanced_prompt,
                    "execution_time": end_time - start_time,
                    "retries": retries
                }
                
                # 如果需要评估，添加评估结果
                if evaluation:
                    try:
                        evaluation_result = self.evaluate_style_transfer(
                            original_image=Image.open(io.BytesIO(image_bytes)),
                            styled_image=image,
                            style_instruction=style_instruction
                        )
                        result["evaluation"] = evaluation_result
                    except Exception as eval_error:
                        print(f"WARN: 评估失败: {str(eval_error)}")
                        # 继续执行，不影响返回结果
                
                # 保存到缓存
                if use_cache:
                    # 限制缓存大小
                    if len(self.result_cache) > 100:
                        # 删除最早的缓存项
                        oldest_key = next(iter(self.result_cache))
                        del self.result_cache[oldest_key]
                    # 保存到缓存
                    self.result_cache[cache_key] = result.copy()
                    # 移除图像对象以减少内存占用
                    if "image" in self.result_cache[cache_key]:
                        del self.result_cache[cache_key]["image"]
                
                return result
                
            except Exception as e:
                print(f"ERROR: 风格迁移失败: {str(e)}")
                
                # 最终降级方案：返回原始图像
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                    image = image.resize((width, height))
                    return {
                        "image": image,
                        "error": str(e),
                        "retries": retries
                    }
                except Exception as final_error:
                    print(f"CRITICAL: 最终降级失败: {str(final_error)}")
                    # 返回错误信息
                    return {
                        "error": f"风格迁移完全失败: {str(e)}",
                        "retries": retries
                    }
    
    def _get_style_parameters(self, style_instruction: str) -> Dict[str, Any]:
        """根据风格指令获取生成参数
        
        Args:
            style_instruction: 风格指令
            
        Returns:
            生成参数字典
        """
        # 检索相关风格知识
        style_knowledge = self.rag_model.retrieve_style_knowledge(style_instruction, top_k=1)
        
        if style_knowledge:
            style_name = style_knowledge[0].get("style_name", "")
            if style_name in self.style_parameters:
                print(f"OK: 使用 {style_name} 的专用参数")
                return self.style_parameters[style_name]
        
        # 基于风格类型的智能参数调整
        style_type = self._classify_style_type(style_instruction)
        parameters = self._get_parameters_by_style_type(style_type)
        
        print(f"OK: 使用 {style_type} 风格类型的参数")
        return parameters
    
    def _classify_style_type(self, style_instruction: str) -> str:
        """分类风格类型
        
        Args:
            style_instruction: 风格指令
            
        Returns:
            风格类型
        """
        style_instruction_lower = style_instruction.lower()
        
        # 艺术风格分类
        if any(keyword in style_instruction_lower for keyword in ["油画", "oil painting"]):
            return "油画风格"
        elif any(keyword in style_instruction_lower for keyword in ["水彩", "watercolor"]):
            return "水彩风格"
        elif any(keyword in style_instruction_lower for keyword in ["卡通", "cartoon", "anime"]):
            return "卡通风格"
        elif any(keyword in style_instruction_lower for keyword in ["中国风", "古风", "chinese"]):
            return "中国风"
        elif any(keyword in style_instruction_lower for keyword in ["赛博朋克", "cyberpunk"]):
            return "赛博朋克风格"
        elif any(keyword in style_instruction_lower for keyword in ["写实", "realistic"]):
            return "写实风格"
        elif any(keyword in style_instruction_lower for keyword in ["梵高", "van gogh"]):
            return "梵高风格"
        elif any(keyword in style_instruction_lower for keyword in ["宫崎骏", "ghibli"]):
            return "宫崎骏风格"
        elif any(keyword in style_instruction_lower for keyword in ["蒸汽朋克", "steampunk"]):
            return "蒸汽朋克风格"
        elif any(keyword in style_instruction_lower for keyword in ["水墨", "ink"]):
            return "水墨风格"
        elif any(keyword in style_instruction_lower for keyword in ["印象派", "impressionist"]):
            return "印象派风格"
        elif any(keyword in style_instruction_lower for keyword in ["抽象", "abstract"]):
            return "抽象风格"
        elif any(keyword in style_instruction_lower for keyword in ["哥特", "gothic"]):
            return "哥特风格"
        elif any(keyword in style_instruction_lower for keyword in ["波普", "pop art"]):
            return "波普艺术风格"
        elif any(keyword in style_instruction_lower for keyword in ["未来主义", "futurism"]):
            return "未来主义风格"
        elif any(keyword in style_instruction_lower for keyword in ["复古", "vintage", "retro"]):
            return "复古风格"
        elif any(keyword in style_instruction_lower for keyword in ["极简", "minimalist"]):
            return "极简主义风格"
        elif any(keyword in style_instruction_lower for keyword in ["梦幻", "dreamy"]):
            return "梦幻风格"
        elif any(keyword in style_instruction_lower for keyword in ["科幻", "sci-fi", "science fiction"]):
            return "科幻风格"
        elif any(keyword in style_instruction_lower for keyword in ["手绘", "hand-drawn"]):
            return "手绘风格"
        else:
            return "默认风格"
    
    def _get_parameters_by_style_type(self, style_type: str) -> Dict[str, Any]:
        """根据风格类型获取参数
        
        Args:
            style_type: 风格类型
            
        Returns:
            生成参数字典
        """
        # 扩展的风格参数表
        extended_style_parameters = {
            "油画风格": {"num_inference_steps": 25, "guidance_scale": 8.0},
            "水彩风格": {"num_inference_steps": 18, "guidance_scale": 7.0},
            "卡通风格": {"num_inference_steps": 15, "guidance_scale": 6.5},
            "中国风": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "赛博朋克风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "写实风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "梵高风格": {"num_inference_steps": 25, "guidance_scale": 8.0},
            "宫崎骏风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "蒸汽朋克风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "水墨风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "印象派风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "抽象风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "哥特风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "波普艺术风格": {"num_inference_steps": 16, "guidance_scale": 6.8},
            "未来主义风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "复古风格": {"num_inference_steps": 22, "guidance_scale": 7.8},
            "极简主义风格": {"num_inference_steps": 15, "guidance_scale": 6.5},
            "梦幻风格": {"num_inference_steps": 18, "guidance_scale": 7.2},
            "科幻风格": {"num_inference_steps": 20, "guidance_scale": 7.5},
            "手绘风格": {"num_inference_steps": 18, "guidance_scale": 7.0},
            "默认风格": {"num_inference_steps": 15, "guidance_scale": 7.0}
        }
        
        return extended_style_parameters.get(style_type, extended_style_parameters["默认风格"])
    
    def evaluate_style_transfer(
        self, 
        original_image: Image.Image, 
        styled_image: Image.Image, 
        style_instruction: str
    ) -> Dict[str, Any]:
        """评估风格迁移效果
        
        Args:
            original_image: 原始图像
            styled_image: 风格迁移后的图像
            style_instruction: 风格指令
            
        Returns:
            评估结果字典
        """
        try:
            # 简单的评估指标
            # 1. 内容保持度（通过图像尺寸和基本结构判断）
            content_similarity = self._calculate_content_similarity(original_image, styled_image)
            
            # 2. 风格匹配度（通过RAG模型分析）
            style_matching = self._calculate_style_matching(styled_image, style_instruction)
            
            # 3. 图像质量（通过基本图像属性判断）
            image_quality = self._calculate_image_quality(styled_image)
            
            # 综合评分
            overall_score = 0.3 * content_similarity + 0.5 * style_matching + 0.2 * image_quality
            
            return {
                "content_similarity": content_similarity,
                "style_matching": style_matching,
                "image_quality": image_quality,
                "overall_score": overall_score,
                "rating": self._get_rating(overall_score)
            }
        except Exception as e:
            print(f"WARN: 评估失败: {str(e)}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "rating": "无法评估"
            }
    
    def _calculate_content_similarity(self, original: Image.Image, styled: Image.Image) -> float:
        """计算内容保持度
        
        Args:
            original: 原始图像
            styled: 风格迁移后的图像
            
        Returns:
            相似度分数（0-1）
        """
        try:
            # 尺寸相似度
            size_similarity = min(original.width / styled.width, styled.width / original.width) * \
                            min(original.height / styled.height, styled.height / original.height)
            
            # 色彩分布相似度（使用直方图比较）
            # 确保图像模式相同
            if original.mode != styled.mode:
                original = original.convert('RGB')
                styled = styled.convert('RGB')
            
            # 计算直方图
            original_hist = original.histogram()
            styled_hist = styled.histogram()
            
            # 计算直方图相似度
            color_similarity = 0
            for o, s in zip(original_hist, styled_hist):
                color_similarity += min(o, s)
            color_similarity = color_similarity / max(sum(original_hist), sum(styled_hist))
            
            # 边缘检测相似度（简化版）
            edge_similarity = self._calculate_edge_similarity(original, styled)
            
            return (size_similarity * 0.3 + color_similarity * 0.4 + edge_similarity * 0.3)
        except Exception as e:
            print(f"WARN: 内容相似度计算失败: {str(e)}")
            return 0.5
    
    def _calculate_edge_similarity(self, original: Image.Image, styled: Image.Image) -> float:
        """计算边缘相似度
        
        Args:
            original: 原始图像
            styled: 风格迁移后的图像
            
        Returns:
            边缘相似度分数（0-1）
        """
        try:
            # 转换为灰度图
            original_gray = original.convert('L')
            styled_gray = styled.convert('L')
            
            # 调整大小以匹配
            if original_gray.size != styled_gray.size:
                styled_gray = styled_gray.resize(original_gray.size)
            
            # 简单的边缘检测（使用差异像素）
            width, height = original_gray.size
            edge_difference = 0
            
            for x in range(width):
                for y in range(height):
                    # 计算相邻像素的差异
                    if x > 0:
                        original_diff = abs(original_gray.getpixel((x, y)) - original_gray.getpixel((x-1, y)))
                        styled_diff = abs(styled_gray.getpixel((x, y)) - styled_gray.getpixel((x-1, y)))
                        edge_difference += abs(original_diff - styled_diff)
                    if y > 0:
                        original_diff = abs(original_gray.getpixel((x, y)) - original_gray.getpixel((x, y-1)))
                        styled_diff = abs(styled_gray.getpixel((x, y)) - styled_gray.getpixel((x, y-1)))
                        edge_difference += abs(original_diff - styled_diff)
            
            # 归一化
            max_difference = width * height * 255 * 2  # 最大可能差异
            edge_similarity = 1 - (edge_difference / max_difference)
            return max(0, min(1, edge_similarity))
        except:
            return 0.5
    
    def _calculate_style_matching(self, styled_image: Image.Image, style_instruction: str) -> float:
        """计算风格匹配度
        
        Args:
            styled_image: 风格迁移后的图像
            style_instruction: 风格指令
            
        Returns:
            匹配度分数（0-1）
        """
        try:
            # 生成图像描述
            from models.llava_model import get_llava_model
            llava_model = get_llava_model()
            
            # 将图像转换为字节
            buffer = io.BytesIO()
            styled_image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            
            # 生成图像描述
            image_description = llava_model.image_bytes_to_text(
                image_bytes=image_bytes,
                prompt="请详细描述这张图像的艺术风格，包括色彩特点、笔触风格、构图特征、光影处理等方面。",
                max_new_tokens=300,
                temperature=0.2,
                top_p=0.9
            )
            
            # 检索风格知识
            style_knowledge = self.rag_model.retrieve_style_knowledge(style_instruction, top_k=1)
            
            if style_knowledge:
                style_description = style_knowledge[0].get("description", "")
                if style_description:
                    # 使用LLaVA模型评估风格匹配度
                    evaluation_prompt = f"""
                    请评估以下生成的图像描述与目标风格描述的匹配程度，返回一个0-1之间的分数：
                    
                    目标风格描述：{style_description}
                    生成图像描述：{image_description}
                    
                    评估标准：
                    1. 色彩特点匹配度
                    2. 笔触风格匹配度
                    3. 构图特征匹配度
                    4. 整体风格一致性
                    
                    请只返回一个数字分数，不要有其他文字。
                    """
                    
                    try:
                        score_text = llava_model.text_to_text(
                            text=evaluation_prompt,
                            max_new_tokens=20,
                            temperature=0.1,
                            top_p=0.9
                        )
                        # 提取分数
                        score = float(score_text.strip())
                        return max(0, min(1, score))
                    except:
                        # 如果评估失败，使用关键词匹配
                        return self._calculate_keyword_match(image_description, style_description)
            
            # 如果没有风格知识，使用默认值
            return 0.6
        except Exception as e:
            print(f"WARN: 风格匹配度计算失败: {str(e)}")
            return 0.5
    
    def _calculate_keyword_match(self, text1: str, text2: str) -> float:
        """计算关键词匹配度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            匹配度分数（0-1）
        """
        try:
            # 提取关键词
            import re
            
            # 简单的关键词提取
            def extract_keywords(text):
                # 移除标点符号，转换为小写
                text = re.sub(r'[.,?!;:"\'()\[\]]', ' ', text.lower())
                # 分词
                words = text.split()
                # 过滤停用词
                stop_words = set(['的', '了', '和', '是', '在', '有', '为', '以', '我', '你', '他', '她', '它', '们'])
                keywords = [word for word in words if word not in stop_words and len(word) > 1]
                return set(keywords)
            
            # 提取关键词
            keywords1 = extract_keywords(text1)
            keywords2 = extract_keywords(text2)
            
            # 计算交集
            common_keywords = keywords1.intersection(keywords2)
            
            # 计算匹配度
            if len(keywords1) + len(keywords2) == 0:
                return 0.5
            
            match_score = 2 * len(common_keywords) / (len(keywords1) + len(keywords2))
            return match_score
        except:
            return 0.5
    
    def _calculate_image_quality(self, image: Image.Image) -> float:
        """计算图像质量
        
        Args:
            image: 待评估的图像
            
        Returns:
            质量分数（0-1）
        """
        try:
            # 检查图像尺寸
            size_score = 0.0
            if image.width >= 512 and image.height >= 512:
                size_score = 1.0
            elif image.width >= 256 and image.height >= 256:
                size_score = 0.7
            else:
                size_score = 0.4
            
            # 检查图像模式
            mode_score = 0.8 if image.mode in ["RGB", "RGBA"] else 0.5
            
            # 计算图像清晰度（基于边缘检测）
            clarity_score = self._calculate_image_clarity(image)
            
            # 计算图像色彩丰富度
            color_score = self._calculate_color_richness(image)
            
            # 综合评分
            return (size_score * 0.3 + mode_score * 0.2 + clarity_score * 0.3 + color_score * 0.2)
        except Exception as e:
            print(f"WARN: 图像质量计算失败: {str(e)}")
            return 0.5
    
    def _calculate_image_clarity(self, image: Image.Image) -> float:
        """计算图像清晰度
        
        Args:
            image: 待评估的图像
            
        Returns:
            清晰度分数（0-1）
        """
        try:
            # 转换为灰度图
            gray_image = image.convert('L')
            
            # 计算边缘强度
            width, height = gray_image.size
            edge_strength = 0
            
            for x in range(1, width-1):
                for y in range(1, height-1):
                    # 使用简单的边缘检测（Sobel算子简化版）
                    dx = abs(gray_image.getpixel((x+1, y)) - gray_image.getpixel((x-1, y)))
                    dy = abs(gray_image.getpixel((x, y+1)) - gray_image.getpixel((x, y-1)))
                    edge_strength += dx + dy
            
            # 归一化
            max_strength = (width-2) * (height-2) * 255 * 2
            clarity = edge_strength / max_strength
            return min(1, clarity)
        except:
            return 0.5
    
    def _calculate_color_richness(self, image: Image.Image) -> float:
        """计算图像色彩丰富度
        
        Args:
            image: 待评估的图像
            
        Returns:
            色彩丰富度分数（0-1）
        """
        try:
            # 确保图像模式为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 计算色彩直方图
            histogram = image.histogram()
            
            # 计算色彩分布的均匀性
            color_count = sum(1 for count in histogram if count > 0)
            max_colors = 256 * 3  # RGB各通道256级
            richness = color_count / max_colors
            
            # 计算色彩饱和度
            pixels = list(image.getdata())
            saturation_sum = 0
            for r, g, b in pixels:
                # 计算亮度
                brightness = (r + g + b) / 3
                if brightness > 0:
                    # 计算饱和度
                    max_rgb = max(r, g, b)
                    min_rgb = min(r, g, b)
                    saturation = (max_rgb - min_rgb) / max_rgb if max_rgb > 0 else 0
                    saturation_sum += saturation
            
            avg_saturation = saturation_sum / len(pixels) if pixels else 0
            
            # 综合评分
            return (richness * 0.5 + avg_saturation * 0.5)
        except:
            return 0.5
    
    def _get_rating(self, score: float) -> str:
        """根据分数获取评级
        
        Args:
            score: 综合评分
            
        Returns:
            评级字符串
        """
        if score >= 0.8:
            return "优秀"
        elif score >= 0.6:
            return "良好"
        elif score >= 0.4:
            return "一般"
        else:
            return "较差"
    
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
    
    def blend_styles(
        self, 
        image_bytes: bytes, 
        styles: List[Dict[str, Any]],
        width: int = 512,
        height: int = 512,
        style_strength: float = 0.7,
        evaluation: bool = False
    ) -> Dict[str, Any]:
        """混合多种风格
        
        Args:
            image_bytes: 原始图像字节数据
            styles: 风格列表，每个风格包含name和weight
            width: 输出图像宽度
            height: 输出图像高度
            style_strength: 整体风格强度
            evaluation: 是否返回评估结果
            
        Returns:
            包含风格混合后图像的字典
        """
        start_time = time.time()
        
        try:
            # 计算风格权重总和
            total_weight = sum(style.get("weight", 0) for style in styles)
            if total_weight == 0:
                total_weight = 1.0
            
            # 标准化权重
            normalized_styles = []
            for style in styles:
                normalized_style = style.copy()
                normalized_style["weight"] = style.get("weight", 1.0) / total_weight
                normalized_styles.append(normalized_style)
            
            # 构建详细的混合风格指令
            style_instruction = "混合风格："
            style_descriptions = []
            
            # 为每种风格获取详细描述
            for style in normalized_styles:
                style_name = style.get("name", "")
                weight = style.get("weight", 0)
                
                # 检索风格知识
                style_knowledge = self.rag_model.retrieve_style_knowledge(style_name, top_k=1)
                style_desc = style_name
                
                if style_knowledge:
                    style_desc = style_knowledge[0].get("description", style_name)
                
                style_descriptions.append(f"{style_desc}({weight:.2f})")
            
            style_instruction += "，".join(style_descriptions)
            style_instruction += f"。保持原始内容和构图，风格过渡自然，高质量，细节丰富。"
            
            # 计算混合风格的生成参数
            generation_params = self._get_blended_style_parameters(normalized_styles)
            
            # 首先使用LLaVA模型分析原始图像内容
            from models.llava_model import get_llava_model
            llava_model = get_llava_model()
            
            try:
                # 生成详细的图像描述
                image_description = llava_model.image_bytes_to_text(
                    image_bytes=image_bytes,
                    prompt="请详细描述这张图像的内容，包括人物、场景、物体、颜色、构图等主要元素，用中文描述。",
                    max_new_tokens=300,
                    temperature=0.2,
                    top_p=0.9
                )
                print(f"OK: 图像内容分析成功: {image_description[:50]}...")
            except Exception as desc_error:
                print(f"WARN: 图像内容分析失败: {str(desc_error)}")
                image_description = "一个人物形象"
            
            # 使用RAG模型增强风格提示词
            enhanced_prompt = self.rag_model.enhance_style_prompt(
                original_prompt=image_description,
                style_instruction=style_instruction
            )
            
            # 添加风格强度参数
            enhanced_prompt += f", 风格强度: {style_strength}, 保留原始内容和构图，风格过渡自然，高质量，细节丰富"
            
            # 使用SD模型生成图像
            from models.sd_model import get_sd_model
            sd_model = get_sd_model()
            
            # 生成图像
            image = sd_model.generate_image(
                prompt=enhanced_prompt,
                negative_prompt="低质量，模糊，扭曲，丑陋，改变原始内容，颜色失真，构图混乱，风格不统一，过渡生硬",
                width=width,
                height=height,
                num_inference_steps=generation_params["num_inference_steps"],
                guidance_scale=generation_params["guidance_scale"]
            )
            
            # 保存图像到img文件夹
            if not os.path.exists('img'):
                os.makedirs('img')
            
            # 生成唯一的文件名
            timestamp = int(time.time())
            filename = f"img/style_blended_{timestamp}.png"
            image.save(filename)
            print(f"OK: 风格混合图像已保存到: {filename}")
            
            end_time = time.time()
            print(f"OK: 风格混合成功，耗时: {end_time - start_time:.2f}秒")
            
            # 构建返回结果
            result = {
                "image": image,
                "filename": filename,
                "prompt": enhanced_prompt,
                "execution_time": end_time - start_time,
                "blended_styles": normalized_styles
            }
            
            # 如果需要评估，添加评估结果
            if evaluation:
                evaluation_result = self.evaluate_style_transfer(
                    original_image=Image.open(io.BytesIO(image_bytes)),
                    styled_image=image,
                    style_instruction=style_instruction
                )
                result["evaluation"] = evaluation_result
            
            return result
        except Exception as e:
            print(f"WARN: 风格混合失败: {str(e)}")
            
            # 最终降级方案：返回原始图像
            image = Image.open(io.BytesIO(image_bytes))
            image = image.resize((width, height))
            return {
                "image": image,
                "error": str(e)
            }
    
    def _get_blended_style_parameters(self, styles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算混合风格的生成参数
        
        Args:
            styles: 标准化后的风格列表
            
        Returns:
            混合后的生成参数字典
        """
        try:
            # 初始化参数
            total_weight = 0
            weighted_steps = 0
            weighted_guidance = 0
            
            # 计算加权平均参数
            for style in styles:
                style_name = style.get("name", "")
                weight = style.get("weight", 0)
                
                # 获取该风格的参数
                style_params = self._get_style_parameters(style_name)
                
                # 加权累加
                weighted_steps += style_params["num_inference_steps"] * weight
                weighted_guidance += style_params["guidance_scale"] * weight
                total_weight += weight
            
            if total_weight > 0:
                # 计算加权平均值
                num_inference_steps = int(round(weighted_steps / total_weight))
                guidance_scale = weighted_guidance / total_weight
                
                # 确保参数在合理范围内
                num_inference_steps = max(10, min(30, num_inference_steps))
                guidance_scale = max(5.0, min(9.0, guidance_scale))
                
                return {
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale
                }
            
            # 默认参数
            return {"num_inference_steps": 15, "guidance_scale": 7.0}
        except Exception as e:
            print(f"WARN: 计算混合风格参数失败: {str(e)}")
            return {"num_inference_steps": 15, "guidance_scale": 7.0}

    def batch_style_transfer(
        self, 
        batch_items: List[Dict[str, Any]],
        max_workers: int = 4
    ) -> List[Dict[str, Any]]:
        """批量执行风格迁移
        
        Args:
            batch_items: 批处理项列表，每个项包含以下字段：
                - image_bytes: 原始图像字节数据
                - style_instruction: 风格指令
                - width: 输出图像宽度（可选，默认512）
                - height: 输出图像高度（可选，默认512）
                - style_reference: 风格参考图像（可选）
                - style_strength: 风格强度（可选，默认0.7）
                - evaluation: 是否返回评估结果（可选，默认False）
            max_workers: 最大工作线程数
            
        Returns:
            批处理结果列表，每个项包含风格迁移结果
        """
        import concurrent.futures
        
        start_time = time.time()
        results = []
        
        # 定义处理单个项目的函数
        def process_item(item):
            try:
                # 提取参数
                image_bytes = item.get("image_bytes")
                style_instruction = item.get("style_instruction")
                width = item.get("width", 512)
                height = item.get("height", 512)
                style_reference = item.get("style_reference")
                style_strength = item.get("style_strength", 0.7)
                evaluation = item.get("evaluation", False)
                
                # 执行风格迁移
                result = self.style_transfer(
                    image_bytes=image_bytes,
                    style_instruction=style_instruction,
                    width=width,
                    height=height,
                    style_reference=style_reference,
                    style_strength=style_strength,
                    evaluation=evaluation
                )
                
                # 添加原始请求信息
                result["original_item"] = {
                    "style_instruction": style_instruction,
                    "width": width,
                    "height": height,
                    "style_strength": style_strength
                }
                
                return result
            except Exception as e:
                print(f"ERROR: 批处理项失败: {str(e)}")
                return {
                    "error": str(e),
                    "original_item": item
                }
        
        # 使用线程池并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_item = {executor.submit(process_item, item): item for item in batch_items}
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"ERROR: 批处理任务失败: {str(e)}")
                    results.append({
                        "error": str(e),
                        "original_item": item
                    })
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"OK: 批处理完成，共处理 {len(batch_items)} 项，耗时: {total_time:.2f}秒")
        
        return results

# 全局模型实例（单例模式）
qwen_image_edit_instance = None

def get_qwen_image_edit_model() -> QwenImageEditModel:
    """获取Qwen-Image-Edit模型实例（单例模式）
    
    Returns:
        QwenImageEditModel实例
    """
    global qwen_image_edit_instance
    if qwen_image_edit_instance is None:
        qwen_image_edit_instance = QwenImageEditModel()
    return qwen_image_edit_instance