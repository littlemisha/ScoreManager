from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QMessageBox, QDialog, QFormLayout, 
                             QFileDialog, QInputDialog, QTabWidget)
from PySide6.QtCore import Qt
from database import (add_student, get_all_students, update_student_name, delete_student, 
                     add_score_rule, get_all_score_rules, delete_score_rule, import_students_from_csv,
                     add_reward_rule, get_all_reward_rules, delete_reward_rule,
                     add_daily_task_rule, get_all_daily_task_rules, delete_daily_task_rule)

class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加学生")
        self.setFixedSize(300, 150)
        self.layout = QFormLayout(self)

        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("请输入学号")
        self.layout.addRow("学号:", self.student_id_input)

        self.student_name_input = QLineEdit()
        self.student_name_input.setPlaceholderText("请输入姓名 (可选)")
        self.layout.addRow("姓名:", self.student_name_input)

        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.accept)
        self.layout.addRow(self.add_button)

    def get_student_info(self):
        return self.student_id_input.text().strip(), self.student_name_input.text().strip()

class AddRuleDialog(QDialog):
    def __init__(self, parent=None, rule_type="score"):
        super().__init__(parent)
        self.rule_type = rule_type
        if rule_type == "score":
            self.setWindowTitle("添加积分规则")
        elif rule_type == "reward":
            self.setWindowTitle("添加兑换规则")
        elif rule_type == "daily_task":
            self.setWindowTitle("添加每日任务规则")
        
        self.setFixedSize(300, 150)
        self.layout = QFormLayout(self)

        self.rule_name_input = QLineEdit()
        if rule_type == "score":
            self.rule_name_input.setPlaceholderText("请输入规则名称 (如：做操+1分)")
        elif rule_type == "reward":
            self.rule_name_input.setPlaceholderText("请输入兑换项目名称 (如：小奖品)")
        elif rule_type == "daily_task":
            self.rule_name_input.setPlaceholderText("请输入任务名称 (如：完成作业)")
        self.layout.addRow("规则名称:", self.rule_name_input)

        self.score_value_input = QLineEdit()
        if rule_type == "score":
            self.score_value_input.setPlaceholderText("请输入积分值 (正数加分，负数减分)")
        elif rule_type == "reward":
            self.score_value_input.setPlaceholderText("请输入积分消耗 (正数)")
        elif rule_type == "daily_task":
            self.score_value_input.setPlaceholderText("请输入积分奖励 (正数)")
        self.score_value_input.setValidator(self.create_int_validator())
        
        if rule_type == "score":
            self.layout.addRow("积分值:", self.score_value_input)
        elif rule_type == "reward":
            self.layout.addRow("积分消耗:", self.score_value_input)
        elif rule_type == "daily_task":
            self.layout.addRow("积分奖励:", self.score_value_input)

        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.accept)
        self.layout.addRow(self.add_button)

    def create_int_validator(self):
        from PySide6.QtGui import QIntValidator
        return QIntValidator()

    def get_rule_info(self):
        name = self.rule_name_input.text().strip()
        value_str = self.score_value_input.text().strip()
        value = int(value_str) if value_str else 0
        return name, value

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_students()
        self.load_score_rules()
        self.load_reward_rules()
        self.load_daily_task_rules()

    def setup_ui(self):
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 学生管理选项卡
        student_tab = QWidget()
        self.setup_student_tab(student_tab)
        self.tab_widget.addTab(student_tab, "学生管理")
        
        # 积分规则选项卡
        score_rule_tab = QWidget()
        self.setup_score_rule_tab(score_rule_tab)
        self.tab_widget.addTab(score_rule_tab, "积分规则")
        
        # 兑换规则选项卡
        reward_rule_tab = QWidget()
        self.setup_reward_rule_tab(reward_rule_tab)
        self.tab_widget.addTab(reward_rule_tab, "兑换规则")
        
        # 每日任务规则选项卡
        daily_task_rule_tab = QWidget()
        self.setup_daily_task_rule_tab(daily_task_rule_tab)
        self.tab_widget.addTab(daily_task_rule_tab, "每日任务规则")
        
        self.main_layout.addWidget(self.tab_widget)

    def setup_student_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 学生管理部分
        student_group_layout = QVBoxLayout()
        student_group_layout.addWidget(QLabel("<h3>学生管理</h3>"))

        student_controls_layout = QHBoxLayout()
        self.add_student_btn = QPushButton("添加学生")
        self.import_students_btn = QPushButton("导入学生(CSV)")
        self.edit_student_btn = QPushButton("编辑学生姓名")
        self.delete_student_btn = QPushButton("删除学生")
        student_controls_layout.addWidget(self.add_student_btn)
        student_controls_layout.addWidget(self.import_students_btn)
        student_controls_layout.addWidget(self.edit_student_btn)
        student_controls_layout.addWidget(self.delete_student_btn)

        self.student_list_widget = QListWidget()
        student_group_layout.addLayout(student_controls_layout)
        student_group_layout.addWidget(self.student_list_widget)

        layout.addLayout(student_group_layout)

        # 连接信号与槽
        self.add_student_btn.clicked.connect(self.add_student_action)
        self.import_students_btn.clicked.connect(self.import_students_action)
        self.edit_student_btn.clicked.connect(self.edit_student_action)
        self.delete_student_btn.clicked.connect(self.delete_student_action)

    def setup_score_rule_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 积分规则管理部分
        rule_group_layout = QVBoxLayout()
        rule_group_layout.addWidget(QLabel("<h3>积分规则管理</h3>"))

        rule_controls_layout = QHBoxLayout()
        self.add_score_rule_btn = QPushButton("添加积分规则")
        self.delete_score_rule_btn = QPushButton("删除积分规则")
        rule_controls_layout.addWidget(self.add_score_rule_btn)
        rule_controls_layout.addWidget(self.delete_score_rule_btn)

        self.score_rule_list_widget = QListWidget()
        rule_group_layout.addLayout(rule_controls_layout)
        rule_group_layout.addWidget(self.score_rule_list_widget)

        layout.addLayout(rule_group_layout)

        # 连接信号与槽
        self.add_score_rule_btn.clicked.connect(self.add_score_rule_action)
        self.delete_score_rule_btn.clicked.connect(self.delete_score_rule_action)

    def setup_reward_rule_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 兑换规则管理部分
        rule_group_layout = QVBoxLayout()
        rule_group_layout.addWidget(QLabel("<h3>兑换规则管理</h3>"))

        rule_controls_layout = QHBoxLayout()
        self.add_reward_rule_btn = QPushButton("添加兑换规则")
        self.delete_reward_rule_btn = QPushButton("删除兑换规则")
        rule_controls_layout.addWidget(self.add_reward_rule_btn)
        rule_controls_layout.addWidget(self.delete_reward_rule_btn)

        self.reward_rule_list_widget = QListWidget()
        rule_group_layout.addLayout(rule_controls_layout)
        rule_group_layout.addWidget(self.reward_rule_list_widget)

        layout.addLayout(rule_group_layout)

        # 连接信号与槽
        self.add_reward_rule_btn.clicked.connect(self.add_reward_rule_action)
        self.delete_reward_rule_btn.clicked.connect(self.delete_reward_rule_action)

    def setup_daily_task_rule_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # 每日任务规则管理部分
        rule_group_layout = QVBoxLayout()
        rule_group_layout.addWidget(QLabel("<h3>每日任务规则管理</h3>"))

        rule_controls_layout = QHBoxLayout()
        self.add_daily_task_rule_btn = QPushButton("添加每日任务规则")
        self.delete_daily_task_rule_btn = QPushButton("删除每日任务规则")
        rule_controls_layout.addWidget(self.add_daily_task_rule_btn)
        rule_controls_layout.addWidget(self.delete_daily_task_rule_btn)

        self.daily_task_rule_list_widget = QListWidget()
        rule_group_layout.addLayout(rule_controls_layout)
        rule_group_layout.addWidget(self.daily_task_rule_list_widget)

        layout.addLayout(rule_group_layout)

        # 连接信号与槽
        self.add_daily_task_rule_btn.clicked.connect(self.add_daily_task_rule_action)
        self.delete_daily_task_rule_btn.clicked.connect(self.delete_daily_task_rule_action)

    def load_students(self):
        self.student_list_widget.clear()
        students = get_all_students()
        for student_id, name, score in students:
            display_text = f"学号: {student_id}"
            if name: display_text += f" 姓名: {name}"
            display_text += f" 积分: {score}"
            self.student_list_widget.addItem(display_text)

    def add_student_action(self):
        dialog = AddStudentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            student_id, name = dialog.get_student_info()
            if not student_id:
                QMessageBox.warning(self, "输入错误", "学号不能为空！")
                return
            if add_student(student_id, name):
                QMessageBox.information(self, "成功", f"学生 {student_id} 添加成功！")
                self.load_students()
            else:
                QMessageBox.warning(self, "错误", f"学号 {student_id} 已存在！")

    def import_students_action(self):
        """导入学生CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择CSV文件", 
            "", 
            "CSV文件 (*.csv);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        # 显示CSV格式说明
        msg = QMessageBox()
        msg.setWindowTitle("CSV格式说明")
        msg.setText("CSV文件格式要求：\n\n"
                   "第一列：学号（必填）\n"
                   "第二列：姓名（可选）\n\n"
                   "示例：\n"
                   "学号,姓名\n"
                   "2023001,张三\n"
                   "2023002,李四\n\n"
                   "或者直接：\n"
                   "2023001,张三\n"
                   "2023002,李四\n\n"
                   "确定要导入吗？")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec() != QMessageBox.Yes:
            return
        
        try:
            success_count, skip_count, errors = import_students_from_csv(file_path)
            
            # 显示导入结果
            result_msg = f"导入完成！\n\n"
            result_msg += f"成功导入：{success_count} 个学生\n"
            result_msg += f"跳过重复：{skip_count} 个学生\n"
            
            if errors:
                result_msg += f"\n错误信息：\n"
                for error in errors[:10]:  # 最多显示10个错误
                    result_msg += f"• {error}\n"
                if len(errors) > 10:
                    result_msg += f"... 还有 {len(errors) - 10} 个错误"
            
            if success_count > 0:
                QMessageBox.information(self, "导入成功", result_msg)
                self.load_students()  # 刷新学生列表
            else:
                QMessageBox.warning(self, "导入失败", result_msg)
                
        except Exception as e:
            QMessageBox.critical(self, "导入错误", f"导入CSV文件时发生错误：\n{str(e)}")

    def edit_student_action(self):
        selected_item = self.student_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "请选择要编辑的学生！")
            return

        current_text = selected_item.text()
        student_id = current_text.split("学号: ")[1].split(" ")[0]

        # 获取当前姓名
        current_name = ""
        if " 姓名: " in current_text:
            current_name = current_text.split(" 姓名: ")[1].split(" 积分: ")[0]

        new_name, ok = QInputDialog.getText(
            self, 
            "编辑学生姓名", 
            f"请输入学生 {student_id} 的新姓名：", 
            QLineEdit.Normal, 
            current_name
        )
        
        if ok:
            if update_student_name(student_id, new_name.strip()):
                QMessageBox.information(self, "成功", f"学生 {student_id} 姓名更新成功！")
                self.load_students()
            else:
                QMessageBox.warning(self, "错误", f"更新学生 {student_id} 姓名失败！")

    def delete_student_action(self):
        selected_item = self.student_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "请选择要删除的学生！")
            return

        current_text = selected_item.text()
        student_id = current_text.split("学号: ")[1].split(" ")[0]

        reply = QMessageBox.question(self, "确认删除", f"确定要删除学生 {student_id} 及其所有积分记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if delete_student(student_id):
                QMessageBox.information(self, "成功", f"学生 {student_id} 已删除！")
                self.load_students()
            else:
                QMessageBox.warning(self, "错误", f"删除学生 {student_id} 失败！")

    def load_score_rules(self):
        self.score_rule_list_widget.clear()
        rules = get_all_score_rules()
        for rule_name, score_value in rules:
            self.score_rule_list_widget.addItem(f"规则名称: {rule_name} 积分值: {score_value}")

    def add_score_rule_action(self):
        dialog = AddRuleDialog(self, rule_type="score")
        if dialog.exec() == QDialog.Accepted:
            rule_name, score_value = dialog.get_rule_info()
            if not rule_name:
                QMessageBox.warning(self, "输入错误", "规则名称不能为空！")
                return
            if add_score_rule(rule_name, score_value):
                QMessageBox.information(self, "成功", f"积分规则 '{rule_name}' 添加成功！")
                self.load_score_rules()
            else:
                QMessageBox.warning(self, "错误", f"积分规则 '{rule_name}' 已存在！")

    def delete_score_rule_action(self):
        selected_item = self.score_rule_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "请选择要删除的规则！")
            return

        current_text = selected_item.text()
        rule_name = current_text.split("规则名称: ")[1].split(" 积分值: ")[0]

        reply = QMessageBox.question(self, "确认删除", f"确定要删除积分规则 '{rule_name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if delete_score_rule(rule_name):
                QMessageBox.information(self, "成功", f"积分规则 '{rule_name}' 已删除！")
                self.load_score_rules()
            else:
                QMessageBox.warning(self, "错误", f"删除积分规则 '{rule_name}' 失败！")

    def load_reward_rules(self):
        self.reward_rule_list_widget.clear()
        rules = get_all_reward_rules()
        for rule_name, score_cost in rules:
            self.reward_rule_list_widget.addItem(f"兑换项目: {rule_name} 积分消耗: {score_cost}")

    def add_reward_rule_action(self):
        dialog = AddRuleDialog(self, rule_type="reward")
        if dialog.exec() == QDialog.Accepted:
            rule_name, score_cost = dialog.get_rule_info()
            if not rule_name:
                QMessageBox.warning(self, "输入错误", "兑换项目名称不能为空！")
                return
            if add_reward_rule(rule_name, score_cost):
                QMessageBox.information(self, "成功", f"兑换规则 '{rule_name}' 添加成功！")
                self.load_reward_rules()
            else:
                QMessageBox.warning(self, "错误", f"兑换规则 '{rule_name}' 已存在！")

    def delete_reward_rule_action(self):
        selected_item = self.reward_rule_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "请选择要删除的兑换规则！")
            return

        current_text = selected_item.text()
        rule_name = current_text.split("兑换项目: ")[1].split(" 积分消耗: ")[0]

        reply = QMessageBox.question(self, "确认删除", f"确定要删除兑换规则 '{rule_name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if delete_reward_rule(rule_name):
                QMessageBox.information(self, "成功", f"兑换规则 '{rule_name}' 已删除！")
                self.load_reward_rules()
            else:
                QMessageBox.warning(self, "错误", f"删除兑换规则 '{rule_name}' 失败！")

    def load_daily_task_rules(self):
        self.daily_task_rule_list_widget.clear()
        rules = get_all_daily_task_rules()
        for task_name, score_value in rules:
            self.daily_task_rule_list_widget.addItem(f"任务名称: {task_name} 积分奖励: {score_value}")

    def add_daily_task_rule_action(self):
        dialog = AddRuleDialog(self, rule_type="daily_task")
        if dialog.exec() == QDialog.Accepted:
            task_name, score_value = dialog.get_rule_info()
            if not task_name:
                QMessageBox.warning(self, "输入错误", "任务名称不能为空！")
                return
            if add_daily_task_rule(task_name, score_value):
                QMessageBox.information(self, "成功", f"每日任务规则 '{task_name}' 添加成功！")
                self.load_daily_task_rules()
            else:
                QMessageBox.warning(self, "错误", f"每日任务规则 '{task_name}' 已存在！")

    def delete_daily_task_rule_action(self):
        selected_item = self.daily_task_rule_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "提示", "请选择要删除的每日任务规则！")
            return

        current_text = selected_item.text()
        task_name = current_text.split("任务名称: ")[1].split(" 积分奖励: ")[0]

        reply = QMessageBox.question(self, "确认删除", f"确定要删除每日任务规则 '{task_name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if delete_daily_task_rule(task_name):
                QMessageBox.information(self, "成功", f"每日任务规则 '{task_name}' 已删除！")
                self.load_daily_task_rules()
            else:
                QMessageBox.warning(self, "错误", f"删除每日任务规则 '{task_name}' 失败！")

    def load_data(self):
        """刷新所有数据"""
        self.load_students()
        self.load_score_rules()
        self.load_reward_rules()
        self.load_daily_task_rules()

