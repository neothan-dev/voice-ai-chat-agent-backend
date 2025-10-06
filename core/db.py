# Copyright © 2025 Neothan
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sqlmodel import SQLModel, create_engine, Session
import os
from typing import Generator
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from core.config import DATABASE_URL_DEFAULT, DATABASE_URL, DATABASE_NAME
from core.config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD

# PostgreSQL数据库配置
def get_database_url():
    """获取数据库URL，支持PostgreSQL和SQLite"""
    database_url = DATABASE_URL
    
    if database_url:
        # 如果设置了DATABASE_URL环境变量，直接使用
        return database_url
    else:
        # 默认使用PostgreSQL，如果没有配置则回退到SQLite
        postgres_host = POSTGRES_HOST
        postgres_port = POSTGRES_PORT
        postgres_user = POSTGRES_USER
        postgres_password = POSTGRES_PASSWORD
        postgres_db = DATABASE_NAME
        
        if all([postgres_host, postgres_port, postgres_user, postgres_password, postgres_db]):
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        else:
            return None


DATABASE_URL = get_database_url()
engine = create_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间（秒）
)

def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session

def create_database():
    postgres_db = DATABASE_NAME
    try:
        # 连接到PostgreSQL服务器（不指定数据库）
        conn = psycopg2.connect(DATABASE_URL_DEFAULT)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (postgres_db,))
        exists = cursor.fetchone()
        if not exists:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE {postgres_db}")
            print(f"数据库 '{postgres_db}' 创建成功")
        else:
            print(f"数据库 '{postgres_db}' 已存在")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        return False

def init_db():
    if create_database():
        print("数据库创建成功，开始创建表结构...")
        
        # 初始化表结构
        try:
            # 初始化数据库，创建所有表
            from models.user import User
            from models.health_data import HealthData
            from models.session import AISession, ConversationMessage
            
            SQLModel.metadata.create_all(engine)
            print("数据库初始化完成，所有表已创建") 
            print("PostgreSQL数据库初始化完成！")
        except Exception as e:
            print(f"创建表结构时出错: {e}")
    else:
        print("数据库创建失败，请检查PostgreSQL配置")