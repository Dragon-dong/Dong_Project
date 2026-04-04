import requests
import json

# 测试多语言文化适配API
url = "http://localhost:8000/api/multilingual-adaptation"

# 测试用例
test_cases = [
    {
        "content": "这是一个测试文本，用于验证多语言文化适配功能",
        "target_lang": "en",
        "description": "中文到英文"
    },
    {
        "content": "This is a test text to verify multilingual cultural adaptation",
        "target_lang": "zh",
        "description": "英文到中文"
    },
    {
        "content": "これは多言語文化適応機能を検証するためのテストテキストです",
        "target_lang": "zh",
        "description": "日文到中文"
    },
    {
        "content": "这是一个测试文本，不指定目标语言",
        "target_lang": None,
        "description": "自动检测语言"
    }
]

for i, test_case in enumerate(test_cases):
    print(f"\n=== 测试用例 {i+1}: {test_case['description']} ===")
    print(f"测试文本: {test_case['content']}")
    print(f"目标语言: {test_case['target_lang']}")
    
    # 构建请求数据
    payload = {
        "content": test_case['content'],
        "target_lang": test_case['target_lang']
    }
    
    try:
        # 发送请求
        response = requests.post(url, json=payload, timeout=10)
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✓ 多语言文化适配API测试成功!")
            # 解析响应内容
            data = response.json()
            print(f"原始内容: {data['result']['original_content']}")
            print(f"适配后内容: {data['result']['adapted_content']}")
            print(f"目标语言: {data['result']['target_language']}")
            print(f"文化风格: {data['result']['cultural_context']['style']}")
        else:
            print("✗ 多语言文化适配API测试失败!")
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
