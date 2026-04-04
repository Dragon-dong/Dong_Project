"""
检查 Python 环境和库路径
"""

import sys
import os

print("Python 解释器路径:", sys.executable)
print("Python 版本:", sys.version)
print("\n库搜索路径:")
for path in sys.path:
    print(f"  - {path}")

print("\n当前工作目录:", os.getcwd())
