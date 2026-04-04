"""
数据库操作封装模块
提供用户管理、生成历史管理、偏好设置和系统配置的CRUD操作
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from database.db_connection import get_db_connection

class DatabaseOperations:
    """数据库操作封装类"""
    
    def __init__(self):
        """初始化数据库操作实例"""
        self.db = get_db_connection()
    
    # 用户管理操作
    def create_user(self, username: str, email: Optional[str], password_hash: str) -> Optional[int]:
        """创建新用户
        
        Args:
            username: 用户名
            email: 邮箱（可选）
            password_hash: 密码哈希值
            
        Returns:
            int: 用户ID，创建失败返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            # 确保email不为None，为空字符串
            email = email or ""
            
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                INSERT INTO users (username, email, password_hash) 
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (username, email, password_hash))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户信息，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Dict: 用户信息，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                return cursor.fetchone()
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户信息
        
        Args:
            email: 邮箱
            
        Returns:
            Dict: 用户信息，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                return cursor.fetchone()
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 更新是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            for key, value in kwargs.items():
                if key in ['username', 'email', 'password_hash']:
                    update_fields.append(f"{key} = %s")
                    update_values.append(value)
            
            if not update_fields:
                return True
            
            update_values.append(user_id)
            
            with conn.cursor(dictionary=True) as cursor:
                sql = f"""
                UPDATE users 
                SET {', '.join(update_fields)} 
                WHERE id = %s
                """
                cursor.execute(sql, update_values)
                conn.commit()
                return True
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "DELETE FROM users WHERE id = %s"
                cursor.execute(sql, (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False
    
    # 生成历史管理操作
    def create_generation_history(
        self, 
        task_type: str, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any], 
        status: str, 
        user_id: Optional[int] = None, 
        error_message: Optional[str] = None, 
        duration: Optional[float] = None
    ) -> Optional[int]:
        """创建生成历史记录
        
        Args:
            task_type: 任务类型
            input_data: 输入数据
            output_data: 输出数据
            status: 状态
            user_id: 用户ID（可选）
            error_message: 错误信息（可选）
            duration: 执行时长（可选）
            
        Returns:
            int: 记录ID，创建失败返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            # 转换数据为JSON字符串
            input_data_json = json.dumps(input_data, ensure_ascii=False)
            output_data_json = json.dumps(output_data, ensure_ascii=False)
            
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                INSERT INTO generation_history 
                (user_id, task_type, input_data, output_data, status, error_message, duration) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    user_id, task_type, input_data_json, output_data_json, 
                    status, error_message, duration
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建生成历史失败: {str(e)}")
            return None
    
    def get_generation_history(
        self, 
        user_id: Optional[int] = None, 
        task_type: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取生成历史记录
        
        Args:
            user_id: 用户ID（可选）
            task_type: 任务类型（可选）
            limit: 返回记录数限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 生成历史记录列表
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return []
            
            # 构建查询条件
            conditions = []
            params = []
            
            if user_id:
                conditions.append("user_id = %s")
                params.append(user_id)
            
            if task_type:
                conditions.append("task_type = %s")
                params.append(task_type)
            
            # 构建SQL语句
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            params.extend([limit, offset])
            
            with conn.cursor(dictionary=True) as cursor:
                sql = f"""
                SELECT * FROM generation_history 
                {where_clause} 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
                """
                cursor.execute(sql, params)
                
                # 转换JSON字符串为字典
                results = []
                for row in cursor.fetchall():
                    row['input_data'] = json.loads(row['input_data'])
                    row['output_data'] = json.loads(row['output_data'])
                    results.append(row)
                
                return results
        except Exception as e:
            print(f"获取生成历史失败: {str(e)}")
            return []
    
    def get_generation_history_by_id(self, history_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取生成历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            Dict: 生成历史记录，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM generation_history WHERE id = %s"
                cursor.execute(sql, (history_id,))
                row = cursor.fetchone()
                
                if row:
                    row['input_data'] = json.loads(row['input_data'])
                    row['output_data'] = json.loads(row['output_data'])
                
                return row
        except Exception as e:
            print(f"获取生成历史失败: {str(e)}")
            return None
    
    def delete_generation_history(self, history_id: int) -> bool:
        """删除生成历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "DELETE FROM generation_history WHERE id = %s"
                cursor.execute(sql, (history_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除生成历史失败: {str(e)}")
            return False
    
    # 偏好设置操作
    def set_user_preference(self, user_id: int, preference_key: str, preference_value: Any) -> bool:
        """设置用户偏好
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键
            preference_value: 偏好值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            # 转换值为JSON字符串
            preference_value_json = json.dumps(preference_value, ensure_ascii=False)
            
            with conn.cursor(dictionary=True) as cursor:
                # 使用INSERT ... ON DUPLICATE KEY UPDATE语法
                sql = """
                INSERT INTO user_preferences (user_id, preference_key, preference_value) 
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                preference_value = %s, 
                updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (
                    user_id, preference_key, preference_value_json, preference_value_json
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"设置用户偏好失败: {str(e)}")
            return False
    
    def get_user_preference(self, user_id: int, preference_key: str) -> Optional[Any]:
        """获取用户偏好
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键
            
        Returns:
            Any: 偏好值，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                SELECT preference_value FROM user_preferences 
                WHERE user_id = %s AND preference_key = %s
                """
                cursor.execute(sql, (user_id, preference_key))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row['preference_value'])
                return None
        except Exception as e:
            print(f"获取用户偏好失败: {str(e)}")
            return None
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户所有偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户偏好字典
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return {}
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT preference_key, preference_value FROM user_preferences WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                
                preferences = {}
                for row in cursor.fetchall():
                    preferences[row['preference_key']] = json.loads(row['preference_value'])
                
                return preferences
        except Exception as e:
            print(f"获取用户偏好失败: {str(e)}")
            return {}
    
    def delete_user_preference(self, user_id: int, preference_key: str) -> bool:
        """删除用户偏好
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            with conn.cursor(dictionary=True) as cursor:
                sql = """
                DELETE FROM user_preferences 
                WHERE user_id = %s AND preference_key = %s
                """
                cursor.execute(sql, (user_id, preference_key))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除用户偏好失败: {str(e)}")
            return False
    
    # 系统配置操作
    def set_system_config(self, config_key: str, config_value: Any) -> bool:
        """设置系统配置
        
        Args:
            config_key: 配置键
            config_value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            # 转换值为JSON字符串
            config_value_json = json.dumps(config_value, ensure_ascii=False)
            
            with conn.cursor(dictionary=True) as cursor:
                # 使用INSERT ... ON DUPLICATE KEY UPDATE语法
                sql = """
                INSERT INTO system_config (config_key, config_value) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE 
                config_value = %s, 
                updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (config_key, config_value_json, config_value_json))
                conn.commit()
                return True
        except Exception as e:
            print(f"设置系统配置失败: {str(e)}")
            return False
    
    def get_system_config(self, config_key: str) -> Optional[Any]:
        """获取系统配置
        
        Args:
            config_key: 配置键
            
        Returns:
            Any: 配置值，未找到返回None
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return None
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT config_value FROM system_config WHERE config_key = %s"
                cursor.execute(sql, (config_key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row['config_value'])
                return None
        except Exception as e:
            print(f"获取系统配置失败: {str(e)}")
            return None
    
    def get_all_system_configs(self) -> Dict[str, Any]:
        """获取所有系统配置
        
        Returns:
            Dict: 系统配置字典
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return {}
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "SELECT config_key, config_value FROM system_config"
                cursor.execute(sql)
                
                configs = {}
                for row in cursor.fetchall():
                    configs[row['config_key']] = json.loads(row['config_value'])
                
                return configs
        except Exception as e:
            print(f"获取系统配置失败: {str(e)}")
            return {}
    
    def delete_system_config(self, config_key: str) -> bool:
        """删除系统配置
        
        Args:
            config_key: 配置键
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = self.db.get_mysql_connection()
            if not conn:
                return False
            
            with conn.cursor(dictionary=True) as cursor:
                sql = "DELETE FROM system_config WHERE config_key = %s"
                cursor.execute(sql, (config_key,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除系统配置失败: {str(e)}")
            return False
    
    # Redis缓存操作
    def set_cache(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒，可选）
            
        Returns:
            bool: 设置是否成功
        """
        try:
            redis_client = self.db.get_redis_client()
            if not redis_client:
                return False
            
            # 转换值为JSON字符串
            value_json = json.dumps(value, ensure_ascii=False)
            
            if expire:
                redis_client.setex(key, expire, value_json)
            else:
                redis_client.set(key, value_json)
            
            return True
        except Exception as e:
            print(f"设置缓存失败: {str(e)}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值，未找到返回None
        """
        try:
            redis_client = self.db.get_redis_client()
            if not redis_client:
                return None
            
            value_json = redis_client.get(key)
            if value_json:
                return json.loads(value_json)
            return None
        except Exception as e:
            print(f"获取缓存失败: {str(e)}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 删除是否成功
        """
        try:
            redis_client = self.db.get_redis_client()
            if not redis_client:
                return False
            
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"删除缓存失败: {str(e)}")
            return False
    
    def clear_cache_pattern(self, pattern: str) -> bool:
        """清除匹配模式的缓存
        
        Args:
            pattern: 缓存键模式
            
        Returns:
            bool: 清除是否成功
        """
        try:
            redis_client = self.db.get_redis_client()
            if not redis_client:
                return False
            
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"清除缓存失败: {str(e)}")
            return False

# 全局数据库操作实例
db_operations_instance = None

def get_db_operations() -> DatabaseOperations:
    """获取数据库操作实例（单例模式）
    
    Returns:
        DatabaseOperations: 数据库操作实例
    """
    global db_operations_instance
    if db_operations_instance is None:
        db_operations_instance = DatabaseOperations()
    return db_operations_instance
