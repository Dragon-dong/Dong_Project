"""
测试 openai 库是否正确安装
"""

try:
    import openai
    print(f"openai 库导入成功，版本: {openai.__version__}")
except ImportError as e:
    print(f"openai 库导入失败: {e}")
