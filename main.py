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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import auth, ai, device, health, speech, navigation, dashboard
from core.db import init_db
from utils.excel_to_code import excel_converter
from utils.config_manager import CONFIG_LOADER
import os

# 导入配置（会自动加载环境变量）
from core.config import GOOGLE_APPLICATION_CREDENTIALS


app = FastAPI(
    title="AI助手API",
    description="提供AI驱动的语音交互服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(device.router)
app.include_router(health.router)
app.include_router(speech.router)
app.include_router(navigation.router)
app.include_router(dashboard.router)

@app.on_event("startup")
def startup_event():
    print("🚀 [startup] 开始应用启动流程...")
    
    # 1. 初始化数据库
    print("📊 [startup] 初始化数据库...")
    try:
        init_db()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        # 数据库初始化失败不应该阻止应用启动，因为可能是数据库连接问题
    
    # 2. Excel转表
    print("📄 [startup] Excel转表...")
    results = excel_converter.convert_all_excel_files()
    if results:
        print(f"✅ 成功转换 {len(results)} 个Excel文件:")
        for excel_name, code_file in results.items():
            print(f"   📄 {excel_name}.xlsx -> {code_file}")
    else:
        print("ℹ️  没有需要转换的Excel文件")

    # 3. 重载配置
    reload_results = CONFIG_LOADER.reload_all_configs()
    if reload_results:
        print(f"✅ 成功重载 {len(reload_results)} 个配置:")
        for config_name, success in reload_results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {config_name}")
    else:
        print("ℹ️  没有需要重载的配置")

    # 4. 检查配置更新
    if not CONFIG_LOADER.check_all_configs_up_to_date()['all_up_to_date']:
        print("❌ 配置未更新，请检查Excel文件是否修改")
        exit(1)
    else:
        print("🎉 [startup] 应用启动流程完成！")

@app.get("/ping")
def ping():
    return {"message": "pong", "status": "healthy"}

@app.get("/")
def root():
    return {
        "message": "AI助手API服务",
        "version": "1.0.0",
        "docs": "/docs"
    } 