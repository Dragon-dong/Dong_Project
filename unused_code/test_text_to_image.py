import requests
import json
import time

# 测试文生图API性能
url = "http://localhost:8000/api/text-to-image"

# 测试用例
test_cases = [
    {
        "prompt": "一只可爱的猫在阳光下睡觉",
        "style": "卡通风格",
        "description": "卡通风格猫"
    },
    {
        "prompt": "一个未来城市的夜景",
        "style": "赛博朋克风格",
        "description": "赛博朋克城市"
    },
    {
        "prompt": "山水风景画",
        "style": "中国风",
        "description": "中国风山水"
    }
]

print("=== 测试优化后的文生图API性能 ===")

for i, test_case in enumerate(test_cases):
    print(f"\n=== 测试用例 {i+1}: {test_case['description']} ===")
    print(f"提示词: {test_case['prompt']}")
    print(f"风格: {test_case['style']}")
    
    # 构建请求数据
    payload = {
        "prompt": test_case['prompt'],
        "style": test_case['style'],
        "resolution": "512x512"
    }
    
    # 测试生成时间
    start_time = time.time()
    
    try:
        # 发送请求
        response = requests.post(url, json=payload, timeout=30)
        
        # 计算生成时间
        end_time = time.time()
        generation_time = end_time - start_time
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        print(f"生成时间: {generation_time:.2f}秒")
        
        if response.status_code == 200:
            print("✓ 文生图API测试成功!")
            # 解析响应内容
            data = response.json()
            print(f"原始提示词: {data['prompt']}")
            print(f"增强后提示词: {data['enhanced_prompt']}")
        else:
            print("✗ 文生图API测试失败!")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        end_time = time.time()
        generation_time = end_time - start_time
        print(f"✗ 测试失败: {str(e)}")
        print(f"耗时: {generation_time:.2f}秒")

print("\n=== 测试完成 ===")
