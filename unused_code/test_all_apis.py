"""
测试所有API端点，验证项目的实现状态
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查API"""
    print("\n=== 测试健康检查API ===")
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def test_text_to_image():
    """测试文生图API"""
    print("\n=== 测试文生图API ===")
    url = f"{BASE_URL}/api/text-to-image"
    payload = {
        "prompt": "一只可爱的猫在阳光下睡觉",
        "style": "cartoon",
        "resolution": "512x512"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"生成状态: {data.get('status')}")
            print(f"提示词: {data.get('prompt')}")
            print(f"风格: {data.get('style')}")
            print(f"是否返回图像: {'image_url' in data}")
            if 'enhanced_prompt' in data:
                print(f"增强提示词: {data.get('enhanced_prompt')}")
        else:
            print(f"响应内容: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def test_image_to_text():
    """测试图生文API"""
    print("\n=== 测试图生文API ===")
    url = f"{BASE_URL}/api/image-to-text"
    
    # 使用测试图片
    test_image_path = "test_image.png"
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(url, files=files, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"生成状态: {data.get('status')}")
                print(f"图像文件名: {data.get('image_filename')}")
                print(f"描述长度: {len(data.get('description', ''))} 字符")
                print(f"描述内容: {data.get('description', '')[:100]}...")
            else:
                print(f"响应内容: {response.text}")
                
            return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def test_generate_story():
    """测试动态叙事生成API"""
    print("\n=== 测试动态叙事生成API ===")
    url = f"{BASE_URL}/api/generate-story"
    payload = {
        "keywords": "冒险, 森林, 神秘生物",
        "story_style": "fantasy",
        "story_length": "medium"
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        end_time = time.time()
        
        print(f"状态码: {response.status_code}")
        print(f"生成耗时: {end_time - start_time:.2f} 秒")
        
        if response.status_code == 200:
            data = response.json()
            print(f"生成状态: {data.get('status')}")
            print(f"关键词: {data.get('keywords')}")
            print(f"故事风格: {data.get('story_style')}")
            print(f"故事长度: {data.get('story_length')}")
            
            story_items = data.get('story_items', [])
            print(f"生成的故事场景数: {len(story_items)}")
            
            for i, item in enumerate(story_items):
                print(f"场景{i+1}: {item.get('caption', '')[:50]}...")
                print(f"  是否有图像: {'image' in item}")
                print(f"  是否有音频: {'audio' in item}")
        else:
            print(f"响应内容: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def test_style_transfer():
    """测试风格迁移API"""
    print("\n=== 测试风格迁移API ===")
    url = f"{BASE_URL}/api/style-transfer"
    
    # 使用测试图片
    test_image_path = "test_image.png"
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {
                'file': ('test_image.png', f, 'image/png'),
                'style_instruction': (None, '赛博朋克风格+水墨画笔触')
            }
            response = requests.post(url, files=files, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"生成状态: {data.get('status')}")
                print(f"风格指令: {data.get('style_instruction')}")
                print(f"图像文件名: {data.get('image_filename')}")
                print(f"是否返回图像: {'image_url' in data}")
            else:
                print(f"响应内容: {response.text}")
                
            return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def test_multilingual_adaptation():
    """测试多语言文化适配API"""
    print("\n=== 测试多语言文化适配API ===")
    url = f"{BASE_URL}/api/multilingual-adaptation"
    payload = {
        "content": "这是一个测试内容，用于多语言文化适配功能",
        "target_lang": "en"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"生成状态: {data.get('status')}")
            print(f"适配结果: {data.get('result', '')}")
        else:
            print(f"响应内容: {response.text}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


def main():
    """测试所有API端点"""
    print("开始测试所有API端点...")
    print(f"测试目标: {BASE_URL}")
    print("=" * 60)
    
    # 测试各个API
    results = {
        "健康检查": test_health_check(),
        "文生图": test_text_to_image(),
        "图生文": test_image_to_text(),
        "动态叙事生成": test_generate_story(),
        "风格迁移": test_style_transfer(),
        "多语言文化适配": test_multilingual_adaptation()
    }
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("-" * 60)
    
    for api, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{api}: {status}")
    
    print("=" * 60)
    print("测试完成!")


if __name__ == "__main__":
    main()
