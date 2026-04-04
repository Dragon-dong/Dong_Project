import requests
import json
import base64
from PIL import Image
import io
import os

# 测试SiliconFlow API
def test_siliconflow_api():
    print("测试SiliconFlow API...")
    
    # SiliconFlow API配置
    url = "https://api.siliconflow.cn/v1/images/generations"
    model_name = "Kwai-Kolors/Kolors"
    prompt = "一只可爱的猫在阳光下睡觉"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "image_size": "512x512",
        "batch_size": 1,
        "num_inference_steps": 20,
        "guidance_scale": 7.5
    }
    headers = {
        "Authorization": "Bearer sk-ikomatcbxqwpaljmpcyxasoryvyneoaqbfphyclfmukltfhm",
        "Content-Type": "application/json"
    }
    
    print(f"API请求参数: model={model_name}, prompt={prompt[:50]}..., size=512x512")
    
    try:
        # 调用API
        response = requests.request("POST", url, json=payload, headers=headers, timeout=30)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:1000]}...")
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"API调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        # 处理响应
        data = response.json()
        print(f"响应数据结构: {list(data.keys())}")
        
        if "images" in data and len(data["images"]) > 0:
            image_url = data["images"][0]["url"]
            print(f"图像URL: {image_url}")
            
            # 下载图像
            image_response = requests.get(image_url, timeout=30)
            print(f"图像下载状态码: {image_response.status_code}")
            print(f"图像数据长度: {len(image_response.content)} bytes")
            
            # 检查图像数据长度
            if len(image_response.content) < 1000:  # 小于1KB的图像可能是错误图像
                print(f"图像数据过小: {len(image_response.content)} bytes")
                print(f"图像数据: {image_response.content[:100]}...")
                return False
            
            # 保存图像
            if not os.path.exists('test_images'):
                os.makedirs('test_images')
            
            # 保存原始图像数据
            with open('test_images/raw_image.bin', 'wb') as f:
                f.write(image_response.content)
            print("原始图像数据已保存到: test_images/raw_image.bin")
            
            # 尝试打开图像
            try:
                image = Image.open(io.BytesIO(image_response.content))
                print(f"图像信息: {image.size}, {image.mode}")
                
                # 保存图像
                image.save('test_images/test_image.png')
                print("图像已保存到: test_images/test_image.png")
                
                # 显示图像
                image.show()
                return True
            except Exception as e:
                print(f"打开图像失败: {str(e)}")
                return False
        else:
            print("API响应中没有图像数据")
            print(f"响应数据: {data}")
            return False
            
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_siliconflow_api()
