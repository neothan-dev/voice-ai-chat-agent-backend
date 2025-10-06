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
import pandas as pd
import json
import yaml
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import time
from loguru import logger
import re
from datetime import datetime

DESCRIBE_SHEET_NAME = ".DESC"

class ExcelToCodeConverter:

    """Excel到Python代码转换器"""
    
    def __init__(self, excel_dir: str = "dev/data/excel", code_dir: str = "dev/data/code"):
        self.excel_dir = Path(excel_dir)
        self.code_dir = Path(code_dir)
        self.excel_dir.mkdir(parents=True, exist_ok=True)
        self.code_dir.mkdir(parents=True, exist_ok=True)
        
        # 持久化修改时间到文件
        self.modified_times_file = Path("dev/data/convert_times.json")
        
        # 记录Excel文件和模块文件的修改时间
        self.excel_modified_time: Dict[str, float] = {}
        self.module_modified_time: Dict[str, float] = {}
        
        # 加载修改时间数据
        self._load_modified_times()
        
    def _load_modified_times(self) -> None:
        """从文件加载修改时间数据"""
        try:
            if self.modified_times_file.exists():
                with open(self.modified_times_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 跳过文件头部的注释
                    lines = content.split('\n')
                    json_start = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.strip().startswith('/*') and not line.strip().startswith('*') and not line.strip().startswith('*/'):
                            json_start = i
                            break
                    
                    json_content = '\n'.join(lines[json_start:])
                    data = json.loads(json_content)
                    
                    # 处理格式（包含excel和module时间）
                    if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()):
                        # 格式：{"config": {"excel": time, "module": time}}
                        for config_name, times in data.items():
                            if isinstance(times, dict):
                                self.excel_modified_time[config_name] = float(times.get('excel', 0))
                                self.module_modified_time[config_name] = float(times.get('module', 0))
        except Exception as e:
            logger.warning(f"加载修改时间文件失败: {e}")
    
    def _save_modified_times(self) -> None:
        """保存修改时间数据到文件"""
        try:
            self.modified_times_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 合并excel和module时间
            combined_data = {}
            for config_name in self.excel_modified_time:
                combined_data[config_name] = {
                    'excel': self.excel_modified_time[config_name],
                    'module': self.module_modified_time.get(config_name, 0)
                }
            
            with open(self.modified_times_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2)
        except Exception as e:
            logger.error(f"保存修改时间文件失败: {e}")
        
    def convert_all_excel_files(self) -> Dict[str, str]:
        """转换所有Excel文件"""
        results = {}
        
        for excel_file in self.excel_dir.glob("*.xlsx"):
            # 跳过临时文件
            if excel_file.name.startswith("~$") or excel_file.name.startswith(".~"):
                continue
            try:
                result = self.convert_excel_file(excel_file)
                if result:
                    results[excel_file.stem] = result
            except Exception as e:
                logger.error(f"转换Excel文件失败 {excel_file}: {e}")
        
        return results
    
    def convert_excel_file(self, excel_path: Path) -> Optional[str]:
        """转换单个Excel文件"""
        try:
            # 检查Excel文件和模块文件的修改时间
            excel_mtime = excel_path.stat().st_mtime
            module_file = self.code_dir / f"{excel_path.stem}_config.py"
            module_mtime = module_file.stat().st_mtime if module_file.exists() else 0
            
            # 获取上次记录的修改时间
            last_excel_mtime = self.excel_modified_time.get(excel_path.stem, 0)
            last_module_mtime = self.module_modified_time.get(excel_path.stem, 0)
            
            # 检查是否需要转换
            excel_changed = last_excel_mtime == 0 or excel_mtime > last_excel_mtime
            module_changed = not module_file.exists() or module_mtime > last_module_mtime
            
            if not excel_changed and not module_changed:
                logger.info(f"Excel文件和模块文件均未变化，跳过转换: {excel_path}")
                return None
            elif last_excel_mtime == 0:
                logger.info(f"首次转换，进行转换: {excel_path}")
            else:
                logger.info(f"文件已修改，需要转换: {excel_path} (Excel: {excel_mtime}, Module: {module_mtime}, Last Excel: {last_excel_mtime}, Last Module: {last_module_mtime})")
            
            # 先进行数据合法性检查
            if not self.validate_data_before_conversion(excel_path):
                raise ValueError(f"Excel文件数据不合法，无法转换: {excel_path}")
            
            # 读取Excel文件的所有sheet，不自动处理第一行作为header
            excel_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl', header=None)
            
            # 转换每个sheet
            converted_data = {}
            for sheet_name, df in excel_data.items():
                if sheet_name == DESCRIBE_SHEET_NAME:
                    continue
                if not df.empty:
                    sheet_data = self._convert_sheet_to_dict(df, sheet_name)
                    if sheet_data:
                        converted_data[sheet_name] = sheet_data
            
            if not converted_data:
                logger.warning(f"Excel文件没有有效数据: {excel_path}")
                return None
            
            # 生成Python代码
            code = self._generate_python_code(excel_path.stem, converted_data, excel_path)
            
            # 保存代码文件
            code_file = self.code_dir / f"{excel_path.stem}_config.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 更新修改时间
            self.excel_modified_time[excel_path.stem] = excel_mtime
            self.module_modified_time[excel_path.stem] = module_file.stat().st_mtime if module_file.exists() else 0
            self._save_modified_times()
            
            logger.info(f"成功转换Excel文件: {excel_path} -> {code_file}")
            return str(code_file)
            
        except Exception as e:
            logger.error(f"转换Excel文件失败 {excel_path}: {e}")
            return None
    
    def _convert_sheet_to_dict(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """将Excel sheet转换为字典"""
        if df.empty:
            return {}
        
        # 检查是否有足够的行（至少4行：列名、描述、类型、数据）
        if len(df) < 4:
            logger.warning(f"Sheet {sheet_name} 行数不足，至少需要4行（列名、描述、类型、数据）")
            return {}
        
        # 第一行：列名（作为字典的键）
        column_names = df.iloc[0].tolist()
        # 第二行：描述（跳过）
        # 第三行：类型定义
        type_definitions = df.iloc[2].tolist()
        
        # 从第四行开始是数据
        data_df = df.iloc[3:].copy()
        data_df.columns = column_names
        
        # 第一列作为键
        key_column = column_names[0]
        result = {}
        
        for _, row in data_df.iterrows():
            key = row[key_column]
            if pd.isna(key) or key == '':
                continue
                
            # 构建该键的属性字典
            item_data = {}
            for i, col in enumerate(column_names[1:], 1):  # 跳过第一列（键列）
                value = row[col]
                col_type = type_definitions[i] if i < len(type_definitions) else 'string'
                
                # 根据类型定义处理值
                processed_value = self._process_value_by_type(value, col_type)
                item_data[col] = processed_value
            
            result[key] = item_data
        
        return result
    
    def _process_value_by_type(self, value: Any, col_type: str) -> Any:
        """根据类型定义处理值"""
        if pd.isna(value):
            return None
            
        col_type = str(col_type).strip().lower()
        
        if col_type == 'string':
            return str(value).strip()
        elif col_type == 'int':
            try:
                return int(value)
            except:
                return 0
        elif col_type == 'float':
            try:
                return float(value)
            except:
                return 0.0
        elif col_type == 'bool':
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', '是']
            return bool(value)
        elif col_type == 'list':
            return self._parse_list_value(value)
        elif col_type == 'json':
            return self._parse_json_value(value)
        elif col_type == 'yaml':
            return self._parse_yaml_value(value)
        else:
            # 默认作为字符串处理
            return str(value).strip()
    
    def _parse_list_value(self, value: Any) -> List[Any]:
        """解析列表值，支持 [a, b, c] 格式"""
        if isinstance(value, str):
            value = value.strip()
            # 检查是否是 [a, b, c] 格式
            if value.startswith('[') and value.endswith(']'):
                try:
                    # 提取括号内的内容
                    content = value[1:-1].strip()
                    if not content:  # 空列表
                        return []
                    
                    # 分割并清理
                    items = [item.strip() for item in content.split(',')]
                    # 尝试转换为数字
                    result = []
                    for item in items:
                        try:
                            if '.' in item:
                                result.append(float(item))
                            else:
                                result.append(int(item))
                        except:
                            result.append(item)
                    return result
                except:
                    pass
            
            # 兼容旧的逗号分隔格式
            if ',' in value:
                items = [item.strip() for item in value.split(',')]
                result = []
                for item in items:
                    try:
                        if '.' in item:
                            result.append(float(item))
                        else:
                            result.append(int(item))
                    except:
                        result.append(item)
                return result
        
        # 如果不是字符串，尝试转换为列表
        if isinstance(value, (list, tuple)):
            return list(value)
        
        return [str(value)]
    
    def _parse_json_value(self, value: Any) -> Any:
        """解析JSON值"""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith('{') and value.endswith('}'):
                try:
                    return json.loads(value)
                except:
                    pass
        return value
    
    def _parse_yaml_value(self, value: Any) -> Any:
        """解析YAML值"""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith('-') or ':' in value:
                try:
                    return yaml.safe_load(value)
                except:
                    pass
        return value
    
    def _parse_structured_value(self, value: str) -> Any:
        """解析结构化值（JSON、YAML、列表等）"""
        value = value.strip()
        
        # 尝试解析JSON
        if value.startswith('{') and value.endswith('}'):
            try:
                return json.loads(value)
            except:
                pass
        
        # 尝试解析YAML
        if value.startswith('-') or ':' in value:
            try:
                return yaml.safe_load(value)
            except:
                pass
        
        # 尝试解析列表（逗号分隔）
        if ',' in value and not value.startswith('{'):
            try:
                items = [item.strip() for item in value.split(',')]
                # 尝试转换为数字
                numeric_items = []
                for item in items:
                    try:
                        if '.' in item:
                            numeric_items.append(float(item))
                        else:
                            numeric_items.append(int(item))
                    except:
                        numeric_items.append(item)
                return numeric_items
            except:
                pass
        
        # 尝试解析布尔值
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        return value
    
    def _generate_python_code(self, config_name: str, data: Dict[str, Dict[str, Any]], excel_path: Path) -> str:
        """生成Python代码"""
        
        # 生成便捷访问函数
        access_functions = []
        for sheet_name in data.keys():
            sheet_var_name = f"{config_name.upper()}_{sheet_name.upper()}_CONFIG"
            access_functions.append(f"""
def get_{config_name}_{sheet_name}_item(key: str) -> dict:
    \"\"\"获取{config_name}_{sheet_name}配置项\"\"\"
    return {sheet_var_name}.get(key, {{}})

def get_{config_name}_{sheet_name}_all() -> dict:
    \"\"\"获取所有{config_name}_{sheet_name}配置\"\"\"
    return {sheet_var_name}

def get_{config_name}_{sheet_name}_keys() -> list:
    \"\"\"获取所有{config_name}_{sheet_name}键\"\"\"
    return list({sheet_var_name}.keys())
""")
        
        # 生成代码
        code = f'''"""
Auto-generated config file for {config_name}
Generated at: {datetime.now().isoformat()}
Source: {excel_path}
"""

'''
        
        # 为每个sheet生成配置字典
        for sheet_name, sheet_data in data.items():
            sheet_var_name = f"{config_name.upper()}_{sheet_name.upper()}_CONFIG"
            # 使用Python字典表示而不是JSON序列化
            sheet_dict_str = self._dict_to_python_str(sheet_data)
            code += f"{sheet_var_name} = {sheet_dict_str}\n\n"
        
        # 添加便捷访问函数
        code += "# 便捷访问函数\n"
        for func in access_functions:
            code += func
        
        return code
    
    def _dict_to_python_str(self, data: Any, indent: int = 0) -> str:
        """将字典转换为Python字符串表示"""
        if isinstance(data, dict):
            if not data:
                return "{}"
            
            items = []
            for key, value in data.items():
                # 处理键名中的特殊字符
                key_str = self._escape_string(key) if isinstance(key, str) else str(key)
                value_str = self._dict_to_python_str(value, indent + 2)
                items.append(f"{' ' * (indent + 2)}{key_str}: {value_str}")
            
            return "{\n" + ",\n".join(items) + "\n" + " " * indent + "}"
        
        elif isinstance(data, list):
            if not data:
                return "[]"
            
            items = []
            for item in data:
                item_str = self._dict_to_python_str(item, indent + 2)
                items.append(" " * (indent + 2) + item_str)
            
            return "[\n" + ",\n".join(items) + "\n" + " " * indent + "]"
        
        elif isinstance(data, bool):
            return "True" if data else "False"
        
        elif isinstance(data, str):
            return self._escape_string(data)
        
        else:
            return str(data)
    
    def _escape_string(self, s: str) -> str:
        """转义字符串中的特殊字符"""
        # 转义双引号
        s = s.replace('"', '\\"')
        # 转义反斜杠
        s = s.replace('\\', '\\\\')
        # 转义换行符
        s = s.replace('\n', '\\n')
        # 转义回车符
        s = s.replace('\r', '\\r')
        # 转义制表符
        s = s.replace('\t', '\\t')
        
        return f'"{s}"'
    
    def watch_and_convert(self, interval: int = 2) -> None:
        """监控Excel文件变化并自动转换"""
        logger.info(f"开始监控Excel文件变化，检查间隔: {interval}秒")
        
        while True:
            try:
                for excel_file in self.excel_dir.glob("*.xlsx"):
                    # 跳过临时文件
                    if excel_file.name.startswith("~$") or excel_file.name.startswith(".~"):
                        continue
                    
                    # 检查Excel文件和模块文件的修改时间
                    excel_mtime = excel_file.stat().st_mtime
                    module_file = self.code_dir / f"{excel_file.stem}_config.py"
                    module_mtime = module_file.stat().st_mtime if module_file.exists() else 0
                    last_excel_mtime = self.excel_modified_time.get(excel_file.stem, 0)
                    
                    # 如果Excel文件或模块文件比上次转换时间新，则需要转换
                    if last_excel_mtime == 0 or excel_mtime > last_excel_mtime or module_mtime > last_excel_mtime:
                        logger.info(f"检测到文件变化，需要转换: {excel_file}")
                        self.convert_excel_file(excel_file)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("停止监控Excel文件")
                break
            except Exception as e:
                logger.error(f"监控Excel文件时出错: {e}")
                time.sleep(interval)
    
    def create_template_excel(self, config_name: str, sheets: List[str], sample_data: Optional[Dict[str, Dict[str, List[Any]]]] = None, types_map: Optional[dict] = None) -> str:
        """创建模板Excel文件，支持类型定义映射"""
        excel_path = self.excel_dir / f"{config_name}.xlsx"
        if sample_data is None:
            sample_data = {
                'main': {
                    'key': ['example_key_1', 'example_key_2'],
                    'value': ['example_value_1', 'example_value_2'],
                    'description': ['示例描述1', '示例描述2']
                }
            }
        if types_map is None:
            types_map = {}
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name in sheets:
                if sheet_name in sample_data:
                    sample = sample_data[sheet_name]
                    columns = list(sample.keys())
                    column_names = columns
                    descriptions = [f"{col}的描述" for col in columns]
                    # 类型定义优先用types_map
                    if sheet_name in types_map:
                        types = types_map[sheet_name]
                    else:
                        types = ['string'] * len(columns)
                    data_rows = []
                    max_rows = max(len(v) for v in sample.values()) if sample.values() else 0
                    for i in range(max_rows):
                        row = []
                        for col in columns:
                            if i < len(sample[col]):
                                row.append(sample[col][i])
                            else:
                                row.append('')
                        data_rows.append(row)
                    all_data = [column_names, descriptions, types] + data_rows
                    df = pd.DataFrame(all_data)
                else:
                    column_names = ['key', 'value', 'description']
                    descriptions = ['键名', '值', '描述']
                    types = ['string', 'string', 'string']
                    data_rows = [
                        ['example_key_1', 'example_value_1', '示例描述1'],
                        ['example_key_2', 'example_value_2', '示例描述2']
                    ]
                    all_data = [column_names, descriptions, types] + data_rows
                    df = pd.DataFrame(all_data)
                df.to_excel(writer, index=False, header=False, sheet_name=sheet_name)
            # 添加说明sheet
            instructions = pd.DataFrame({
                'key': [
                    'Excel格式说明',
                    '第一行：列名',
                    '第二行：描述（可选）',
                    '第三行：类型定义',
                    '第四行开始：数据',
                    '支持的数据类型',
                    'string类型',
                    'int类型',
                    'float类型',
                    'bool类型',
                    'list类型',
                    'json类型',
                    'yaml类型',
                    '列表格式要求',
                    'JSON格式要求',
                    'YAML格式要求'
                ],
                'description': [
                    'Excel文件格式说明',
                    '第一行必须是列名，作为字典的键',
                    '第二行是描述，不参与转换',
                    '第三行定义每列的数据类型',
                    '从第四行开始是实际数据',
                    'string, int, float, bool, list, json, yaml',
                    '字符串类型，支持任意文本',
                    '整数类型，如：123',
                    '浮点数类型，如：123.45',
                    '布尔类型，如：true/false/1/0/yes/no/是/否',
                    '列表类型，格式：[a, b, c]',
                    'JSON对象类型，格式：{"key": "value"}',
                    'YAML格式，如：- item1\\n- item2',
                    '必须用中括号包围，如：[a, b, c]',
                    '必须用大括号包围，如：{"key": "value"}',
                    '支持YAML语法，如：- item1\\n- item2'
                ]
            })
            instructions.to_excel(writer, index=False, header=False, sheet_name=DESCRIBE_SHEET_NAME)
        logger.info(f"已创建模板Excel文件: {excel_path}")
        return str(excel_path)
    
    def validate_excel_file(self, excel_path: Path) -> Dict[str, Any]:
        """验证Excel文件"""
        try:
            excel_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl', header=None)
            
            validation_result = {
                'file_name': excel_path.name,
                'total_sheets': len(excel_data),
                'sheets': {},
                'errors': [],
                'warnings': []
            }
            
            # 检查文件基本信息
            if not excel_path.exists():
                validation_result['errors'].append("文件不存在")
                return validation_result
            
            if excel_path.stat().st_size == 0:
                validation_result['errors'].append("文件为空")
                return validation_result
            
            # 检查是否有有效的sheet
            valid_sheets = 0
            for sheet_name, df in excel_data.items():
                if sheet_name == DESCRIBE_SHEET_NAME:
                    continue
                sheet_result = self._validate_sheet(df, sheet_name)
                validation_result['sheets'][sheet_name] = sheet_result
                
                if not sheet_result['errors']:
                    valid_sheets += 1
                
                if sheet_result['errors']:
                    validation_result['errors'].extend([f"{sheet_name}: {e}" for e in sheet_result['errors']])
                if sheet_result['warnings']:
                    validation_result['warnings'].extend([f"{sheet_name}: {w}" for w in sheet_result['warnings']])
            
            # 检查是否有至少一个有效sheet
            if valid_sheets == 0:
                validation_result['errors'].append("没有有效的sheet")
            
            # 检查sheet名称合法性
            for sheet_name in excel_data.keys():
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', sheet_name) and sheet_name != DESCRIBE_SHEET_NAME:
                    validation_result['warnings'].append(f"Sheet名称 '{sheet_name}' 包含特殊字符")
                
                if len(sheet_name) > 30:
                    validation_result['warnings'].append(f"Sheet名称 '{sheet_name}' 过长")
            
            return validation_result
            
        except Exception as e:
            return {
                'file_name': excel_path.name,
                'error': str(e),
                'errors': [str(e)],
                'warnings': []
            }
    
    def validate_data_before_conversion(self, excel_path: Path) -> bool:
        """转换前进行数据合法性检查"""
        try:
            validation_result = self.validate_excel_file(excel_path)
            
            # 如果有错误，记录并返回False
            if validation_result.get('errors'):
                logger.error(f"数据验证失败 {excel_path}:")
                for error in validation_result['errors']:
                    logger.error(f"  ❌ {error}")
                return False
            
            # 如果有警告，记录但不阻止转换
            if validation_result.get('warnings'):
                logger.warning(f"数据验证警告 {excel_path}:")
                for warning in validation_result['warnings']:
                    logger.warning(f"  ⚠️  {warning}")
            
            logger.info(f"✅ 数据验证通过: {excel_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据验证异常 {excel_path}: {e}")
            return False
    
    def _validate_sheet(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """验证单个sheet"""
        result = {
            'sheet_name': sheet_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'errors': [],
            'warnings': []
        }
        
        if df.empty:
            result['errors'].append("Sheet为空")
            return result
        
        # 检查是否有足够的行（至少4行：列名、描述、类型、数据）
        if len(df) < 4:
            result['errors'].append("至少需要4行：列名、描述、类型、数据")
            return result
        
        # 检查列数
        if len(df.columns) < 2:
            result['errors'].append("至少需要2列：键列和值列")
            return result
        
        # 第一行：列名
        column_names = df.iloc[0].tolist()
        # 第二行：描述（跳过）
        # 第三行：类型定义
        type_definitions = df.iloc[2].tolist()
        
        # 从第四行开始是数据
        data_df = df.iloc[3:].copy()
        data_df.columns = column_names
        
        # 检查第一列（键列）
        key_column = column_names[0]
        keys = data_df[key_column].dropna()
        
        # 检查空键
        empty_keys = keys[keys.astype(str).str.strip() == '']
        if not empty_keys.empty:
            result['errors'].append(f"发现空键: {len(empty_keys)}个")
        
        # 检查重复键
        duplicate_keys = keys[keys.duplicated()]
        if not duplicate_keys.empty:
            result['errors'].append(f"发现重复键: {duplicate_keys.unique().tolist()}")
        
        # 检查键的合法性
        for idx, key in keys.items():
            key_str = str(key).strip()
            if not key_str:
                continue
            
            # 检查键是否包含特殊字符（允许数字开头的键，因为字典键不需要是有效的Python变量名）
            if not re.match(r'^[a-zA-Z0-9_]+$', key_str):
                result['warnings'].append(f"键 '{key_str}' 包含特殊字符，可能影响数据访问")
            
            # 检查键长度
            if len(key_str) > 50:
                result['warnings'].append(f"键 '{key_str}' 过长（{len(key_str)}字符）")
        
        # 检查键列类型声明
        key_column_type = type_definitions[0] if len(type_definitions) > 0 else None
        if pd.isna(key_column_type):
            result['errors'].append("键列缺少类型声明")
        else:
            key_type_str = str(key_column_type).strip().lower()
            valid_key_types = ['string', 'int']
            if key_type_str not in valid_key_types:
                result['errors'].append(f"键列类型 '{key_type_str}' 不是有效类型，键列只支持: {valid_key_types}")
        
        # 检查其他列的类型定义
        valid_types = ['string', 'int', 'float', 'bool', 'list', 'json', 'yaml']
        for i, col_type in enumerate(type_definitions[1:], 1):  # 跳过第一列
            if pd.isna(col_type):
                result['warnings'].append(f"列 {i} 缺少类型定义")
                continue
                
            col_type_str = str(col_type).strip().lower()
            if col_type_str not in valid_types:
                result['warnings'].append(f"列 {i} 类型 '{col_type_str}' 不是有效类型，有效类型: {valid_types}")
        
        # 检查数据类型和内容
        for i, col in enumerate(column_names[1:], 1):  # 跳过第一列（键列）
            col_errors = []
            col_warnings = []
            col_type = type_definitions[i] if i < len(type_definitions) else 'string'
            
            for idx, value in data_df[col].items():
                if pd.isna(value):
                    continue
                
                # 根据类型定义验证值
                validation_result = self._validate_value_by_type(value, col_type, idx + 4)  # +4 因为数据从第4行开始
                col_errors.extend(validation_result['errors'])
                col_warnings.extend(validation_result['warnings'])
            
            if col_errors:
                result['errors'].extend([f"列 '{col}': {e}" for e in col_errors])
            if col_warnings:
                result['warnings'].extend([f"列 '{col}': {w}" for w in col_warnings])
        
        # 检查数据完整性
        total_cells = len(data_df) * len(column_names)
        empty_cells = data_df.isna().sum().sum()
        if empty_cells > total_cells * 0.8:  # 80%以上为空
            result['warnings'].append(f"数据稀疏度较高（{empty_cells}/{total_cells} 空单元格）")
        
        return result
    
    def _validate_value_by_type(self, value: Any, col_type: str, row_num: int) -> Dict[str, List[str]]:
        """根据类型定义验证值"""
        result = {'errors': [], 'warnings': []}
        
        if pd.isna(value):
            return result
            
        col_type = str(col_type).strip().lower()
        
        if col_type == 'string':
            if not isinstance(value, str):
                result['warnings'].append(f"行 {row_num}: 期望字符串类型，实际为 {type(value)}")
            else:
                if len(value) > 1000:
                    result['warnings'].append(f"行 {row_num}: 字符串过长（{len(value)}字符）")
                
                # 检查是否包含特殊字符
                if '\x00' in value or '\x01' in value or '\x02' in value:
                    result['errors'].append(f"行 {row_num}: 包含控制字符")
                
                # 检查编码问题
                try:
                    value.encode('utf-8')
                except UnicodeEncodeError:
                    result['errors'].append(f"行 {row_num}: 编码问题")
                    
        elif col_type == 'int':
            try:
                int(value)
            except (ValueError, TypeError):
                result['errors'].append(f"行 {row_num}: 无法转换为整数")
            else:
                int_val = int(value)
                if int_val < -2**31 or int_val > 2**31 - 1:
                    result['warnings'].append(f"行 {row_num}: 整数超出范围")
                    
        elif col_type == 'float':
            try:
                float(value)
            except (ValueError, TypeError):
                result['errors'].append(f"行 {row_num}: 无法转换为浮点数")
            else:
                float_val = float(value)
                if float_val < -1e308 or float_val > 1e308:
                    result['warnings'].append(f"行 {row_num}: 浮点数超出范围")
                    
        elif col_type == 'bool':
            if isinstance(value, str):
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no', '是', '否']:
                    result['warnings'].append(f"行 {row_num}: 布尔值格式不规范")
                    
        elif col_type == 'list':
            if isinstance(value, str):
                value = value.strip()
                # 检查是否是 [a, b, c] 格式
                if not (value.startswith('[') and value.endswith(']')):
                    result['warnings'].append(f"行 {row_num}: 列表格式应为 [a, b, c]，当前格式: {value}")
                else:
                    # 验证列表内容
                    try:
                        content = value[1:-1].strip()
                        if content:  # 非空列表
                            items = [item.strip() for item in content.split(',')]
                            if not items:
                                result['warnings'].append(f"行 {row_num}: 列表格式错误")
                    except:
                        result['errors'].append(f"行 {row_num}: 列表格式解析失败")
                        
        elif col_type == 'json':
            if isinstance(value, str):
                value = value.strip()
                if not (value.startswith('{') and value.endswith('}')):
                    result['warnings'].append(f"行 {row_num}: JSON格式应为 {{key: value}}，当前格式: {value}")
                else:
                    try:
                        json.loads(value)
                    except:
                        result['errors'].append(f"行 {row_num}: JSON格式解析失败")
                        
        elif col_type == 'yaml':
            if isinstance(value, str):
                value = value.strip()
                if not (value.startswith('-') or ':' in value):
                    result['warnings'].append(f"行 {row_num}: YAML格式不规范")
                else:
                    try:
                        yaml.safe_load(value)
                    except:
                        result['errors'].append(f"行 {row_num}: YAML格式解析失败")
        
        return result

# 全局转换器实例
excel_converter = ExcelToCodeConverter() 