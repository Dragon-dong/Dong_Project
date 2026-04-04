from models.rag_model import get_rag_model

# 测试RAG模型
print("=== 测试RAG架构风格知识检索模型 ===")

# 获取RAG模型实例
rag_model = get_rag_model()

# 测试1: 风格知识检索
print("\n=== 测试1: 风格知识检索 ===")
query = "梵高星空风格"
results = rag_model.retrieve_style_knowledge(query, top_k=3)
print(f"查询: {query}")
print(f"找到 {len(results)} 个相关风格:")
for i, result in enumerate(results):
    print(f"{i+1}. {result['style_name']} (相似度: {result['similarity']:.4f})")
    print(f"   描述: {result['description']}")
    print(f"   特征: {', '.join(result['features'])}")

# 测试2: 提示词增强
print("\n=== 测试2: 提示词增强 ===")
original_prompt = "一只可爱的猫在阳光下睡觉"
style_instruction = "梵高星空风格"
enhanced_prompt = rag_model.enhance_style_prompt(original_prompt, style_instruction)
print(f"原始提示词: {original_prompt}")
print(f"风格指令: {style_instruction}")
print(f"增强后提示词: {enhanced_prompt}")

# 测试3: 另一个风格的提示词增强
print("\n=== 测试3: 另一个风格的提示词增强 ===")
original_prompt = "一个未来城市的夜景"
style_instruction = "赛博朋克风格"
enhanced_prompt = rag_model.enhance_style_prompt(original_prompt, style_instruction)
print(f"原始提示词: {original_prompt}")
print(f"风格指令: {style_instruction}")
print(f"增强后提示词: {enhanced_prompt}")

# 测试4: 获取特定风格信息
print("\n=== 测试4: 获取特定风格信息 ===")
style_name = "中国风"
style_info = rag_model.get_style_info(style_name)
if style_info:
    print(f"风格名称: {style_info['style_name']} ({style_info['style_en']})")
    print(f"描述: {style_info['description']}")
    print(f"特征: {', '.join(style_info['features'])}")
    print(f"示例: {', '.join(style_info['examples'])}")
    print(f"提示词关键词: {', '.join(style_info['prompt_keywords'])}")
else:
    print(f"未找到风格: {style_name}")

print("\n=== RAG模型测试完成 ===")
