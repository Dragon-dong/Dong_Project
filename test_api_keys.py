import requests
import base64
from PIL import Image
import io
import os

# 测试阿里云百炼API Key
TEST_API_KEYS = {
    "LLaVA & LLM模型": "sk-a2f939f05191490184744855395f348c",
    "Qwen-Image-Edit模型": "sk-ikomatcbxqwpaljmpcyxasoryvyneoaqbfphyclfmukltfhm"
}

# 测试图像路径
TEST_IMAGE_PATH = "test_image.png"

def test_api_key(api_key, api_name):
    """测试API Key是否有效"""
    print(f"\n测试 {api_name} 的API Key...")
    
    # 测试LLaVA/LLM API
    if api_name == "LLaVA & LLM模型":
        api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        
        # 构建请求数据
        payload = {
            "model": "qwen3-vl-plus",
            "messages": [
                {
                    "role": "user",
                    "content": "你好，测试API Key是否有效"
                }
            ],
            "max_tokens": 100
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✓ {api_name} 的API Key有效")
                return True
            else:
                print(f"✗ {api_name} 的API Key无效，状态码: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
        except Exception as e:
            print(f"✗ {api_name} 的API Key测试失败: {str(e)}")
            return False
    
    # 测试Qwen-Image-Edit API
    elif api_name == "Qwen-Image-Edit模型":
        api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal_conversation/generation"
        
        # 读取测试图像
        if not os.path.exists(TEST_IMAGE_PATH):
            print(f"错误：测试图像 {TEST_IMAGE_PATH} 不存在")
            return False
        
        with open(TEST_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()
        
        # 将图像转换为Base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 构建请求数据
        payload = {
            "model": "qwen-image-edit-max",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": f"data:image/png;base64,{image_base64}"
                        },
                        {
                            "text": "请简单描述这张图像"
                        }
                    ]
                }
            ],
            "stream": False,
            "n": 1,
            "watermark": False,
            "size": "512*512"
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                print(f"✓ {api_name} 的API Key有效")
                return True
            else:
                print(f"✗ {api_name} 的API Key无效，状态码: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
        except Exception as e:
            print(f"✗ {api_name} 的API Key测试失败: {str(e)}")
            return False

def main():
    """测试所有API Key"""
    print("开始测试项目中的API Key...")
    
    valid_keys = []
    invalid_keys = []
    
    for api_name, api_key in TEST_API_KEYS.items():
        if test_api_key(api_key, api_name):
            valid_keys.append(api_name)
        else:
            invalid_keys.append(api_name)
    
    print("\n测试结果总结:")
    print(f"有效的API Key: {len(valid_keys)}")
    for api_name in valid_keys:
        print(f"  - {api_name}")
    
    print(f"无效的API Key: {len(invalid_keys)}")
    for api_name in invalid_keys:
        print(f"  - {api_name}")
    
    if invalid_keys:
        print("\n建议: 请获取有效的API Key并更新到相应的模型文件中")
    else:
        print("\n所有API Key都有效，项目可以正常使用")

if __name__ == "__main__":
    main()
