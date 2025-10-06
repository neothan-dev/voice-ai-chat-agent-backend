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

import os
import sys
import json
import importlib
import importlib.util
from typing import Dict, Any, List, Optional
from pathlib import Path
import time
from loguru import logger
from .excel_to_code import excel_converter

class ConfigManager:
    """通用配置管理器"""
    
    def __init__(self, code_dir: str = "dev/data/code"):
        self.code_dir = Path(code_dir)
        self.code_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_modules: Dict[str, Any] = {}
        # 内存中的重载时间记录（不持久化）
        self.last_modified: Dict[str, float] = {}
    
    def _load_config_module(self, code_file: Path, config_name: str) -> Optional[Any]:
        """加载配置模块"""
        try:
            # 检查文件是否被修改
            current_mtime = code_file.stat().st_mtime
            if config_name in self.last_modified and current_mtime <= self.last_modified[config_name]:
                # logger.info(f"配置文件未变化，跳过重载: {code_file}")
                return self.loaded_modules.get(config_name)
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(f"config_{config_name}", code_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 缓存模块和修改时间（仅内存）
            self.loaded_modules[config_name] = module
            self.last_modified[config_name] = current_mtime
            
            logger.info(f"成功加载配置模块: {config_name}")
            return module
            
        except Exception as e:
            logger.error(f"加载配置模块失败 {code_file}: {e}")
            return None
    
    def reload_config(self, config_name: str, check_excel_modified: bool = True) -> bool:
        """重新加载指定配置，会检查当前module对应的excel文件是否修改"""
        try:
            if check_excel_modified:
                # 重新转换Excel
                excel_file = excel_converter.excel_dir / f"{config_name}.xlsx"
                if excel_file.exists():
                # 只在Excel文件真正修改时才转换
                    current_mtime = excel_file.stat().st_mtime
                    if config_name not in excel_converter.excel_modified_time or current_mtime > excel_converter.excel_modified_time[config_name]:
                        excel_converter.convert_excel_file(excel_file)
            
            # 重新加载配置模块
            code_file = self.code_dir / f"{config_name}_config.py"
            if code_file.exists():
                module = self._load_config_module(code_file, config_name)
                return module is not None
            
            return False
        except Exception as e:
            logger.error(f"重新加载配置失败 {config_name}: {e}")
            return False

    
    def get_config(self, config_name: str, auto_reload: bool = True) -> Optional[Any]:
        """获取配置模块"""
        if auto_reload:
            self.reload_config(config_name)
        
        return self.loaded_modules.get(config_name)
    
    def get_config_value(self, config_name: str, sheet_name: str, key, auto_reload: bool = True) -> Optional[Any]:
        config_sheet = self.get_config_sheet(config_name, sheet_name, auto_reload)

        return config_sheet and config_sheet.get(key)
    
    def get_config_sheet(self, config_name: str, sheet_name: str, auto_reload: bool = True) -> Optional[Dict[str, Any]]:
        """获取配置sheet"""
        module = self.get_config(config_name, auto_reload)
        if not module:
            return None
        
        # 构建变量名
        var_name = f"{config_name.upper()}_{sheet_name.upper()}_CONFIG"
        if hasattr(module, var_name):
            return getattr(module, var_name)
        
        return None
    
    def reload_all_configs(self, convert_all_excel_first: bool = False, check_excel_modified: bool = True) -> Dict[str, bool]:
        """重新加载所有配置"""
        results = {}
        
        if convert_all_excel_first:
            excel_converter.convert_all_excel_files()
        
        # 重新加载所有配置模块
        for code_file in self.code_dir.glob("*_config.py"):
            # 只删除最后一个_config，避免文件名中包含_config时的问题
            config_name = code_file.stem
            if config_name.endswith("_config"):
                config_name = config_name[:-7]  # 删除最后的"_config"

            result = self.reload_config(config_name, check_excel_modified)
            if result:
                results[config_name] = result
        
        return results
    
    def list_configs(self) -> List[str]:
        """列出所有配置"""
        configs = []
        for code_file in self.code_dir.glob("*_config.py"):
            # 只删除最后一个_config，避免文件名中包含_config时的问题
            config_name = code_file.stem
            if config_name.endswith("_config"):
                config_name = config_name[:-7]  # 删除最后的"_config"
            configs.append(config_name)
        return configs
    
    def list_sheets(self, config_name: str) -> List[str]:
        """列出配置的所有sheet"""
        module = self.get_config(config_name)
        if not module:
            return []
        
        sheets = []
        for attr_name in dir(module):
            if attr_name.endswith("_CONFIG") and attr_name.startswith(config_name.upper()):
                # 精确删除前缀和后缀，避免sheet名称中包含_CONFIG或配置名称时的问题
                prefix = f"{config_name.upper()}_"
                if attr_name.startswith(prefix):
                    sheet_name = attr_name[len(prefix):]  # 删除前缀
                else:
                    sheet_name = attr_name
                
                if sheet_name.endswith("_CONFIG"):
                    sheet_name = sheet_name[:-7]  # 删除最后的"_CONFIG"
                
                sheets.append(sheet_name)
        
        return sheets
    
    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """验证配置"""
        try:
            # 验证Excel文件
            excel_file = excel_converter.excel_dir / f"{config_name}.xlsx"
            if not excel_file.exists():
                return {
                    'config_name': config_name,
                    'error': 'Excel文件不存在',
                    'valid': False
                }
            
            validation_result = excel_converter.validate_excel_file(excel_file)
            
            # 检查生成的代码文件
            code_file = self.code_dir / f"{config_name}_config.py"
            if not code_file.exists():
                validation_result['errors'].append('生成的代码文件不存在')
            
            validation_result['valid'] = len(validation_result['errors']) == 0
            return validation_result
            
        except Exception as e:
            return {
                'config_name': config_name,
                'error': str(e),
                'valid': False
            }
    
    def check_all_configs_up_to_date(self) -> Dict[str, Any]:
        """检查所有配置是否都是最新的"""
        result = {
            "all_up_to_date": True,
            "total_configs": 0,
            "up_to_date_configs": 0,
            "outdated_configs": [],
            "missing_excel_files": [],
            "missing_code_files": [],
            "details": {}
        }
        
        try:
            # 获取所有Excel文件
            excel_files = []
            for excel_file in excel_converter.excel_dir.glob("*.xlsx"):
                # 跳过临时文件
                if excel_file.name.startswith("~$") or excel_file.name.startswith(".~"):
                    continue
                excel_files.append(excel_file)
            result["total_configs"] = len(excel_files)
            
            for excel_file in excel_files:
                config_name = excel_file.stem
                result["details"][config_name] = {
                    "excel_file": str(excel_file),
                    "excel_mtime": excel_file.stat().st_mtime,
                    "code_file": None,
                    "code_mtime": None,
                    "last_converted": None,
                    "up_to_date": False,
                    "status": "unknown"
                }
                
                # 检查代码文件
                code_file = self.code_dir / f"{config_name}_config.py"
                if code_file.exists():
                    result["details"][config_name]["code_file"] = str(code_file)
                    result["details"][config_name]["code_mtime"] = code_file.stat().st_mtime
                else:
                    result["details"][config_name]["status"] = "missing_code_file"
                    result["missing_code_files"].append(config_name)
                    result["all_up_to_date"] = False
                    continue
                
                # 检查转换时间和内存重载时间
                excel_mtime = excel_file.stat().st_mtime
                code_mtime = code_file.stat().st_mtime
                last_excel_mtime = excel_converter.excel_modified_time.get(config_name, 0)
                last_module_mtime = excel_converter.module_modified_time.get(config_name, 0)
                last_reload_time = self.last_modified.get(config_name, 0)
                
                result["details"][config_name]["last_converted"] = last_excel_mtime
                result["details"][config_name]["last_module_time"] = last_module_mtime
                result["details"][config_name]["last_reload_time"] = last_reload_time
                
                # 判断是否最新（检查Excel转换、模块生成和内存重载）
                excel_changed = last_excel_mtime == 0 or excel_mtime > last_excel_mtime
                module_changed = not code_file.exists() or code_mtime > last_module_mtime
                reload_needed = last_reload_time == 0 or code_mtime > last_reload_time
                
                if not excel_changed and not module_changed and not reload_needed:
                    result["details"][config_name]["up_to_date"] = True
                    result["details"][config_name]["status"] = "up_to_date"
                    result["up_to_date_configs"] += 1
                else:
                    result["details"][config_name]["up_to_date"] = False
                    result["details"][config_name]["status"] = "outdated"
                    result["details"][config_name]["excel_changed"] = excel_changed
                    result["details"][config_name]["module_changed"] = module_changed
                    result["details"][config_name]["reload_needed"] = reload_needed
                    result["outdated_configs"].append(config_name)
                    result["all_up_to_date"] = False
            
            # 检查是否有孤立的代码文件（没有对应的Excel文件）
            for code_file in self.code_dir.glob("*_config.py"):
                # 只删除最后一个_config，避免文件名中包含_config时的问题
                config_name = code_file.stem
                if config_name.endswith("_config"):
                    config_name = config_name[:-7]  # 删除最后的"_config"
                excel_file = excel_converter.excel_dir / f"{config_name}.xlsx"
                if not excel_file.exists():
                    result["details"][config_name] = {
                        "excel_file": None,
                        "code_file": str(code_file),
                        "status": "orphaned_code_file"
                    }
                    result["all_up_to_date"] = False
            
        except Exception as e:
            result["error"] = str(e)
            result["all_up_to_date"] = False
            
        return result
    
    def watch_and_reload(self, interval: int = 2) -> None:
        """监控配置变化并自动重载"""
        logger.info(f"开始监控配置变化，检查间隔: {interval}秒")
        
        while True:
            try:
                # 检查Excel文件变化
                for excel_file in excel_converter.excel_dir.glob("*.xlsx"):
                    # 跳过临时文件
                    if excel_file.name.startswith("~$") or excel_file.name.startswith(".~"):
                        continue
                    current_mtime = excel_file.stat().st_mtime
                    config_name = excel_file.stem
                    
                    if config_name not in excel_converter.excel_modified_time or current_mtime > excel_converter.excel_modified_time[config_name]:
                        logger.info(f"检测到Excel文件变化: {excel_file}")
                        excel_converter.convert_excel_file(excel_file)
                        self.reload_config(config_name)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("停止监控配置变化")
                break
            except Exception as e:
                logger.error(f"监控配置变化时出错: {e}")
                time.sleep(interval)

# 全局配置管理器实例
config_manager = ConfigManager()

class ConfigLoader:
    def __init__(self):
        self.config_manager = config_manager
    
    def get_config(self, config_name: str):
        return self.config_manager.get_config(config_name)
    
    def get_config_value(self, config_name: str, sheet_name: str, key):
        return self.config_manager.get_config_value(config_name, sheet_name, key)
    
    def get_config_sheet(self, config_name: str, sheet_name: str):
        return self.config_manager.get_config_sheet(config_name, sheet_name)
    
    def reload_config(self, config_name: str):
        return self.config_manager.reload_config(config_name)
    
    def reload_all_configs(self, bConvertAllExcelFirst: bool = False):
        return self.config_manager.reload_all_configs(bConvertAllExcelFirst)
    
    def list_configs(self):
        return self.config_manager.list_configs()
    
    def list_sheets(self, config_name: str):
        return self.config_manager.list_sheets(config_name)
    
    def validate_config(self, config_name: str):
        return self.config_manager.validate_config(config_name)
    
    def check_all_configs_up_to_date(self):
        return self.config_manager.check_all_configs_up_to_date()
    
    def start_config_watch(self, interval: int = 2):
        return self.config_manager.watch_and_reload(interval)

CONFIG_LOADER = ConfigLoader() 