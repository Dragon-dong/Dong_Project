import torch
from transformers import LlavaForConditionalGeneration, AutoProcessor
from PIL import Image
import io
import base64
import os
import requests
import json
from typing import Optional

# 使用requests库调用阿里云百炼API，绕过openai库的httpx版本依赖问题
print("OK: 使用requests库调用阿里云百炼API")
openai_available = False  # 不再使用openai库

class LLaVAModel:
    """LLaVA模型封装，用于图生文功能"""
    
    def __init__(self, model_id: str = "llava-hf/llava-1.6-vicuna-7b-hf"):
        """初始化LLaVA模型
        
        Args:
            model_id: 模型ID或本地路径
        """
        self.model_id = model_id
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
        # 初始化阿里云百炼API配置
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            # 使用提供的API Key
            self.api_key = "sk-a2f939f05191490184744855395f348c"
            print("⚠️  未设置环境变量DASHSCOPE_API_KEY，使用默认API Key")
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        print("OK: 阿里云百炼API配置初始化成功")
    

    
    def load_model(self):
        """加载LLaVA模型"""
        try:
            # 尝试快速加载模型（设置超时）
            import requests
            from requests.exceptions import Timeout
            
            # 首先检查网络连接
            try:
                response = requests.get("https://huggingface.co", timeout=3)
                print("OK: 网络连接正常")
            except Timeout:
                print("⚠️  网络连接超时，直接进入模拟模式")
                self.model_loaded = False
                return
            except Exception:
                print("⚠️  网络连接失败，直接进入模拟模式")
                self.model_loaded = False
                return
            
            # 加载处理器
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            
            # 加载模型
            self.model = LlavaForConditionalGeneration.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
            )
            
            # 优化模型
            if self.device == "cuda":
                self.model = self.model.to(self.device)
            else:
                self.model = self.model.to(self.device)
                
            print(f"OK: LLaVA模型加载成功，使用设备: {self.device}")
            self.model_loaded = True
        except Exception as e:
            print(f"ERROR: 加载LLaVA模型失败: {str(e)}")
            print("WARN: 启用模拟模式，将使用阿里云百炼API")
            self.model_loaded = False
    
    def image_to_text(
        self, 
        image: Image.Image, 
        prompt: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.9
    ) -> str:
        """图像生成文本描述
        
        Args:
            image: PIL图像对象
            prompt: 提示文本（可选）
            max_new_tokens: 生成的最大 tokens 数
            temperature: 生成温度
            top_p: 核采样参数
            
        Returns:
            生成的文本描述
        """
        if not hasattr(self, 'model_loaded') or not self.model_loaded:
            # 模型未加载，尝试使用阿里云百炼API
            if hasattr(self, 'api_key') and self.api_key:
                try:
                    print("使用阿里云百炼API进行图像分析")
                    # 将PIL图像转换为字节
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    image_bytes = img_byte_arr.getvalue()
                    
                    # 使用阿里云百炼API
                    return self._use_dashscope_api(image_bytes, prompt)
                except Exception as e:
                    print(f"ERROR: 使用阿里云百炼API失败: {str(e)}")
                    # API调用失败时返回占位文本
                    return "图像分析失败。由于API调用错误，无法提供图像描述。请检查网络连接或稍后重试。"
            else:
                # 无可用API，返回占位文本
                return "这是一个模拟的图像描述。由于模型加载失败且无可用API，无法提供真实的图像分析。在实际应用中，这里会返回基于图像内容的详细描述，包括物体、场景、颜色、动作等信息。"
        
        try:
            # 使用默认提示词如果没有提供
            if prompt is None:
                prompt = "Describe the image in detail."
            
            # 准备输入
            inputs = self.processor(
                images=image,
                text=prompt,
                return_tensors="pt"
            ).to(self.device)
            
            # 生成文本
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    use_cache=True
                )
            
            # 解码生成的文本
            generated_text = self.processor.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            return generated_text.strip()
        except Exception as e:
            print(f"ERROR: 图像生成文本失败: {str(e)}")
            # 生成失败时，尝试使用阿里云百炼API
            if hasattr(self, 'api_key') and self.api_key:
                try:
                    print("LLaVA模型失败，尝试使用阿里云百炼API")
                    # 将PIL图像转换为字节
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    image_bytes = img_byte_arr.getvalue()
                    
                    # 使用阿里云百炼API
                    return self._use_dashscope_api(image_bytes, prompt)
                except Exception as api_error:
                    print(f"ERROR: 使用阿里云百炼API失败: {str(api_error)}")
            
            # 所有方法都失败时返回占位文本
            return "图像分析失败。由于模型处理错误，无法提供图像描述。请检查图像格式是否正确，或稍后重试。"
    
    def _use_dashscope_api(
        self, 
        image_bytes: bytes, 
        prompt: Optional[str] = None
    ) -> str:
        """使用阿里云百炼API进行图像分析
        
        Args:
            image_bytes: 图像字节数据
            prompt: 提示文本（可选）
            
        Returns:
            生成的文本描述
        """
        try:
            # 将图像字节转换为base64编码
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # 使用默认提示词如果没有提供
            if prompt is None:
                prompt = "图中描绘的是什么景象?"
            
            # 构建请求数据
            payload = {
                "model": "qwen3-vl-plus",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            }
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            # 处理响应
            if response.status_code == 200:
                # 解析响应
                data = response.json()
                result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return result
            else:
                # 请求失败
                error_msg = f"API请求失败，状态码: {response.status_code}, 内容: {response.text}"
                print(f"✗ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            print(f"✗ 调用阿里云百炼API失败: {str(e)}")
            raise
    
    def image_bytes_to_text(
        self, 
        image_bytes: bytes, 
        prompt: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.9
    ) -> str:
        """从图像字节生成文本描述
        
        Args:
            image_bytes: 图像字节数据
            prompt: 提示文本（可选）
            max_new_tokens: 生成的最大 tokens 数
            temperature: 生成温度
            top_p: 核采样参数
            
        Returns:
            生成的文本描述
        """
        try:
            # 从字节创建PIL图像
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")
            
            # 调用图像生成文本方法
            return self.image_to_text(
                image=image,
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )
        except Exception as e:
            print(f"ERROR: 从图像字节生成文本失败: {str(e)}")
            # 生成失败时尝试直接使用阿里云百炼API
            if hasattr(self, 'api_key') and self.api_key:
                try:
                    print("尝试直接使用阿里云百炼API")
                    return self._use_dashscope_api(image_bytes, prompt)
                except Exception as api_error:
                    print(f"ERROR: 使用阿里云百炼API失败: {str(api_error)}")
            
            # 所有方法都失败时返回占位文本
            return "图像分析失败。由于模型处理错误，无法提供图像描述。请检查图像格式是否正确，或稍后重试。"

# 全局模型实例（单例模式）
llava_model_instance = None

def get_llava_model() -> LLaVAModel:
    """获取LLaVA模型实例（单例模式）
    
    Returns:
        LLaVAModel实例
    """
    global llava_model_instance
    if llava_model_instance is None:
        llava_model_instance = LLaVAModel()
    return llava_model_instance
