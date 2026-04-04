"""
测试阿里云百炼API的图像到文本功能
使用 img/generated_1770299767.png 图片进行测试
"""

import os
from PIL import Image
from models.llava_model import get_llava_model


def test_dashscope_image_to_text():
    """测试阿里云百炼API的图像到文本功能"""
    print("开始测试阿里云百炼API的图像到文本功能...")
    
    # 获取LLaVA模型实例
    model = get_llava_model()
    
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
        
        # 测试图像到文本
        print("\n测试图像到文本功能:")
        print("=" * 60)
        
        # 测试默认提示词
        print("\n1. 使用默认提示词:")
        result = model.image_to_text(image)
        print(f"结果: {result}")
        
        # 测试自定义提示词
        print("\n2. 使用自定义提示词:")
        custom_prompt = "请详细描述图片中的内容，包括物体、场景、颜色和氛围"
        result_custom = model.image_to_text(image, prompt=custom_prompt)
        print(f"结果: {result_custom}")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")


if __name__ == "__main__":
    test_dashscope_image_to_text()
