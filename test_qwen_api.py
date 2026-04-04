import requests
import base64
from PIL import Image
import io
import os
import json
import time

# 配置
API_KEY = "sk-ikomatcbxqwpaljmpcyxasoryvyneoaqbfphyclfmukltfhm"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal_conversation/generation"
TEST_IMAGE_PATH = "test_image.png"

# 测试风格指令
TEST_STYLES = [
    "水墨画风格，中国风，保留原始图像内容",
    "梵高风格，星空，印象派，保留原始图像内容",
    "卡通风格，迪士尼风格，保留原始图像内容"
]

def test_qwen_image_edit_api():
    """直接测试Qwen-Image-Edit API"""
    print("开始直接测试Qwen-Image-Edit API...")
    
    # 检查测试图像是否存在
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"错误：测试图像 {TEST_IMAGE_PATH} 不存在")
        return
    
    # 读取测试图像
    with open(TEST_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    
    # 将图像转换为Base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # 测试不同风格
    for style in TEST_STYLES:
        print(f"\n测试风格：{style}")
        
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
                            "text": f"请按照以下风格指令对图像进行风格迁移，保持原始图像的内容和构图不变：{style}"
                        }
                    ]
                }
            ],
            "stream": False,
            "n": 1,
            "watermark": False,
            "negative_prompt": "低质量，模糊，扭曲，丑陋，改变原始内容",
            "prompt_extend": True,
            "size": "512*512"
        }
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            # 发送请求
            start_time = time.time()
            response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            response.raise_for_status()  # 检查请求是否成功
            end_time = time.time()
            
            print(f"✓ API调用成功，耗时: {end_time - start_time:.2f}秒")
            
            # 处理响应
            data = response.json()
            
            # 保存响应结果
            timestamp = int(time.time())
            with open(f"qwen_api_response_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  响应结果已保存到：qwen_api_response_{timestamp}.json")
            
            # 提取生成的图像
            if 'output' in data and 'choices' in data['output']:
                choice = data['output']['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    for item in content:
                        if 'image' in item:
                            image_url = item['image']
                            print(f"  生成的图像URL: {image_url}")
                            
                            # 下载图像
                            image_response = requests.get(image_url)
                            image = Image.open(io.BytesIO(image_response.content))
                            
                            # 保存图像
                            if not os.path.exists('img'):
                                os.makedirs('img')
                            filename = f"img/qwen_api_test_{timestamp}.png"
                            image.save(filename)
                            print(f"  图像已保存到：{filename}")
            
        except Exception as e:
            print(f"✗ API调用失败：{str(e)}")
            # 保存错误响应
            if hasattr(response, 'text'):
                timestamp = int(time.time())
                with open(f"qwen_api_error_{timestamp}.json", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"  错误响应已保存到：qwen_api_error_{timestamp}.json")
    
    print("\nQwen-Image-Edit API测试完成！")

if __name__ == "__main__":
    test_qwen_image_edit_api()
