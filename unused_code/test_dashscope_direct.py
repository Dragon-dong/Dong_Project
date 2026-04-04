"""
直接测试阿里云百炼API的图像到文本功能
使用提供的代码和 img/generated_1770299767.png 图片进行测试
"""

import os
import base64
from PIL import Image
import io

# 尝试导入openai库
try:
    from openai import OpenAI
    print("✓ openai库导入成功")
except ImportError as e:
    print(f"✗ openai库导入失败: {str(e)}")
    print("请确保安装了兼容版本的openai和httpx库")
    exit(1)


def test_dashscope_api():
    """测试阿里云百炼API的图像到文本功能"""
    print("开始测试阿里云百炼API的图像到文本功能...")
    
    # 初始化OpenAI客户端
    try:
        client = OpenAI(
            # 使用提供的API Key
            api_key="sk-a2f939f05191490184744855395f348c",
            # 北京地域的base_url
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        print("✓ 阿里云百炼API客户端初始化成功")
    except Exception as e:
        print(f"✗ 初始化阿里云百炼API客户端失败: {str(e)}")
        return
    
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
        
        # 测试默认提示词
        print("\n1. 使用默认提示词:")
        print("=" * 60)
        
        completion = client.chat.completions.create(
            model="qwen3-vl-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                        {"type": "text", "text": "图中描绘的是什么景象?"},
                    ],
                },
            ],
        )
        
        print(f"结果: {completion.choices[0].message.content}")
        
        # 测试自定义提示词
        print("\n2. 使用自定义提示词:")
        print("=" * 60)
        
        custom_prompt = "请详细描述图片中的内容，包括物体、场景、颜色和氛围"
        completion_custom = client.chat.completions.create(
            model="qwen3-vl-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                        {"type": "text", "text": custom_prompt},
                    ],
                },
            ],
        )
        
        print(f"结果: {completion_custom.choices[0].message.content}")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_dashscope_api()
