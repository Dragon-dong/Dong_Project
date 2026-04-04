#!/usr/bin/env python3
"""
测试优化后的RAG模型功能
"""

from models.rag_model import get_rag_model


def test_rag_model():
    """测试RAG模型功能"""
    print("\n=== 测试RAG模型功能 ===")
    
    # 初始化RAG模型（使用阿里云百炼API）
    print("\n1. 初始化RAG模型...")
    rag_model = get_rag_model(use_dashscope=True)
    
    # 测试风格知识检索
    print("\n2. 测试风格知识检索...")
    query = "中国风"
    results = rag_model.retrieve_style_knowledge(query, top_k=2)
    print(f"检索结果数量: {len(results)}")
    for i, result in enumerate(results):
        print(f"  结果{i+1}: {result['style_name']}")
        print(f"  描述: {result['description'][:100]}...")
    
    # 测试提示词增强
    print("\n3. 测试提示词增强...")
    original_prompt = "一只猫在花园里"
    style_instruction = "中国风，水墨画"
    enhanced_prompt = rag_model.enhance_style_prompt(original_prompt, style_instruction)
    print(f"原始提示词: {original_prompt}")
    print(f"风格指令: {style_instruction}")
    print(f"增强后提示词: {enhanced_prompt}")
    
    # 测试另一个风格
    print("\n4. 测试另一个风格...")
    original_prompt = "一个城市夜景"
    style_instruction = "赛博朋克"
    enhanced_prompt = rag_model.enhance_style_prompt(original_prompt, style_instruction)
    print(f"原始提示词: {original_prompt}")
    print(f"风格指令: {style_instruction}")
    print(f"增强后提示词: {enhanced_prompt}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_rag_model()
