import requests
import json

# 测试动态叙事生成API
url = "http://localhost:8000/api/generate-story"

# 请求数据
payload = {
    "keywords": "冒险, 森林, 神秘生物",
    "story_style": "fantasy",
    "story_length": "medium"
}

print(f"测试动态叙事生成API: {url}")
print(f"请求数据: {json.dumps(payload, ensure_ascii=False)}")

try:
    # 发送请求，增加超时时间到60秒
    response = requests.post(url, json=payload, timeout=60)
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✓ 动态叙事生成API测试成功!")
        # 解析响应内容
        data = response.json()
        print(f"生成的故事场景数: {len(data.get('story_items', []))}")
    else:
        print("✗ 动态叙事生成API测试失败!")
        
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
