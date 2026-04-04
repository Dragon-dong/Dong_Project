import requests

# 测试图生文API
url = "http://localhost:8000/api/image-to-text"
file_path = "test_image.png"

print(f"测试图生文API: {url}")
print(f"上传文件: {file_path}")

try:
    # 打开文件并发送请求
    with open(file_path, "rb") as f:
        files = {"file": ("test_image.png", f, "image/png")}
        response = requests.post(url, files=files, timeout=10)
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✓ 图生文API测试成功!")
    else:
        print("✗ 图生文API测试失败!")
        
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
