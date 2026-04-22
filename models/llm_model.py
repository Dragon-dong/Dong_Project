"""
LLM模型封装，用于文本生成和动态叙事生成
使用阿里云百炼API作为后端
"""

import os
import requests
import json
from typing import Optional, List, Dict


class LLMModel:
    """LLM模型封装，用于文本生成和动态叙事生成"""
    
    def __init__(self, model_settings=None):
        """初始化LLM模型
        
        Args:
            model_settings: 模型设置，包含modelType、localPaths、apiConfig等
        """
        if model_settings and model_settings.modelType == "custom-api" and model_settings.apiConfig:
            # 使用自定义API配置
            api_config = model_settings.apiConfig
            self.api_key = api_config.get("key")
            self.api_url = api_config.get("baseUrl", "https://api.openai.com/v1/chat/completions")
            self.model = api_config.get("provider", "openai")
            print(f"LLM模型初始化成功，使用自定义API: {self.model}")
        else:
            # 初始化阿里云百炼API配置
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
            if not self.api_key:
                # 使用提供的API Key
                self.api_key = "sk-a2f939f05191490184744855395f348c"
                print("未设置环境变量DASHSCOPE_API_KEY，使用默认API Key")
            self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
            self.model = "qwen3-vl-plus"
            print("LLM模型初始化成功，使用阿里云百炼API")
    
    def generate_text(
        self, 
        prompt: str, 
        model: str = "qwen3-vl-plus",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """生成文本
        
        Args:
            prompt: 提示文本
            model: 模型名称
            max_tokens: 最大生成tokens数
            temperature: 生成温度
            top_p: 核采样参数
            
        Returns:
            生成的文本
        """
        try:
            # 构建请求数据
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
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
                print(f"{error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            print(f"调用阿里云百炼API失败: {str(e)}")
            raise
    
    def generate_story(
        self, 
        keywords: str, 
        story_style: str = "fantasy",
        story_length: str = "medium"
    ) -> List[Dict[str, str]]:
        """生成动态叙事故事（旧格式）
        
        Args:
            keywords: 关键词，用逗号分隔
            story_style: 故事风格
            story_length: 故事长度
            
        Returns:
            故事场景列表，每个场景包含caption（文案）和enhanced_prompt（增强的图像生成提示词）
        """
        try:
            # 根据故事长度确定场景数量
            if story_length == "short":
                scene_count = 3
            elif story_length == "medium":
                scene_count = 4
            else:  # long
                scene_count = 5
            
            # 构建故事生成提示词
            prompt = f"请根据以下关键词生成一个{story_style}风格的故事，包含{scene_count}个连续的场景：\n"
            prompt += f"关键词：{keywords}\n"
            prompt += f"风格：{story_style}\n"
            prompt += f"长度：{story_length}\n"
            prompt += "\n要求：\n"
            prompt += f"1. 生成{scene_count}个清晰的场景，每个场景描述一个具体的画面\n"
            prompt += "2. 每个场景以'场景X：'开头，其中X是场景序号\n"
            prompt += "3. 场景之间要有逻辑连贯性，形成完整的故事\n"
            prompt += "4. 每个场景描述要详细，包含人物、环境、动作等元素\n"
            prompt += "5. 每个场景必须自然融入所有关键词\n"
            prompt += "6. 语言要生动形象，符合所选风格\n"
            prompt += "7. 只返回故事内容，不要添加其他说明"
            
            print(f"生成{story_style}风格故事，关键词: {keywords}")
            
            # 生成故事
            story_content = self.generate_text(prompt, max_tokens=2000)
            
            # 解析故事场景
            scenes = self._parse_story_scenes(story_content, scene_count, story_style)
            
            # 为每个场景生成增强的图像生成提示词
            for i, scene in enumerate(scenes):
                caption = scene.get("caption", "")
                # 生成增强的图像生成提示词
                enhanced_prompt = self._generate_enhanced_image_prompt(caption, keywords, story_style)
                scene["enhanced_prompt"] = enhanced_prompt
            
            return scenes
        except Exception as e:
            print(f"生成故事失败: {str(e)}")
            # 返回默认故事场景
            default_scenes = self._get_default_story_scenes(keywords, story_style)
            # 为默认场景生成增强的图像生成提示词
            for i, scene in enumerate(default_scenes):
                caption = scene.get("caption", "")
                enhanced_prompt = self._generate_enhanced_image_prompt(caption, keywords, story_style)
                scene["enhanced_prompt"] = enhanced_prompt
            return default_scenes
    
    def generate_story_from_scenes(
        self, 
        scene_keywords: List[str], 
        story_style: str = "fantasy",
        story_length: str = "medium"
    ) -> List[Dict[str, str]]:
        """根据场景关键词列表生成动态叙事故事（新格式）
        
        Args:
            scene_keywords: 场景关键词列表，每个元素对应一个场景的关键词
            story_style: 故事风格
            story_length: 故事长度
            
        Returns:
            故事场景列表，每个场景包含caption（文案）和enhanced_prompt（增强的图像生成提示词）
        """
        try:
            # 场景数量由scene_keywords的长度决定
            scene_count = len(scene_keywords)
            
            # 构建故事生成提示词
            prompt = f"请根据以下场景关键词列表生成一个{story_style}风格的故事，包含{scene_count}个连续的场景：\n"
            for i, keywords in enumerate(scene_keywords, 1):
                prompt += f"场景{i}关键词：{keywords}\n"
            prompt += f"风格：{story_style}\n"
            prompt += f"长度：{story_length}\n"
            prompt += "\n要求：\n"
            prompt += f"1. 生成{scene_count}个清晰的场景，每个场景描述一个具体的画面\n"
            prompt += "2. 每个场景以'场景X：'开头，其中X是场景序号\n"
            prompt += "3. 场景之间要有逻辑连贯性，形成完整的故事\n"
            prompt += "4. 每个场景描述要详细，包含人物、环境、动作等元素\n"
            prompt += "5. 每个场景必须自然融入对应场景的关键词\n"
            prompt += "6. 语言要生动形象，符合所选风格\n"
            prompt += "7. 只返回故事内容，不要添加其他说明"
            
            print(f"生成{story_style}风格故事，场景数量: {scene_count}")
            
            # 生成故事
            story_content = self.generate_text(prompt, max_tokens=3000)
            
            # 解析故事场景
            scenes = self._parse_story_scenes(story_content, scene_count, story_style)
            
            # 为每个场景生成增强的图像生成提示词
            for i, scene in enumerate(scenes):
                caption = scene.get("caption", "")
                # 使用对应场景的关键词生成增强提示词
                scene_keyword = scene_keywords[i] if i < len(scene_keywords) else ""
                # 生成增强的图像生成提示词
                enhanced_prompt = self._generate_enhanced_image_prompt(caption, scene_keyword, story_style)
                scene["enhanced_prompt"] = enhanced_prompt
            
            return scenes
        except Exception as e:
            print(f"生成故事失败: {str(e)}")
            # 返回默认故事场景
            default_scenes = []
            for i, keywords in enumerate(scene_keywords):
                default_scenes.append({
                    "caption": f"这是故事的第{i+1}个场景，描述了一个{story_style}风格的画面。{keywords.split(',')[0]}是这个场景的核心元素。",
                    "image": f"https://picsum.photos/seed/story{i+1}/512/512"  # 添加占位图像
                })
            # 为默认场景生成增强的图像生成提示词
            for i, scene in enumerate(default_scenes):
                caption = scene.get("caption", "")
                scene_keyword = scene_keywords[i] if i < len(scene_keywords) else ""
                enhanced_prompt = self._generate_enhanced_image_prompt(caption, scene_keyword, story_style)
                scene["enhanced_prompt"] = enhanced_prompt
            return default_scenes
    
    def generate_coherent_story(
        self, 
        scene_descriptions: List[str],
        story_style: str = "fantasy"
    ) -> str:
        """将多个场景描述整合为一个连贯的故事
        
        Args:
            scene_descriptions: 场景描述列表
            story_style: 故事风格
            
        Returns:
            连贯的故事内容
        """
        try:
            # 构建提示词
            prompt = f"请将以下{len(scene_descriptions)}个场景描述整合为一个连贯的{story_style}风格故事：\n\n"
            
            for i, description in enumerate(scene_descriptions, 1):
                prompt += f"场景{i}：{description}\n\n"
            
            prompt += "\n要求：\n"
            prompt += "1. 保持每个场景的主要内容\n"
            prompt += "2. 添加场景之间的过渡和连接，使故事连贯流畅\n"
            prompt += "3. 保持故事的整体风格一致\n"
            prompt += "4. 语言生动形象，符合所选风格\n"
            prompt += "5. 只返回完整的故事，不要添加其他说明"
            
            print(f"生成连贯的{story_style}风格故事")
            
            # 生成连贯的故事
            coherent_story = self.generate_text(prompt, max_tokens=3000)
            
            return coherent_story
        except Exception as e:
            print(f"生成连贯故事失败: {str(e)}")
            # 返回简单的场景连接
            return "\n\n".join(scene_descriptions)
    
    def _parse_story_scenes(self, story_content: str, scene_count: int, story_style: str) -> List[Dict[str, str]]:
        """解析故事场景
        
        Args:
            story_content: 生成的故事内容
            scene_count: 期望的场景数量
            story_style: 故事风格
            
        Returns:
            故事场景列表
        """
        scenes = []
        
        # 按场景分割故事
        lines = story_content.strip().split('\n')
        current_scene = None
        current_caption = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('场景') and ':' in line:
                # 保存当前场景
                if current_scene is not None:
                    scenes.append({
                        "caption": ' '.join(current_caption).strip()
                    })
                # 开始新场景
                current_scene = line.split(':')[0]
                current_caption = [line.split(':', 1)[1].strip()]
            elif current_scene:
                # 累加场景内容
                current_caption.append(line)
        
        # 保存最后一个场景
        if current_scene is not None:
            scenes.append({
                "caption": ' '.join(current_caption).strip()
            })
        
        # 确保场景数量正确
        if len(scenes) < scene_count:
            # 添加默认场景
            for i in range(len(scenes), scene_count):
                scenes.append({
                    "caption": f"这是故事的第{i+1}个场景，描述了一个{story_style}风格的画面。"
                })
        elif len(scenes) > scene_count:
            # 截取前scene_count个场景
            scenes = scenes[:scene_count]
        
        return scenes
    
    def _generate_enhanced_image_prompt(self, caption: str, keywords: str, story_style: str) -> str:
        """生成增强的图像生成提示词
        
        Args:
            caption: 场景描述
            keywords: 关键词
            story_style: 故事风格
            
        Returns:
            增强的图像生成提示词
        """
        try:
            # 构建提示词
            prompt = f"请根据以下场景描述和关键词，生成一个详细的图像生成提示词：\n\n"
            prompt += f"场景描述：{caption}\n"
            prompt += f"关键词：{keywords}\n"
            prompt += f"故事风格：{story_style}\n\n"
            prompt += "要求：\n"
            prompt += "1. 包含场景中的主要元素和细节\n"
            prompt += "2. 融入所有关键词\n"
            prompt += "3. 体现故事风格\n"
            prompt += "4. 描述画面的构图、光线、色彩等视觉元素\n"
            prompt += "5. 语言简洁明了，适合作为图像生成的提示词\n"
            prompt += "6. 只返回提示词，不要添加其他说明"
            
            # 生成增强的提示词
            enhanced_prompt = self.generate_text(prompt, max_tokens=500)
            return enhanced_prompt.strip()
        except Exception as e:
            print(f"生成增强提示词失败: {str(e)}")
            # 返回基础提示词
            return f"{caption}, {keywords}, {story_style} style, detailed, vivid, high quality"
    
    def _get_default_story_scenes(self, keywords: str, story_style: str) -> List[Dict[str, str]]:
        """获取默认故事场景
        
        Args:
            keywords: 关键词
            story_style: 故事风格
            
        Returns:
            默认故事场景列表
        """
        default_scenes = [
            {
                "caption": f"在一个{story_style}风格的世界里，故事开始于一个神秘的地方。{keywords.split(',')[0]}是这个故事的核心元素。"
            },
            {
                "caption": f"主角发现了一个关于{keywords.split(',')[0]}的秘密，决定展开一段冒险。"
            },
            {
                "caption": f"在旅途中，主角遇到了各种挑战和机遇，逐渐成长。"
            },
            {
                "caption": f"最终，主角成功解决了问题，获得了宝贵的经验和友谊。"
            }
        ]
        return default_scenes


# 全局模型实例（单例模式）
llm_model_instance = None


def get_llm_model(model_settings=None) -> LLMModel:
    """获取LLM模型实例（单例模式）
    
    Args:
        model_settings: 模型设置，包含modelType、localPaths、apiConfig等
    
    Returns:
        LLMModel实例
    """
    global llm_model_instance
    if model_settings:
        # 根据模型设置创建新的实例
        if model_settings.modelType == "custom-api" and model_settings.apiConfig:
            # 使用自定义API配置
            return LLMModel(model_settings=model_settings)
    
    # 默认使用全局实例
    if llm_model_instance is None:
        llm_model_instance = LLMModel()
    return llm_model_instance
