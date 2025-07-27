import os
import sys
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# 数据文件路径配置
DATA_DIR = 'data'
STUDENTS_FILE = 'students.csv'
SCORE_EVENTS_FILE = 'score_events.csv'
SETTINGS_FILE = 'settings.json'
SCORE_RULES_FILE = 'score_rules.csv'

# 新增数据文件路径配置
REWARD_EVENTS_FILE = 'reward_events.csv'
REWARD_RULES_FILE = 'reward_rules.csv'
DAILY_TASK_RULES_FILE = 'daily_task_rules.csv'
DAILY_TASK_EVENTS_FILE = 'daily_task_events.csv'
SCORE_EVENTS_DIR = 'score_events'  # 积分事件按天存储的目录

def get_data_dir():
    """获取数据目录路径，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # 如果是PyInstaller打包的exe
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是普通Python脚本
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    data_path = os.path.join(application_path, DATA_DIR)
    os.makedirs(data_path, exist_ok=True)
    return data_path

def get_file_path(filename, is_score_event=False):
    """获取数据文件的完整路径"""
    if is_score_event:
        return os.path.join(get_data_dir(), SCORE_EVENTS_DIR, filename)
    return os.path.join(get_data_dir(), filename)
def init_db():
    """初始化数据文件"""
    data_dir = get_data_dir()
    
    # 初始化学生文件
    students_file = get_file_path(STUDENTS_FILE)
    if not os.path.exists(students_file):
        with open(students_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'name', 'current_score'])
    
    # 初始化积分事件目录
    score_events_dir_path = os.path.join(data_dir, SCORE_EVENTS_DIR)
    os.makedirs(score_events_dir_path, exist_ok=True)

    # 初始化兑换事件文件
    reward_events_file = get_file_path(REWARD_EVENTS_FILE)
    if not os.path.exists(reward_events_file):
        with open(reward_events_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'reward_name', 'score_cost', 'timestamp'])

    # 初始化兑换规则文件
    reward_rules_file = get_file_path(REWARD_RULES_FILE)
    if not os.path.exists(reward_rules_file):
        with open(reward_rules_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['rule_name', 'score_cost'])

    # 初始化每日任务规则文件
    daily_task_rules_file = get_file_path(DAILY_TASK_RULES_FILE)
    if not os.path.exists(daily_task_rules_file):
        with open(daily_task_rules_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['task_name', 'score_value'])

    # 初始化每日任务事件文件
    daily_task_events_file = get_file_path(DAILY_TASK_EVENTS_FILE)
    if not os.path.exists(daily_task_events_file):
        with open(daily_task_events_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'task_name', 'score_change', 'timestamp'])
    
    # 初始化设置文件
    settings_file = get_file_path(SETTINGS_FILE)
    if not os.path.exists(settings_file):
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    # 初始化积分规则文件
    rules_file = get_file_path(SCORE_RULES_FILE)
    if not os.path.exists(rules_file):
        with open(rules_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['rule_name', 'score_value'])

# 学生相关函数
def add_student(student_id: str, name: str = "") -> bool:
    """添加学生"""
    try:
        # 检查学生是否已存在
        if get_student_by_id(student_id):
            return False
        
        students_file = get_file_path(STUDENTS_FILE)
        with open(students_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, name, 0])
        return True
    except Exception as e:
        print(f"添加学生失败: {e}")
        return False

def get_all_students() -> List[Tuple[str, str, int]]:
    """获取所有学生信息"""
    try:
        students_file = get_file_path(STUDENTS_FILE)
        students = []
        
        if not os.path.exists(students_file):
            return students
            
        with open(students_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 3:
                    student_id, name, current_score = row[0], row[1], int(row[2])
                    students.append((student_id, name, current_score))
        
        return students
    except Exception as e:
        print(f"获取学生列表失败: {e}")
        return []

def get_student_by_id(student_id: str) -> Optional[Tuple[str, str, int]]:
    """根据学号获取学生信息"""
    students = get_all_students()
    for sid, name, score in students:
        if sid == student_id:
            return (sid, name, score)
    return None

def update_student_name(student_id: str, new_name: str) -> bool:
    """更新学生姓名"""
    try:
        students = get_all_students()
        updated = False
        
        for i, (sid, name, score) in enumerate(students):
            if sid == student_id:
                students[i] = (sid, new_name, score)
                updated = True
                break
        
        if updated:
            _save_all_students(students)
        
        return updated
    except Exception as e:
        print(f"更新学生姓名失败: {e}")
        return False

def delete_student(student_id: str) -> bool:
    """删除学生"""
    try:
        students = get_all_students()
        original_count = len(students)
        students = [(sid, name, score) for sid, name, score in students if sid != student_id]
        
        if len(students) < original_count:
            _save_all_students(students)
            # 同时删除该学生的所有积分记录
            _delete_student_score_events(student_id)
            return True
        
        return False
    except Exception as e:
        print(f"删除学生失败: {e}")
        return False

def _save_all_students(students: List[Tuple[str, str, int]]):
    """保存所有学生信息到文件"""
    students_file = get_file_path(STUDENTS_FILE)
    with open(students_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['student_id', 'name', 'current_score'])
        for student_id, name, score in students:
            writer.writerow([student_id, name, score])

def update_student_score(student_id: str, new_score: int) -> bool:
    """更新学生当前积分"""
    try:
        students = get_all_students()
        updated = False
        
        for i, (sid, name, score) in enumerate(students):
            if sid == student_id:
                students[i] = (sid, name, new_score)
                updated = True
                break
        
        if updated:
            _save_all_students(students)
        
        return updated
    except Exception as e:
        print(f"更新学生积分失败: {e}")
        return False

# 积分事件相关函数
def add_score_event(student_id: str, event_name: str, score_change: int, event_type: str = "score") -> bool:
    """添加积分事件"""
    try:
        # 检查学生是否存在
        student = get_student_by_id(student_id)
        if not student:
            return False
            
        # 记录积分事件到按天存储的文件
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        events_file = get_file_path(f"score_events_{date_str}.csv", is_score_event=True)
        
        # 检查文件是否存在，如果不存在则写入标题行
        file_exists = os.path.exists(events_file)
        with open(events_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["student_id", "event_name", "score_change", "timestamp", "event_type"])
            writer.writerow([student_id, event_name, score_change, timestamp.strftime("%Y-%m-%d %H:%M:%S"), event_type])
        
        # 更新学生当前积分
        sid, name, current_score = student
        new_score = current_score + score_change
        update_student_score(student_id, new_score)
        
        return True
    except Exception as e:
        print(f"添加积分事件失败: {e}")
        return False

def get_score_events_by_student(student_id: str) -> List[Tuple[str, str, int, str, str]]:
    """获取指定学生的积分事件"""
    try:
        events = []
        score_events_dir_path = os.path.join(get_data_dir(), SCORE_EVENTS_DIR)
        
        if not os.path.exists(score_events_dir_path):
            return events
            
        for filename in os.listdir(score_events_dir_path):
            if filename.startswith("score_events_") and filename.endswith(".csv"):
                file_path = os.path.join(score_events_dir_path, filename)
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None) # 读取标题行
                    if header is None: # 空文件
                        continue
                    
                    # 确保标题行包含所有预期字段，如果缺少则跳过此文件或按默认处理
                    expected_headers = ["student_id", "event_name", "score_change", "timestamp", "event_type"]
                    if not all(h in header for h in expected_headers):
                        print(f"警告: 文件 {filename} 缺少预期的标题行字段，跳过或按旧格式处理")
                        # 对于旧格式文件，尝试按原索引读取
                        f.seek(0) # 重置文件指针
                        next(reader) # 跳过标题行
                        for row in reader:
                            if len(row) >= 4 and row[0] == student_id:
                                sid, event_name, score_change, timestamp = row[0], row[1], int(row[2]), row[3]
                                events.append((sid, event_name, score_change, timestamp, "score")) # 默认为score类型
                        continue

                    # 获取列索引
                    col_indices = {h: header.index(h) for h in expected_headers}

                    for row in reader:
                        if len(row) > max(col_indices.values()) and row[col_indices["student_id"]] == student_id:
                            sid = row[col_indices["student_id"]]
                            event_name = row[col_indices["event_name"]]
                            score_change = int(row[col_indices["score_change"]])
                            timestamp = row[col_indices["timestamp"]]
                            event_type = row[col_indices["event_type"]] if "event_type" in col_indices else "score" # 兼容旧数据
                            events.append((sid, event_name, score_change, timestamp, event_type))
        
        return events
    except Exception as e:
        print(f"获取学生积分事件失败: {e}")
        return []

def _delete_student_score_events(student_id: str):
    """删除指定学生的所有积分事件"""
    try:
        score_events_dir_path = os.path.join(get_data_dir(), SCORE_EVENTS_DIR)
        
        if not os.path.exists(score_events_dir_path):
            return
            
        for filename in os.listdir(score_events_dir_path):
            if filename.startswith("score_events_") and filename.endswith(".csv"):
                file_path = os.path.join(score_events_dir_path, filename)
                all_events = []
                
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header:
                        all_events.append(header)
                        for row in reader:
                            if len(row) >= 1 and row[0] != student_id:
                                all_events.append(row)
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(all_events)
    except Exception as e:
        print(f"删除学生积分事件失败: {e}")

# 积分规则相关函数
def add_score_rule(rule_name: str, score_value: int) -> bool:
    """添加积分规则"""
    try:
        # 检查规则是否已存在
        if get_score_rule_by_name(rule_name):
            return False
        
        rules_file = get_file_path(SCORE_RULES_FILE)
        with open(rules_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([rule_name, score_value])
        return True
    except Exception as e:
        print(f"添加积分规则失败: {e}")
        return False

def get_all_score_rules() -> List[Tuple[str, int]]:
    """获取所有积分规则"""
    try:
        rules_file = get_file_path(SCORE_RULES_FILE)
        rules = []
        
        if not os.path.exists(rules_file):
            return rules
            
        with open(rules_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 2:
                    rule_name, score_value = row[0], int(row[1])
                    rules.append((rule_name, score_value))
        
        return rules
    except Exception as e:
        print(f"获取积分规则失败: {e}")
        return []

def get_score_rule_by_name(rule_name: str) -> Optional[Tuple[str, int]]:
    """根据规则名称获取积分规则"""
    rules = get_all_score_rules()
    for name, value in rules:
        if name == rule_name:
            return (name, value)
    return None

def delete_score_rule(rule_name: str) -> bool:
    """删除积分规则"""
    try:
        rules = get_all_score_rules()
        original_count = len(rules)
        rules = [(name, value) for name, value in rules if name != rule_name]
        
        if len(rules) < original_count:
            _save_all_score_rules(rules)
            return True
        
        return False
    except Exception as e:
        print(f"删除积分规则失败: {e}")
        return False

def _save_all_score_rules(rules: List[Tuple[str, int]]):
    """保存所有积分规则到文件"""
    rules_file = get_file_path(SCORE_RULES_FILE)
    with open(rules_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['rule_name', 'score_value'])
        for rule_name, score_value in rules:
            writer.writerow([rule_name, score_value])

# 设置相关函数
def get_setting(key: str, default_value: str = "") -> str:
    """获取设置值"""
    try:
        settings_file = get_file_path(SETTINGS_FILE)
        
        if not os.path.exists(settings_file):
            return default_value
            
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get(key, default_value)
    except Exception as e:
        print(f"获取设置失败: {e}")
        return default_value

def set_setting(key: str, value: str) -> bool:
    """设置值"""
    try:
        settings_file = get_file_path(SETTINGS_FILE)
        
        # 读取现有设置
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except:
            settings = {}
        
        # 更新设置
        settings[key] = value
        
        # 保存设置
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"设置值失败: {e}")
        return False

# CSV导入功能
def import_students_from_csv(csv_file_path: str) -> Tuple[int, int, List[str]]:
    """
    从CSV文件导入学生信息
    返回: (成功导入数量, 跳过数量, 错误信息列表)
    """
    success_count = 0
    skip_count = 0
    errors = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # 尝试检测是否有标题行
            first_row = next(reader, None)
            if not first_row:
                errors.append("CSV文件为空")
                return 0, 0, errors
            
            # 如果第一行看起来像标题，跳过它
            if first_row[0].lower() in ['student_id', 'studentid', '学号', 'id']:
                pass  # 跳过标题行
            else:
                # 第一行是数据，重新处理
                f.seek(0)
                reader = csv.reader(f)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 1:
                    continue
                
                student_id = row[0].strip()
                name = row[1].strip() if len(row) > 1 else ""
                
                if not student_id:
                    errors.append(f"第{row_num}行: 学号不能为空")
                    continue
                
                if add_student(student_id, name):
                    success_count += 1
                else:
                    skip_count += 1
                    errors.append(f"第{row_num}行: 学号 {student_id} 已存在，跳过")
    
    except Exception as e:
        errors.append(f"读取CSV文件失败: {str(e)}")
    
    return success_count, skip_count, errors



# 新增数据文件路径配置
REWARD_EVENTS_FILE = 'reward_events.csv'
REWARD_RULES_FILE = 'reward_rules.csv'
DAILY_TASK_RULES_FILE = 'daily_task_rules.csv'
DAILY_TASK_EVENTS_FILE = 'daily_task_events.csv'
SCORE_EVENTS_DIR = 'score_events' # 新的积分事件存储目录



# 兑换事件相关函数
def add_reward_event(student_id: str, reward_name: str, score_cost: int) -> bool:
    """添加兑换事件"""
    try:
        # 检查学生是否存在
        student = get_student_by_id(student_id)
        if not student:
            return False
            
        # 记录兑换事件
        events_file = get_file_path(REWARD_EVENTS_FILE)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(events_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, reward_name, score_cost, timestamp])
        
        # 更新学生当前积分 (兑换是扣分)
        sid, name, current_score = student
        new_score = current_score - score_cost
        update_student_score(student_id, new_score)
        
        # 同时记录到总积分事件中，类型为'reward'
        add_score_event(student_id, f"兑换: {reward_name}", -score_cost, event_type="reward")

        return True
    except Exception as e:
        print(f"添加兑换事件失败: {e}")
        return False

def get_all_reward_events() -> List[Tuple[str, str, int, str]]:
    """获取所有兑换事件"""
    try:
        events_file = get_file_path(REWARD_EVENTS_FILE)
        events = []
        
        if not os.path.exists(events_file):
            return events
            
        with open(events_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 4:
                    student_id, reward_name, score_cost, timestamp = row[0], row[1], int(row[2]), row[3]
                    events.append((student_id, reward_name, score_cost, timestamp))
        
        return events
    except Exception as e:
        print(f"获取兑换事件失败: {e}")
        return []

# 兑换规则相关函数
def add_reward_rule(rule_name: str, score_cost: int) -> bool:
    """添加兑换规则"""
    try:
        if get_reward_rule_by_name(rule_name):
            return False
        
        rules_file = get_file_path(REWARD_RULES_FILE)
        with open(rules_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([rule_name, score_cost])
        return True
    except Exception as e:
        print(f"添加兑换规则失败: {e}")
        return False

def get_all_reward_rules() -> List[Tuple[str, int]]:
    """获取所有兑换规则"""
    try:
        rules_file = get_file_path(REWARD_RULES_FILE)
        rules = []
        
        if not os.path.exists(rules_file):
            return rules
            
        with open(rules_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 2:
                    rule_name, score_cost = row[0], int(row[1])
                    rules.append((rule_name, score_cost))
        
        return rules
    except Exception as e:
        print(f"获取兑换规则失败: {e}")
        return []

def get_reward_rule_by_name(rule_name: str) -> Optional[Tuple[str, int]]:
    """根据规则名称获取兑换规则"""
    rules = get_all_reward_rules()
    for name, cost in rules:
        if name == rule_name:
            return (name, cost)
    return None

def delete_reward_rule(rule_name: str) -> bool:
    """删除兑换规则"""
    try:
        rules = get_all_reward_rules()
        original_count = len(rules)
        rules = [(name, cost) for name, cost in rules if name != rule_name]
        
        if len(rules) < original_count:
            _save_all_reward_rules(rules)
            return True
        
        return False
    except Exception as e:
        print(f"删除兑换规则失败: {e}")
        return False

def _save_all_reward_rules(rules: List[Tuple[str, int]]):
    """保存所有兑换规则到文件"""
    rules_file = get_file_path(REWARD_RULES_FILE)
    with open(rules_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["rule_name", "score_cost"])
        for rule_name, score_cost in rules:
            writer.writerow([rule_name, score_cost])




# 每日任务规则相关函数
def add_daily_task_rule(task_name: str, score_value: int) -> bool:
    """添加每日任务规则"""
    try:
        if get_daily_task_rule_by_name(task_name):
            return False
        
        rules_file = get_file_path(DAILY_TASK_RULES_FILE)
        with open(rules_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([task_name, score_value])
        return True
    except Exception as e:
        print(f"添加每日任务规则失败: {e}")
        return False

def get_all_daily_task_rules() -> List[Tuple[str, int]]:
    """获取所有每日任务规则"""
    try:
        rules_file = get_file_path(DAILY_TASK_RULES_FILE)
        rules = []
        
        if not os.path.exists(rules_file):
            return rules
            
        with open(rules_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 2:
                    task_name, score_value = row[0], int(row[1])
                    rules.append((task_name, score_value))
        
        return rules
    except Exception as e:
        print(f"获取每日任务规则失败: {e}")
        return []

def get_daily_task_rule_by_name(task_name: str) -> Optional[Tuple[str, int]]:
    """根据规则名称获取每日任务规则"""
    rules = get_all_daily_task_rules()
    for name, value in rules:
        if name == task_name:
            return (name, value)
    return None

def delete_daily_task_rule(task_name: str) -> bool:
    """删除每日任务规则"""
    try:
        rules = get_all_daily_task_rules()
        original_count = len(rules)
        rules = [(name, value) for name, value in rules if name != task_name]
        
        if len(rules) < original_count:
            _save_all_daily_task_rules(rules)
            return True
        
        return False
    except Exception as e:
        print(f"删除每日任务规则失败: {e}")
        return False

def _save_all_daily_task_rules(rules: List[Tuple[str, int]]):
    """保存所有每日任务规则到文件"""
    rules_file = get_file_path(DAILY_TASK_RULES_FILE)
    with open(rules_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["task_name", "score_value"])
        for task_name, score_value in rules:
            writer.writerow([task_name, score_value])

# 每日任务事件相关函数
def add_daily_task_event(student_id: str, task_name: str, score_change: int, timestamp: str) -> bool:
    """添加每日任务事件"""
    try:
        # 检查学生是否存在
        student = get_student_by_id(student_id)
        if not student:
            return False
            
        # 记录每日任务事件
        events_file = get_file_path(DAILY_TASK_EVENTS_FILE)
        
        with open(events_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, task_name, score_change, timestamp])
        
        # 同时记录到总积分事件中，类型为'daily_task'
        add_score_event(student_id, f"每日任务: {task_name}", score_change, event_type="daily_task")

        return True
    except Exception as e:
        print(f"添加每日任务事件失败: {e}")
        return False

def get_all_daily_task_events() -> List[Tuple[str, str, int, str]]:
    """获取所有每日任务事件"""
    try:
        events_file = get_file_path(DAILY_TASK_EVENTS_FILE)
        events = []
        
        if not os.path.exists(events_file):
            return events
            
        with open(events_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 4:
                    student_id, task_name, score_change, timestamp = row[0], row[1], int(row[2]), row[3]
                    events.append((student_id, task_name, score_change, timestamp))
        
        return events
    except Exception as e:
        print(f"获取每日任务事件失败: {e}")
        return []



# 历史记录查询相关函数
def get_all_events_in_date_range(start_date: str = None, end_date: str = None, 
                                student_id: str = None, event_type: str = None) -> List[Tuple[str, str, int, str, str]]:
    """
    获取指定时间范围内的所有事件
    参数:
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - student_id: 学生ID筛选
    - event_type: 事件类型筛选 ('score', 'reward', 'daily_task')
    
    返回: [(student_id, event_name, score_change, timestamp, event_type), ...]
    """
    try:
        all_events = []
        
        # 从按天存储的积分事件文件中读取
        score_events_dir_path = os.path.join(get_data_dir(), SCORE_EVENTS_DIR)
        if os.path.exists(score_events_dir_path):
            for filename in os.listdir(score_events_dir_path):
                if filename.startswith("score_events_") and filename.endswith(".csv"):
                    # 从文件名提取日期
                    file_date = filename.replace("score_events_", "").replace(".csv", "")
                    
                    # 检查日期范围
                    if start_date and file_date < start_date:
                        continue
                    if end_date and file_date > end_date:
                        continue
                    
                    file_path = os.path.join(score_events_dir_path, filename)
                    with open(file_path, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                        if header is None:
                            continue
                        
                        # 处理新格式和旧格式
                        expected_headers = ["student_id", "event_name", "score_change", "timestamp", "event_type"]
                        if all(h in header for h in expected_headers):
                            col_indices = {h: header.index(h) for h in expected_headers}
                            for row in reader:
                                if len(row) > max(col_indices.values()):
                                    sid = row[col_indices["student_id"]]
                                    event_name = row[col_indices["event_name"]]
                                    score_change = int(row[col_indices["score_change"]])
                                    timestamp = row[col_indices["timestamp"]]
                                    evt_type = row[col_indices["event_type"]]
                                    
                                    # 应用筛选条件
                                    if student_id and sid != student_id:
                                        continue
                                    if event_type and evt_type != event_type:
                                        continue
                                    
                                    all_events.append((sid, event_name, score_change, timestamp, evt_type))
                        else:
                            # 旧格式处理
                            for row in reader:
                                if len(row) >= 4:
                                    sid, event_name, score_change, timestamp = row[0], row[1], int(row[2]), row[3]
                                    evt_type = "score"  # 默认类型
                                    
                                    # 应用筛选条件
                                    if student_id and sid != student_id:
                                        continue
                                    if event_type and evt_type != event_type:
                                        continue
                                    
                                    all_events.append((sid, event_name, score_change, timestamp, evt_type))
        
        # 按时间戳排序（最新的在前）
        all_events.sort(key=lambda x: x[3], reverse=True)
        
        return all_events
    except Exception as e:
        print(f"获取历史记录失败: {e}")
        return []

def get_all_score_rules_names() -> List[str]:
    """获取所有积分规则名称"""
    rules = get_all_score_rules()
    return [rule[0] for rule in rules]

def get_all_reward_rules_names() -> List[str]:
    """获取所有兑换规则名称"""
    rules = get_all_reward_rules()
    return [rule[0] for rule in rules]

def get_all_daily_task_rules_names() -> List[str]:
    """获取所有每日任务规则名称"""
    rules = get_all_daily_task_rules()
    return [rule[0] for rule in rules]

def search_events_by_rule_name(rule_name: str, start_date: str = None, end_date: str = None) -> List[Tuple[str, str, int, str, str]]:
    """
    根据规则名称搜索事件
    """
    all_events = get_all_events_in_date_range(start_date, end_date)
    filtered_events = []
    
    for event in all_events:
        student_id, event_name, score_change, timestamp, event_type = event
        # 检查事件名称是否包含规则名称
        if rule_name.lower() in event_name.lower():
            filtered_events.append(event)
    
    return filtered_events

