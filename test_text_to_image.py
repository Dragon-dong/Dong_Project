import requests
import json

# 测试文生图API
url = "http://localhost:8000/api/text-to-image"

# 测试数据
data = {
    "prompt": "一只可爱的猫在阳光下睡觉",
    "style": "卡通风格",
    "resolution": "512x512"
}

print("测试文生图API...")
try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 解析响应
    if response.status_code == 200:
        result = response.json()
        print(f"生成状态: {result.get('status')}")
        print(f"是否有图像URL: {'image_url' in result}")
        if 'image_url' in result:
            print(f"图像URL长度: {len(result['image_url'])}")
    else:
        print("API调用失败")
except Exception as e:
    print(f"请求失败: {str(e)}")
