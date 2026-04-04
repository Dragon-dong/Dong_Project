from typing import List, Dict, Any, Optional
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 尝试导入dashscope库
try:
    from dashscope import Assistants, Messages, Runs, Threads
    DASHSCOPE_AVAILABLE = True
    print("OK: dashscope库导入成功")
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("WARN: dashscope库未安装，将使用本地RAG模式")

class RAGModel:
    """RAG架构风格知识检索模型
    
    支持两种检索模式：
    1. 阿里云百炼API模式：使用阿里云百炼的RAG功能，提供更强大的知识检索能力
    2. 本地RAG模式：使用TF-IDF和余弦相似度进行本地知识库检索
    
    当阿里云百炼API不可用时，会自动回退到本地RAG模式，确保系统稳定性。
    """

    
    def __init__(self, knowledge_base_path: Optional[str] = None, use_dashscope: bool = True):
        """初始化RAG模型
        
        Args:
            knowledge_base_path: 知识库路径（可选）
            use_dashscope: 是否使用阿里云百炼API
        """
        # 加载本地知识库
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self._build_vector_index()
        
        # 初始化阿里云百炼API
        self.use_dashscope = use_dashscope and DASHSCOPE_AVAILABLE
        self.dashscope_assistant = None
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            # 使用提供的API Key
            self.api_key = "sk-a2f939f05191490184744855395f348c"
            print("WARN: 未设置环境变量DASHSCOPE_API_KEY，使用默认API Key")
        
        if self.use_dashscope:
            try:
                # 设置API密钥
                os.environ["DASHSCOPE_API_KEY"] = self.api_key
                # 创建assistant
                self._create_dashscope_assistant()
                print("OK: 阿里云百炼API初始化成功")
            except Exception as e:
                print(f"WARN: 初始化阿里云百炼API失败: {str(e)}")
                self.use_dashscope = False
        
        print("OK: RAG架构风格知识检索模型初始化成功")
    
    def _load_knowledge_base(self, knowledge_base_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """加载风格知识库
        
        Args:
            knowledge_base_path: 知识库路径
            
        Returns:
            风格知识库列表
        """
        # 如果提供了知识库路径，尝试从文件加载
        if knowledge_base_path and os.path.exists(knowledge_base_path):
            try:
                with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"WARN: 从文件加载知识库失败: {str(e)}，使用默认知识库")
        
        # 默认风格知识库
        default_knowledge_base = [
            {
                "id": 1,
                "style_name": "写实风格",
                "style_en": "Realism",
                "description": "写实风格强调对现实世界的真实再现，注重细节和准确性，追求与实际物体的相似性。",
                "features": ["细节丰富", "色彩真实", "透视准确", "光影自然"],
                "examples": ["人物肖像", "风景写生", "静物画"],
                "prompt_keywords": ["realistic", "detailed", "accurate", "natural lighting", "lifelike"]
            },
            {
                "id": 2,
                "style_name": "卡通风格",
                "style_en": "Cartoon",
                "description": "卡通风格具有夸张的表现手法，简洁的线条，鲜明的色彩，常用于动画和漫画。",
                "features": ["线条简洁", "色彩鲜明", "形象夸张", "表情丰富"],
                "examples": ["动漫人物", "卡通动物", "漫画场景"],
                "prompt_keywords": ["cartoon", "anime", "stylized", "colorful", "exaggerated features"]
            },
            {
                "id": 3,
                "style_name": "油画风格",
                "style_en": "Oil Painting",
                "description": "油画风格具有丰富的色彩层次和质感，笔触明显，色彩浓郁，具有厚重感。",
                "features": ["色彩浓郁", "笔触明显", "层次丰富", "质感强烈"],
                "examples": ["古典油画", "印象派油画", "现代油画"],
                "prompt_keywords": ["oil painting", "rich colors", "visible brushstrokes", "textured", "vibrant"]
            },
            {
                "id": 4,
                "style_name": "水彩风格",
                "style_en": "Watercolor",
                "description": "水彩风格色彩透明，笔触轻盈，具有自然的晕染效果，给人清新淡雅的感觉。",
                "features": ["色彩透明", "笔触轻盈", "自然晕染", "清新淡雅"],
                "examples": ["风景画", "花卉画", "静物画"],
                "prompt_keywords": ["watercolor", "transparent", "light brushstrokes", "soft edges", "delicate"]
            },
            {
                "id": 5,
                "style_name": "赛博朋克风格",
                "style_en": "Cyberpunk",
                "description": "赛博朋克风格结合了高科技和低生活的元素，具有霓虹灯效果，未来感强烈，常有故障艺术效果。",
                "features": ["霓虹灯效果", "未来感", "故障艺术", "高对比度"],
                "examples": ["未来城市", "科幻场景", "赛博朋克人物"],
                "prompt_keywords": ["cyberpunk", "neon lights", "futuristic", "glitch art", "high contrast"]
            },
            {
                "id": 6,
                "style_name": "中国风",
                "style_en": "Chinese Style",
                "description": "中国风融合了中国传统艺术元素，如水墨、工笔、国画等，具有东方美学特色。",
                "features": ["水墨效果", "工笔细致", "留白", "东方美学"],
                "examples": ["山水画", "花鸟画", "人物画"],
                "prompt_keywords": ["Chinese style", "ink painting", "traditional", "oriental aesthetics", "water and ink"]
            },
            {
                "id": 7,
                "style_name": "梵高风格",
                "style_en": "Van Gogh Style",
                "description": "梵高风格以强烈的色彩、扭曲的线条和厚重的笔触为特点，具有强烈的情感表达。",
                "features": ["色彩强烈", "线条扭曲", "笔触厚重", "情感表达"],
                "examples": ["星空", "向日葵", "自画像"],
                "prompt_keywords": ["Van Gogh style", "bold colors", "twisted lines", "thick brushstrokes", "expressive"]
            },
            {
                "id": 8,
                "style_name": "宫崎骏风格",
                "style_en": "Hayao Miyazaki Style",
                "description": "宫崎骏风格以细腻的画面、丰富的想象力、温暖的色调和人文关怀为特点。",
                "features": ["画面细腻", "想象力丰富", "色调温暖", "人文关怀"],
                "examples": ["龙猫", "千与千寻", "哈尔的移动城堡"],
                "prompt_keywords": ["Hayao Miyazaki style", "detailed", "imaginative", "warm colors", "whimsical"]
            },
            {
                "id": 9,
                "style_name": "蒸汽朋克风格",
                "style_en": "Steampunk",
                "description": "蒸汽朋克风格结合了维多利亚时代的美学和蒸汽动力技术，具有复古未来主义特色。",
                "features": ["蒸汽动力", "维多利亚时代", "机械元素", "复古未来"],
                "examples": ["蒸汽火车", "机械装置", "复古城市"],
                "prompt_keywords": ["steampunk", "Victorian era", "steam-powered", "mechanical", "retro-futuristic"]
            },
            {
                "id": 10,
                "style_name": "水墨风格",
                "style_en": "Ink Wash",
                "description": "水墨风格是中国传统绘画的一种，以水和墨为主要媒介，注重意境和笔墨韵味。",
                "features": ["黑白灰层次", "笔墨韵味", "意境深远", "留白"],
                "examples": ["山水画", "花鸟画", "人物画"],
                "prompt_keywords": ["ink wash", "black and white", "traditional Chinese", "atmospheric", "minimalist"]
            }
        ]
        
        return default_knowledge_base
    
    def _build_vector_index(self):
        """构建向量索引"""
        # 为知识库中的每个风格创建文本表示
        self.style_texts = []
        for style in self.knowledge_base:
            # 组合风格的各种信息为文本
            style_text = f"{style['style_name']} {style['style_en']} {style['description']} {' '.join(style['features'])} {' '.join(style['examples'])} {' '.join(style['prompt_keywords'])}"
            self.style_texts.append(style_text)
        
        # 构建TF-IDF向量索引
        self.tfidf_matrix = self.vectorizer.fit_transform(self.style_texts)
    
    def _create_dashscope_assistant(self):
        """创建阿里云百炼assistant"""
        try:
            # 创建assistant
            assistant = Assistants.create(
                # 使用qwen-max模型
                model='qwen-max',
                name='style_rag_assistant',
                description='一个用于风格知识检索的智能助手，能够根据用户的风格指令提供相关的风格知识。',
                instructions='你是一个风格知识检索助手，请根据用户的风格指令，提供相关的风格知识和提示词建议。',
                tools=[
                    {
                        "type": "rag",
                        "prompt_ra": {
                            "pipeline_id": ["fqcioazfej"],  # 知识库id
                            "multiknowledge_rerank_top_n": 10,  # 多个知识库总共召回的片段数
                            "rerank_top_n": 5,  # 单个知识库召回的片段数
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query_word": {
                                        "type": "str",
                                        "value": "${document1}"
                                    }
                                }
                            }
                        }
                    }
                ]
            )
            self.dashscope_assistant = assistant
            print(f"OK: 阿里云百炼assistant创建成功，ID: {assistant.id}")
        except Exception as e:
            print(f"WARN: 创建阿里云百炼assistant失败: {str(e)}")
            raise
    
    def _retrieve_style_knowledge_dashscope(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """使用阿里云百炼API检索风格知识
        
        Args:
            query: 查询文本
            top_k: 返回的top-k结果数
            
        Returns:
            检索到的风格知识列表
        """
        try:
            if not self.dashscope_assistant:
                print("WARN: 阿里云百炼assistant未初始化")
                return []
            
            # 创建thread
            thread = Threads.create()
            
            # 创建message
            message = Messages.create(thread.id, content=query)
            
            # 创建run
            run = Runs.create(thread.id, assistant_id=self.dashscope_assistant.id)
            
            # 等待run完成
            run_status = Runs.wait(run.id, thread_id=thread.id)
            
            # 获取thread messages
            msgs = Messages.list(thread.id)
            
            # 提取结果
            results = []
            for message in msgs['data'][::-1]:
                if message['role'] == 'assistant':
                    content = message['content'][0]['text']['value']
                    # 构建风格知识结果
                    style_info = {
                        'id': len(results) + 1,
                        'style_name': f"风格_{len(results) + 1}",
                        'style_en': f"Style_{len(results) + 1}",
                        'description': content,
                        'features': [],
                        'examples': [],
                        'prompt_keywords': [],
                        'similarity': 1.0
                    }
                    results.append(style_info)
                    if len(results) >= top_k:
                        break
            
            print(f"OK: 阿里云百炼API风格知识检索成功，找到 {len(results)} 个相关风格")
            return results
            
        except Exception as e:
            print(f"WARN: 阿里云百炼API风格知识检索出错: {str(e)}")
            return []
    
    def _retrieve_style_knowledge_local(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """使用本地RAG检索风格知识
        
        Args:
            query: 查询文本
            top_k: 返回的top-k结果数
            
        Returns:
            检索到的风格知识列表
        """
        try:
            # 将查询文本转换为向量
            query_vector = self.vectorizer.transform([query])
            
            # 计算余弦相似度
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # 获取top-k最相似的风格
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # 构建检索结果
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # 相似度阈值
                    style_info = self.knowledge_base[idx].copy()
                    style_info['similarity'] = float(similarities[idx])
                    results.append(style_info)
            
            print(f"OK: 本地RAG风格知识检索成功，找到 {len(results)} 个相关风格")
            return results
            
        except Exception as e:
            print(f"WARN: 本地RAG风格知识检索出错: {str(e)}")
            return []
    
    def retrieve_style_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """检索风格知识
        
        Args:
            query: 查询文本
            top_k: 返回的top-k结果数
            
        Returns:
            检索到的风格知识列表
        """
        # 优先使用阿里云百炼API
        if self.use_dashscope:
            results = self._retrieve_style_knowledge_dashscope(query, top_k)
            if results:
                return results
        
        # 回退到本地RAG
        return self._retrieve_style_knowledge_local(query, top_k)
    
    def _enhance_style_prompt_dashscope(self, original_prompt: str, style_instruction: str) -> str:
        """使用阿里云百炼API增强风格提示词
        
        Args:
            original_prompt: 原始提示词
            style_instruction: 风格指令
            
        Returns:
            增强后的提示词
        """
        try:
            if not self.dashscope_assistant:
                print("WARN: 阿里云百炼assistant未初始化")
                return f"{original_prompt}, {style_instruction}"
            
            # 构建详细的提示词
            prompt = f"请根据以下信息，为图像生成任务增强提示词：\n"
            prompt += f"原始提示词：{original_prompt}\n"
            prompt += f"风格指令：{style_instruction}\n"
            prompt += "\n要求：\n"
            prompt += "1. 保留原始提示词的核心内容\n"
            prompt += "2. 根据风格指令添加相关的风格描述和关键词\n"
            prompt += "3. 生成的提示词要具体、详细，适合用于图像生成\n"
            prompt += "4. 只返回增强后的提示词，不要添加其他说明"
            
            # 创建thread
            thread = Threads.create()
            
            # 创建message
            message = Messages.create(thread.id, content=prompt)
            
            # 创建run
            run = Runs.create(thread.id, assistant_id=self.dashscope_assistant.id)
            
            # 等待run完成
            run_status = Runs.wait(run.id, thread_id=thread.id)
            
            # 获取thread messages
            msgs = Messages.list(thread.id)
            
            # 提取结果
            enhanced_prompt = f"{original_prompt}, {style_instruction}"
            for message in msgs['data'][::-1]:
                if message['role'] == 'assistant':
                    content = message['content'][0]['text']['value'].strip()
                    if content:
                        enhanced_prompt = content
                    break
            
            print(f"OK: 阿里云百炼API风格提示词增强成功")
            print(f"原始提示词: {original_prompt}")
            print(f"增强后提示词: {enhanced_prompt}")
            
            return enhanced_prompt
            
        except Exception as e:
            print(f"WARN: 阿里云百炼API风格提示词增强出错: {str(e)}")
            return f"{original_prompt}, {style_instruction}"
    
    def _enhance_style_prompt_local(self, original_prompt: str, style_instruction: str) -> str:
        """使用本地RAG增强风格提示词
        
        Args:
            original_prompt: 原始提示词
            style_instruction: 风格指令
            
        Returns:
            增强后的提示词
        """
        # 检索相关风格知识
        style_knowledge = self._retrieve_style_knowledge_local(style_instruction, top_k=2)
        
        if not style_knowledge:
            # 如果没有检索到相关风格，返回原始提示词
            return f"{original_prompt}, {style_instruction}"
        
        # 构建增强的提示词
        enhanced_prompt = original_prompt
        
        # 添加风格信息
        for style in style_knowledge:
            # 添加风格名称
            enhanced_prompt += f", {style['style_name']} style"
            
            # 添加风格特征关键词
            if 'prompt_keywords' in style:
                enhanced_prompt += f", {' '.join(style['prompt_keywords'][:3])}"
        
        # 添加原始风格指令
        enhanced_prompt += f", {style_instruction}"
        
        print(f"OK: 本地RAG风格提示词增强成功")
        print(f"原始提示词: {original_prompt}")
        print(f"增强后提示词: {enhanced_prompt}")
        
        return enhanced_prompt
    
    def enhance_style_prompt(self, original_prompt: str, style_instruction: str) -> str:
        """增强风格提示词
        
        Args:
            original_prompt: 原始提示词
            style_instruction: 风格指令
            
        Returns:
            增强后的提示词
        """
        # 优先使用阿里云百炼API
        if self.use_dashscope:
            enhanced_prompt = self._enhance_style_prompt_dashscope(original_prompt, style_instruction)
            if enhanced_prompt != f"{original_prompt}, {style_instruction}":
                return enhanced_prompt
        
        # 回退到本地RAG
        return self._enhance_style_prompt_local(original_prompt, style_instruction)
    
    def get_style_info(self, style_name: str) -> Optional[Dict[str, Any]]:
        """获取特定风格的详细信息
        
        Args:
            style_name: 风格名称
            
        Returns:
            风格详细信息
        """
        for style in self.knowledge_base:
            if style['style_name'] == style_name or style['style_en'].lower() == style_name.lower():
                return style
        return None
    
    def add_style_to_knowledge_base(self, style_info: Dict[str, Any]):
        """向知识库添加新风格
        
        Args:
            style_info: 新风格信息
        """
        # 为新风格生成ID
        new_id = max([style['id'] for style in self.knowledge_base]) + 1 if self.knowledge_base else 1
        style_info['id'] = new_id
        
        # 添加到知识库
        self.knowledge_base.append(style_info)
        
        # 重新构建向量索引
        self._build_vector_index()
        
        print(f"OK: 新风格 '{style_info.get('style_name', 'Unknown')}' 添加到知识库成功")
    
    def save_knowledge_base(self, output_path: str):
        """保存知识库到文件
        
        Args:
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print(f"OK: 知识库保存成功: {output_path}")
        except Exception as e:
            print(f"WARN: 知识库保存失败: {str(e)}")

# 全局模型实例（单例模式）
rag_model_instance = None

def get_rag_model(knowledge_base_path: Optional[str] = None, use_dashscope: bool = True) -> RAGModel:
    """获取RAG模型实例（单例模式）
    
    Args:
        knowledge_base_path: 知识库路径（可选）
        use_dashscope: 是否使用阿里云百炼API
        
    Returns:
        RAGModel实例
    """
    global rag_model_instance
    if rag_model_instance is None:
        rag_model_instance = RAGModel(knowledge_base_path, use_dashscope)
    return rag_model_instance
