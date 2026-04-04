#!/usr/bin/env python3
"""
数据库表结构更新脚本
用于修改现有表结构以解决字段长度问题
"""

import mysql.connector
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# MySQL配置
mysql_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'cross_modal_system'),
    'charset': 'utf8mb4'
}

def update_database_schema():
    """更新数据库表结构"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**mysql_config)
        print("✓ 连接数据库成功")
        
        with conn.cursor() as cursor:
            # 修改 task_type 字段类型
            print("正在修改 task_type 字段...")
            cursor.execute('''
            ALTER TABLE generation_history
            MODIFY COLUMN task_type VARCHAR(100) NOT NULL
            ''')
            print("✓ task_type 字段修改成功")
            
            # 修改 output_data 字段类型
            print("正在修改 output_data 字段...")
            cursor.execute('''
            ALTER TABLE generation_history
            MODIFY COLUMN output_data LONGTEXT NOT NULL
            ''')
            print("✓ output_data 字段修改成功")
            
            # 提交事务
            conn.commit()
            print("✓ 数据库表结构更新成功")
            
    except Exception as e:
        print(f"✗ 更新数据库表结构失败: {str(e)}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("✓ 数据库连接已关闭")

if __name__ == "__main__":
    print("开始更新数据库表结构...")
    update_database_schema()
    print("数据库表结构更新完成")
