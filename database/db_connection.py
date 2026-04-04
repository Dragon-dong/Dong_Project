"""
数据库连接和初始化模块
负责MySQL和Redis的连接管理、数据库初始化和连接池配置
"""

import os
import mysql.connector
import redis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DatabaseConnection:
    """数据库连接管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        # MySQL配置
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'password'),
            'database': os.getenv('MYSQL_DATABASE', 'cross_modal_system'),
            'charset': 'utf8mb4'
        }
        
        # Redis配置
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0)),
            'password': os.getenv('REDIS_PASSWORD', '')
        }
        
        # 连接实例
        self.mysql_conn = None
        self.redis_client = None
        
        # 初始化连接
        self.init_connections()
        
    def init_connections(self):
        """初始化数据库连接"""
        try:
            # 连接MySQL
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)
            print("OK: MySQL连接成功")
            
            # 初始化数据库表结构
            self.init_database()
            
        except Exception as e:
            print(f"ERROR: MySQL连接失败: {str(e)}")
        
        try:
            # 连接Redis
            self.redis_client = redis.Redis(**self.redis_config)
            # 测试连接
            self.redis_client.ping()
            print("OK: Redis连接成功")
        except Exception as e:
            print(f"ERROR: Redis连接失败: {str(e)}")
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with self.mysql_conn.cursor(dictionary=True) as cursor:
                # 创建用户表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建生成历史表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    task_type VARCHAR(100) NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data LONGTEXT NOT NULL,
                    status ENUM('success', 'failed') NOT NULL,
                    error_message TEXT,
                    duration FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建偏好设置表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    preference_key VARCHAR(50) NOT NULL,
                    preference_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY user_preference (user_id, preference_key),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 创建系统配置表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    config_key VARCHAR(50) NOT NULL UNIQUE,
                    config_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                ''')
                
                # 提交事务
                self.mysql_conn.commit()
                print("OK: 数据库表结构初始化成功")
                
        except Exception as e:
            print(f"ERROR: 数据库表结构初始化失败: {str(e)}")
            self.mysql_conn.rollback()
    
    def get_mysql_connection(self):
        """获取MySQL连接
        
        Returns:
            mysql.connector.connection.MySQLConnection: MySQL连接实例
        """
        # 检查连接是否有效
        if self.mysql_conn and self.mysql_conn.is_connected():
            return self.mysql_conn
        else:
            # 重新连接
            try:
                self.mysql_conn = mysql.connector.connect(**self.mysql_config)
                print("OK: MySQL重新连接成功")
                return self.mysql_conn
            except Exception as e:
                print(f"ERROR: MySQL重新连接失败: {str(e)}")
                return None
    
    def get_redis_client(self):
        """获取Redis客户端
        
        Returns:
            redis.Redis: Redis客户端实例
        """
        # 检查连接是否有效
        if self.redis_client:
            try:
                self.redis_client.ping()
                return self.redis_client
            except Exception as e:
                print(f"ERROR: Redis连接失效: {str(e)}")
        
        # 重新连接
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            self.redis_client.ping()
            print("OK: Redis重新连接成功")
            return self.redis_client
        except Exception as e:
            print(f"ERROR: Redis重新连接失败: {str(e)}")
            return None
    
    def close_connections(self):
        """关闭数据库连接"""
        try:
            if self.mysql_conn and self.mysql_conn.is_connected():
                self.mysql_conn.close()
                print("OK: MySQL连接已关闭")
        except Exception as e:
            print(f"ERROR: 关闭MySQL连接失败: {str(e)}")
        
        try:
            if self.redis_client:
                self.redis_client.close()
                print("OK: Redis连接已关闭")
        except Exception as e:
            print(f"ERROR: 关闭Redis连接失败: {str(e)}")

# 全局数据库连接实例
db_instance = None

def get_db_connection():
    """获取数据库连接实例（单例模式）
    
    Returns:
        DatabaseConnection: 数据库连接实例
    """
    global db_instance
    if db_instance is None:
        db_instance = DatabaseConnection()
    return db_instance

# 测试连接
if __name__ == "__main__":
    db = get_db_connection()
    print("数据库连接测试完成")
    db.close_connections()
