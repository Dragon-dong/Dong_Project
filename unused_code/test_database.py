"""
数据库测试脚本
测试数据库连接、初始化和各种操作是否正常工作
"""

import time
import json
from database.db_connection import get_db_connection
from database.db_operations import get_db_operations

class TestDatabase:
    """数据库测试类"""
    
    def __init__(self):
        """初始化测试类"""
        self.db = get_db_connection()
        self.db_ops = get_db_operations()
        self.test_user_id = None
        
    def test_connection(self):
        """测试数据库连接"""
        print("\n=== 测试数据库连接 ===")
        
        # 测试MySQL连接
        mysql_conn = self.db.get_mysql_connection()
        if mysql_conn:
            print("✓ MySQL连接成功")
        else:
            print("✗ MySQL连接失败")
        
        # 测试Redis连接
        redis_client = self.db.get_redis_client()
        if redis_client:
            print("✓ Redis连接成功")
        else:
            print("✗ Redis连接失败")
    
    def test_user_operations(self):
        """测试用户管理操作"""
        print("\n=== 测试用户管理操作 ===")
        
        # 创建测试用户
        username = f"test_user_{int(time.time())}"
        email = f"{username}@example.com"
        password_hash = "test_password_hash"
        
        print(f"创建测试用户: {username}")
        user_id = self.db_ops.create_user(username, email, password_hash)
        
        if user_id:
            print(f"✓ 创建用户成功，ID: {user_id}")
            self.test_user_id = user_id
            
            # 根据ID获取用户
            user = self.db_ops.get_user_by_id(user_id)
            if user:
                print("✓ 根据ID获取用户成功")
                print(f"  用户名: {user['username']}")
                print(f"  邮箱: {user['email']}")
            else:
                print("✗ 根据ID获取用户失败")
            
            # 根据用户名获取用户
            user_by_username = self.db_ops.get_user_by_username(username)
            if user_by_username:
                print("✓ 根据用户名获取用户成功")
            else:
                print("✗ 根据用户名获取用户失败")
            
            # 更新用户信息
            new_email = f"updated_{email}"
            update_success = self.db_ops.update_user(user_id, email=new_email)
            if update_success:
                print("✓ 更新用户信息成功")
                updated_user = self.db_ops.get_user_by_id(user_id)
                if updated_user and updated_user['email'] == new_email:
                    print("✓ 验证更新成功")
                else:
                    print("✗ 验证更新失败")
            else:
                print("✗ 更新用户信息失败")
        else:
            print("✗ 创建用户失败")
    
    def test_generation_history(self):
        """测试生成历史管理操作"""
        print("\n=== 测试生成历史管理操作 ===")
        
        # 创建测试生成历史
        input_data = {"prompt": "测试生成", "style": "cartoon"}
        output_data = {"image_url": "test_image_url", "status": "success"}
        
        history_id = self.db_ops.create_generation_history(
            task_type="text_to_image",
            input_data=input_data,
            output_data=output_data,
            status="success",
            user_id=self.test_user_id,
            duration=1.23
        )
        
        if history_id:
            print(f"✓ 创建生成历史成功，ID: {history_id}")
            
            # 根据ID获取生成历史
            history = self.db_ops.get_generation_history_by_id(history_id)
            if history:
                print("✓ 根据ID获取生成历史成功")
                print(f"  任务类型: {history['task_type']}")
                print(f"  状态: {history['status']}")
            else:
                print("✗ 根据ID获取生成历史失败")
            
            # 获取生成历史列表
            history_list = self.db_ops.get_generation_history(
                task_type="text_to_image",
                limit=10
            )
            if history_list:
                print(f"✓ 获取生成历史列表成功，共 {len(history_list)} 条")
            else:
                print("✗ 获取生成历史列表失败")
            
            # 删除生成历史
            delete_success = self.db_ops.delete_generation_history(history_id)
            if delete_success:
                print("✓ 删除生成历史成功")
            else:
                print("✗ 删除生成历史失败")
        else:
            print("✗ 创建生成历史失败")
    
    def test_user_preferences(self):
        """测试偏好设置操作"""
        print("\n=== 测试偏好设置操作 ===")
        
        if not self.test_user_id:
            print("⚠️  跳过测试，未创建测试用户")
            return
        
        # 设置用户偏好
        preference_key = "default_style"
        preference_value = "cartoon"
        
        set_success = self.db_ops.set_user_preference(
            self.test_user_id, preference_key, preference_value
        )
        
        if set_success:
            print("✓ 设置用户偏好成功")
            
            # 获取用户偏好
            get_value = self.db_ops.get_user_preference(
                self.test_user_id, preference_key
            )
            if get_value == preference_value:
                print("✓ 获取用户偏好成功")
                print(f"  偏好值: {get_value}")
            else:
                print("✗ 获取用户偏好失败")
            
            # 获取所有用户偏好
            all_preferences = self.db_ops.get_user_preferences(self.test_user_id)
            if all_preferences:
                print(f"✓ 获取所有用户偏好成功，共 {len(all_preferences)} 项")
            else:
                print("✗ 获取所有用户偏好失败")
            
            # 删除用户偏好
            delete_success = self.db_ops.delete_user_preference(
                self.test_user_id, preference_key
            )
            if delete_success:
                print("✓ 删除用户偏好成功")
            else:
                print("✗ 删除用户偏好失败")
        else:
            print("✗ 设置用户偏好失败")
    
    def test_system_config(self):
        """测试系统配置操作"""
        print("\n=== 测试系统配置操作 ===")
        
        # 设置系统配置
        config_key = f"test_config_{int(time.time())}"
        config_value = {"test_key": "test_value", "test_number": 123}
        
        set_success = self.db_ops.set_system_config(config_key, config_value)
        if set_success:
            print("✓ 设置系统配置成功")
            
            # 获取系统配置
            get_value = self.db_ops.get_system_config(config_key)
            if get_value == config_value:
                print("✓ 获取系统配置成功")
                print(f"  配置值: {json.dumps(get_value, ensure_ascii=False)}")
            else:
                print("✗ 获取系统配置失败")
            
            # 获取所有系统配置
            all_configs = self.db_ops.get_all_system_configs()
            if all_configs:
                print(f"✓ 获取所有系统配置成功，共 {len(all_configs)} 项")
            else:
                print("✗ 获取所有系统配置失败")
            
            # 删除系统配置
            delete_success = self.db_ops.delete_system_config(config_key)
            if delete_success:
                print("✓ 删除系统配置成功")
            else:
                print("✗ 删除系统配置失败")
        else:
            print("✗ 设置系统配置失败")
    
    def test_redis_cache(self):
        """测试Redis缓存操作"""
        print("\n=== 测试Redis缓存操作 ===")
        
        # 设置缓存
        cache_key = f"test_cache_{int(time.time())}"
        cache_value = {"test_key": "test_value", "test_time": time.time()}
        
        set_success = self.db_ops.set_cache(cache_key, cache_value, expire=30)
        if set_success:
            print("✓ 设置缓存成功")
            
            # 获取缓存
            get_value = self.db_ops.get_cache(cache_key)
            if get_value == cache_value:
                print("✓ 获取缓存成功")
                print(f"  缓存值: {json.dumps(get_value, ensure_ascii=False)}")
            else:
                print("✗ 获取缓存失败")
            
            # 清除缓存
            delete_success = self.db_ops.delete_cache(cache_key)
            if delete_success:
                print("✓ 删除缓存成功")
                
                # 验证缓存已删除
                deleted_value = self.db_ops.get_cache(cache_key)
                if deleted_value is None:
                    print("✓ 验证缓存已删除成功")
                else:
                    print("✗ 验证缓存已删除失败")
            else:
                print("✗ 删除缓存失败")
        else:
            print("✗ 设置缓存失败")
    
    def test_cleanup(self):
        """测试清理"""
        print("\n=== 测试清理 ===")
        
        # 删除测试用户
        if self.test_user_id:
            delete_success = self.db_ops.delete_user(self.test_user_id)
            if delete_success:
                print("✓ 删除测试用户成功")
            else:
                print("✗ 删除测试用户失败")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始数据库测试...")
        
        # 运行所有测试
        self.test_connection()
        self.test_user_operations()
        self.test_generation_history()
        self.test_user_preferences()
        self.test_system_config()
        self.test_redis_cache()
        self.test_cleanup()
        
        print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test = TestDatabase()
    test.run_all_tests()
