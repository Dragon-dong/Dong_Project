"""
使用 requests 库测试阿里云百炼API的图像到文本功能
绕过 httpx 版本不兼容问题
"""

import os
import base64
import json
import requests
from PIL import Image
import io


def test_dashscope_with_requests():
    """使用 requests 库测试阿里云百炼API的图像到文本功能"""
    print("开始测试阿里云百炼API的图像到文本功能...")
    
    # API配置
    api_key = "sk-a2f939f05191490184744855395f348c"
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    # 测试图片路径
    image_path = "img/generated_1770299767.png"
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"错误: 图片文件 {image_path} 不存在")
        return
    
    try:
        # 加载图片
        print(f"加载图片: {image_path}")
        image = Image.open(image_path)
        image = image.convert("RGB")
        
        # 将图片转换为字节
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        image_bytes = img_byte_arr.getvalue()
        
        # 将图像字节转换为base64编码
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # 构建请求数据
        payload = {
            "model": "qwen3-vl-plus",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        },
                        {"type": "text", "text": "图中描绘的是什么景象?"}
                    ]
                }
            ]
        }
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 发送请求
        print("\n发送请求到阿里云百炼API...")
        response = requests.post(url, headers=headers, json=payload)
        
        # 处理响应
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 解析响应
            data = response.json()
            result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print("\n" + "=" * 60)
            print("测试结果:")
            print("=" * 60)
            print(result)
            print("=" * 60)
            print("测试完成!")
        else:
            print(f"\n请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"\n测试失败: {str(e)}")


if __name__ == "__main__":
    test_dashscope_with_requests()
