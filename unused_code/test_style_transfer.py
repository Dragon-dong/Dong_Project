import requests

# 测试风格迁移API
url = "http://localhost:8000/api/style-transfer"
file_path = "test_image.png"
style_instruction = "将这幅画转换为梵高星空风格"

print(f"测试风格迁移API: {url}")
print(f"上传文件: {file_path}")
print(f"风格指令: {style_instruction}")

try:
    # 打开文件并发送请求
    with open(file_path, "rb") as f:
        files = {"file": ("test_image.png", f, "image/png")}
        data = {"style_instruction": style_instruction}
        response = requests.post(url, files=files, data=data, timeout=10)
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✓ 风格迁移API测试成功!")
    else:
        print("✗ 风格迁移API测试失败!")
        
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
