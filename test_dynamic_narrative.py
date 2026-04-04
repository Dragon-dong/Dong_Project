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
    # 发送请求，增加超时时间到120秒
    response = requests.post(url, json=payload, timeout=120)
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ 动态叙事生成API测试成功!")
        # 解析响应内容
        data = response.json()
        print(f"生成的故事场景数: {len(data.get('story_items', []))}")
        print(f"是否包含连贯故事: {'coherent_story' in data}")
        
        # 打印每个场景的信息
        for i, item in enumerate(data.get('story_items', [])):
            print(f"\n场景{i+1}:")
            print(f"  描述: {item.get('caption', '')[:100]}...")
            print(f"  是否有图像: {'image' in item}")
            print(f"  是否有增强提示词: {'enhanced_prompt' in item}")
            if 'enhanced_prompt' in item:
                print(f"  增强提示词: {item.get('enhanced_prompt', '')[:100]}...")
        
        # 打印连贯故事
        if 'coherent_story' in data:
            print("\n连贯故事:")
            print(data.get('coherent_story', '')[:200] + "...")
    else:
        print("\n✗ 动态叙事生成API测试失败!")
        
except Exception as e:
    print(f"\n✗ 测试失败: {str(e)}")
