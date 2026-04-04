#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试风格迁移功能优化
"""

import os
import io
from PIL import Image
from models.qwen_image_edit_model import get_qwen_image_edit_model

# 获取风格迁移模型实例
qwen_image_edit_model = get_qwen_image_edit_model()

# 测试图像路径
TEST_IMAGE_PATH = "test_image.png"

# 确保测试图像存在
if not os.path.exists(TEST_IMAGE_PATH):
    # 创建一个简单的测试图像
    test_image = Image.new('RGB', (512, 512), color=(255, 200, 200))
    test_image.save(TEST_IMAGE_PATH)
    print(f"创建测试图像: {TEST_IMAGE_PATH}")

# 读取测试图像
with open(TEST_IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

print("=== 测试基本风格迁移功能 ===")
# 测试不同风格
test_styles = [
    "油画风格",
    "水彩风格",
    "卡通风格",
    "中国风",
    "赛博朋克风格"
]

for style in test_styles:
    print(f"\n测试风格: {style}")
    try:
        # 执行风格迁移
        result = qwen_image_edit_model.style_transfer(
            image_bytes=image_bytes,
            style_instruction=style,
            width=512,
            height=512,
            style_strength=0.7,
            evaluation=True
        )
        
        # 检查结果
        if "image" in result:
            print(f"OK: 风格迁移成功")
            print(f"  执行时间: {result.get('execution_time', 0):.2f}秒")
            
            # 保存结果
            if "filename" in result:
                print(f"  保存路径: {result['filename']}")
            
            # 打印评估结果
            if "evaluation" in result:
                eval_result = result["evaluation"]
                print(f"  评估结果:")
                print(f"    综合评分: {eval_result.get('overall_score', 0):.2f}")
                print(f"    评级: {eval_result.get('rating', '未知')}")
                print(f"    内容保持度: {eval_result.get('content_similarity', 0):.2f}")
                print(f"    风格匹配度: {eval_result.get('style_matching', 0):.2f}")
                print(f"    图像质量: {eval_result.get('image_quality', 0):.2f}")
        else:
            print(f"ERROR: 风格迁移失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"ERROR: 测试失败: {str(e)}")

print("\n=== 测试风格混合功能 ===")
try:
    # 测试风格混合
    blended_styles = [
        {"name": "油画", "weight": 0.6},
        {"name": "中国风", "weight": 0.4}
    ]
    
    result = qwen_image_edit_model.blend_styles(
        image_bytes=image_bytes,
        styles=blended_styles,
        width=512,
        height=512
    )
    
    if "image" in result:
        print("OK: 风格混合成功")
        print(f"  执行时间: {result.get('execution_time', 0):.2f}秒")
        if "filename" in result:
            print(f"  保存路径: {result['filename']}")
        print(f"  混合风格: {[style['name'] for style in result.get('blended_styles', [])]}")
    else:
        print(f"ERROR: 风格混合失败: {result.get('error', '未知错误')}")
except Exception as e:
    print(f"ERROR: 风格混合测试失败: {str(e)}")

print("\n=== 测试风格强度参数 ===")
# 测试不同风格强度
style_strengths = [0.3, 0.5, 0.7, 0.9]
for strength in style_strengths:
    print(f"\n测试风格强度: {strength}")
    try:
        result = qwen_image_edit_model.style_transfer(
            image_bytes=image_bytes,
            style_instruction="油画风格",
            width=512,
            height=512,
            style_strength=strength
        )
        
        if "image" in result:
            print(f"OK: 风格迁移成功")
            print(f"  执行时间: {result.get('execution_time', 0):.2f}秒")
            if "filename" in result:
                print(f"  保存路径: {result['filename']}")
        else:
            print(f"ERROR: 风格迁移失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"ERROR: 测试失败: {str(e)}")

print("\n测试完成！")
