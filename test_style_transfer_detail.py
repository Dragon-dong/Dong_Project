import requests
import base64
from PIL import Image
import io
import os
import json

# API端点
API_URL = "http://localhost:8000/api/style-transfer"

# 测试图像路径
TEST_IMAGE_PATH = "test_image.png"

# 测试风格指令
TEST_STYLES = [
    "水墨画风格，中国风，保留原始图像内容",
    "梵高风格，星空，印象派，保留原始图像内容",
    "卡通风格，迪士尼风格，保留原始图像内容",
    "赛博朋克风格，未来感，保留原始图像内容"
]

def test_style_transfer():
    """详细测试风格迁移功能"""
    print("开始详细测试风格迁移功能...")
    
    # 检查测试图像是否存在
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"错误：测试图像 {TEST_IMAGE_PATH} 不存在")
        return
    
    # 读取测试图像
    with open(TEST_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    
    # 测试不同风格
    for style in TEST_STYLES:
        print(f"\n测试风格：{style}")
        
        # 构建请求
        files = {
            "file": ("test_image.png", image_bytes, "image/png")
        }
        data = {
            "style_instruction": style
        }
        
        try:
            # 发送请求
            response = requests.post(API_URL, files=files, data=data, timeout=60)
            response.raise_for_status()  # 检查请求是否成功
            
            # 处理响应
            result = response.json()
            if result.get("status") == "success":
                print("✓ 风格迁移成功")
                print(f"  图像文件名：{result.get('image_filename')}")
                print(f"  风格指令：{result.get('style_instruction')}")
                print(f"  图像URL长度：{len(result.get('image_url', ''))} 字符")
                
                # 保存响应结果
                timestamp = int(os.time() if hasattr(os, 'time') else time.time())
                with open(f"style_transfer_result_{timestamp}.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  响应结果已保存到：style_transfer_result_{timestamp}.json")
            else:
                print(f"✗ 风格迁移失败：{result.get('detail', '未知错误')}")
                
        except Exception as e:
            print(f"✗ 请求失败：{str(e)}")
    
    print("\n风格迁移功能详细测试完成！")

if __name__ == "__main__":
    import time
    test_style_transfer()
