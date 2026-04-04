#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试多语言文化适配模型
"""

from models.multilingual_model import get_multilingual_model

# 获取多语言模型实例
multilingual_model = get_multilingual_model()

# 测试语言检测
print("=== 测试语言检测 ===")
test_texts = [
    "这是一段中文文本",
    "This is an English text",
    "これは日本語のテキストです",
    "Hello 世界"
]

for text in test_texts:
    lang = multilingual_model.detect_language(text)
    print(f"文本: '{text}' -> 语言: {lang}")

# 测试文化背景获取
print("\n=== 测试文化背景获取 ===")
languages = ["zh", "en", "ja"]
for lang in languages:
    context = multilingual_model.get_cultural_context(lang)
    print(f"语言: {lang} -> 文化风格: {context['style']}")

# 测试风格化翻译
print("\n=== 测试风格化翻译 ===")
test_cases = [
    ("这是一段中文文本", "en"),
    ("This is an English text", "zh"),
    ("これは日本語のテキストです", "zh")
]

for text, target_lang in test_cases:
    translated = multilingual_model.stylized_translation(text, target_lang)
    print(f"原文: '{text}' -> 目标语言: {target_lang} -> 翻译: '{translated}'")

# 测试内容文化适配
print("\n=== 测试内容文化适配 ===")
test_content = "这是一段需要文化适配的内容"
result = multilingual_model.adapt_content_to_culture(test_content, "en")
print(f"原文: '{result['original_content']}'")
print(f"适配后: '{result['adapted_content']}'")
print(f"目标语言: {result['target_language']}")
print(f"文化风格: {result['cultural_context']['style']}")

print("\n测试完成！")
