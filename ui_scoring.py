from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTextEdit, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QCheckBox, QScrollArea)
from PySide6.QtCore import Qt
from database import get_all_students, get_all_score_rules, add_score_event, get_score_events_by_student

class ScoringPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 标题
        self.main_layout.addWidget(QLabel("<h1>学生记分</h1>"), alignment=Qt.AlignCenter)

        # 单一学生记分
        single_score_layout = QVBoxLayout()
        single_score_layout.addWidget(QLabel("<h3>单一学生记分</h3>"))

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("学号:"))
        self.single_student_id_input = QLineEdit()
        self.single_student_id_input.setPlaceholderText("请输入学号")
        form_layout.addWidget(self.single_student_id_input)

        form_layout.addWidget(QLabel("积分规则:"))
        self.single_rule_combo = QComboBox()
        form_layout.addWidget(self.single_rule_combo)

        self.single_score_btn = QPushButton("记分")
        form_layout.addWidget(self.single_score_btn)
        form_layout.addStretch()
        single_score_layout.addLayout(form_layout)

        self.main_layout.addLayout(single_score_layout)

        # 批量选择记分
        batch_score_layout = QVBoxLayout()
        batch_score_layout.addWidget(QLabel("<h3>批量选择记分</h3>"))

        # 积分规则选择
        rule_layout = QHBoxLayout()
        rule_layout.addWidget(QLabel("积分规则:"))
        self.batch_rule_combo = QComboBox()
        rule_layout.addWidget(self.batch_rule_combo)
        
        self.batch_score_btn = QPushButton("为选中学生记分")
        rule_layout.addWidget(self.batch_score_btn)
        
        self.select_all_btn = QPushButton("全选")
        self.deselect_all_btn = QPushButton("全不选")
        rule_layout.addWidget(self.select_all_btn)
        rule_layout.addWidget(self.deselect_all_btn)
        rule_layout.addStretch()
        batch_score_layout.addLayout(rule_layout)

        # 学生选择区域
        students_label = QLabel("选择学生:")
        batch_score_layout.addWidget(students_label)
        
        # 创建滚动区域来容纳学生复选框
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(200)  # 限制高度
        
        self.students_widget = QWidget()
        self.students_layout = QVBoxLayout(self.students_widget)
        self.students_checkboxes = []
        
        self.scroll_area.setWidget(self.students_widget)
        batch_score_layout.addWidget(self.scroll_area)

        self.main_layout.addLayout(batch_score_layout)

        # 文本批量记分（保留原有功能）
        text_batch_layout = QVBoxLayout()
        text_batch_layout.addWidget(QLabel("<h3>文本批量记分</h3>"))

        text_form_layout = QHBoxLayout()
        text_form_layout.addWidget(QLabel("学号列表 (每行一个):"))
        self.batch_student_ids_input = QTextEdit()
        self.batch_student_ids_input.setPlaceholderText("请输入学号，每行一个")
        self.batch_student_ids_input.setMaximumHeight(100)
        text_form_layout.addWidget(self.batch_student_ids_input)

        text_form_layout.addWidget(QLabel("积分规则:"))
        self.text_batch_rule_combo = QComboBox()
        text_form_layout.addWidget(self.text_batch_rule_combo)

        self.text_batch_score_btn = QPushButton("批量记分")
        text_form_layout.addWidget(self.text_batch_score_btn)
        text_form_layout.addStretch()
        text_batch_layout.addLayout(text_form_layout)

        self.main_layout.addLayout(text_batch_layout)

        # 学生积分历史
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("<h3>学生积分历史</h3>"))

        history_search_layout = QHBoxLayout()
        history_search_layout.addWidget(QLabel("查询学号:"))
        self.history_student_id_input = QLineEdit()
        self.history_student_id_input.setPlaceholderText("请输入学号")
        history_search_layout.addWidget(self.history_student_id_input)
        self.search_history_btn = QPushButton("查询历史")
        history_search_layout.addWidget(self.search_history_btn)
        history_search_layout.addStretch()
        history_layout.addLayout(history_search_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["事件名称", "积分变化", "时间"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)

        self.main_layout.addLayout(history_layout)

        # 连接信号与槽
        self.single_score_btn.clicked.connect(self.single_score_action)
        self.batch_score_btn.clicked.connect(self.batch_score_action)
        self.text_batch_score_btn.clicked.connect(self.text_batch_score_action)
        self.search_history_btn.clicked.connect(self.load_score_history)
        self.select_all_btn.clicked.connect(self.select_all_students)
        self.deselect_all_btn.clicked.connect(self.deselect_all_students)

    def load_data(self):
        self.load_students_checkboxes()
        self.load_score_rules_for_combos()

    def load_students_checkboxes(self):
        """加载学生复选框列表"""
        # 清除现有复选框
        for checkbox in self.students_checkboxes:
            checkbox.setParent(None)
        self.students_checkboxes.clear()

        # 获取所有学生
        students = get_all_students()
        
        for student_id, name, score in students:
            display_text = f"{student_id}"
            if name:
                display_text += f" - {name}"
            display_text += f" (当前积分: {score})"
            
            checkbox = QCheckBox(display_text)
            checkbox.setProperty("student_id", student_id)
            self.students_checkboxes.append(checkbox)
            self.students_layout.addWidget(checkbox)

    def load_score_rules_for_combos(self):
        """加载积分规则到下拉框"""
        self.single_rule_combo.clear()
        self.batch_rule_combo.clear()
        self.text_batch_rule_combo.clear()
        
        rules = get_all_score_rules()
        for rule_name, score_value in rules:
            display_text = f"{rule_name} ({score_value:+d})"
            self.single_rule_combo.addItem(display_text, (rule_name, score_value))
            self.batch_rule_combo.addItem(display_text, (rule_name, score_value))
            self.text_batch_rule_combo.addItem(display_text, (rule_name, score_value))

    def select_all_students(self):
        """全选学生"""
        for checkbox in self.students_checkboxes:
            checkbox.setChecked(True)

    def deselect_all_students(self):
        """全不选学生"""
        for checkbox in self.students_checkboxes:
            checkbox.setChecked(False)

    def get_selected_students(self):
        """获取选中的学生ID列表"""
        selected_students = []
        for checkbox in self.students_checkboxes:
            if checkbox.isChecked():
                student_id = checkbox.property("student_id")
                selected_students.append(student_id)
        return selected_students

    def single_score_action(self):
        """单一学生记分"""
        student_id = self.single_student_id_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "输入错误", "学号不能为空！")
            return

        selected_rule_data = self.single_rule_combo.currentData()
        if not selected_rule_data:
            QMessageBox.warning(self, "输入错误", "请选择积分规则！")
            return

        rule_name, score_value = selected_rule_data

        try:
            if add_score_event(student_id, rule_name, score_value):
                QMessageBox.information(self, "成功", f"学生 {student_id} 积分已更新！")
                self.single_student_id_input.clear()
                self.load_students_checkboxes()  # 刷新学生列表显示最新积分
                self.load_score_history(student_id)  # 刷新当前学生的历史记录
            else:
                QMessageBox.warning(self, "错误", f"学生 {student_id} 不存在！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"记分失败: {e}")

    def batch_score_action(self):
        """批量选择记分"""
        selected_students = self.get_selected_students()
        if not selected_students:
            QMessageBox.warning(self, "选择错误", "请至少选择一个学生！")
            return

        selected_rule_data = self.batch_rule_combo.currentData()
        if not selected_rule_data:
            QMessageBox.warning(self, "输入错误", "请选择积分规则！")
            return

        rule_name, score_value = selected_rule_data

        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认批量记分", 
            f"确定要为 {len(selected_students)} 名学生应用规则 '{rule_name}' ({score_value:+d}分) 吗？",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return

        success_count = 0
        failed_students = []
        
        for student_id in selected_students:
            try:
                if add_score_event(student_id, rule_name, score_value):
                    success_count += 1
                else:
                    failed_students.append(student_id)
            except Exception:
                failed_students.append(student_id)
        
        # 显示结果
        if success_count > 0:
            QMessageBox.information(self, "成功", f"成功为 {success_count} 名学生记分！")
            self.load_students_checkboxes()  # 刷新学生列表显示最新积分
            self.deselect_all_students()  # 清除选择
        
        if failed_students:
            QMessageBox.warning(self, "部分失败", f"以下学号记分失败:\n{', '.join(failed_students)}")

    def text_batch_score_action(self):
        """文本批量记分"""
        student_ids_text = self.batch_student_ids_input.toPlainText().strip()
        if not student_ids_text:
            QMessageBox.warning(self, "输入错误", "学号列表不能为空！")
            return

        student_ids = [s.strip() for s in student_ids_text.split("\n") if s.strip()]

        selected_rule_data = self.text_batch_rule_combo.currentData()
        if not selected_rule_data:
            QMessageBox.warning(self, "输入错误", "请选择积分规则！")
            return

        rule_name, score_value = selected_rule_data

        success_count = 0
        failed_students = []
        for student_id in student_ids:
            try:
                if add_score_event(student_id, rule_name, score_value):
                    success_count += 1
                else:
                    failed_students.append(student_id)
            except Exception:
                failed_students.append(student_id)
        
        if success_count > 0:
            QMessageBox.information(self, "成功", f"成功为 {success_count} 名学生记分！")
            self.load_students_checkboxes()  # 刷新学生列表显示最新积分
        
        if failed_students:
            QMessageBox.warning(self, "部分失败", f"以下学号记分失败 (可能不存在):\n{', '.join(failed_students)}")
        
        self.batch_student_ids_input.clear()

    def load_score_history(self, student_id=None):
        """加载学生积分历史"""
        if student_id is None:
            student_id = self.history_student_id_input.text().strip()
        
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        if not student_id:
            return

        events = get_score_events_by_student(student_id)
        self.history_table.setRowCount(len(events))
        for i, (sid, event_name, score_change, timestamp) in enumerate(events):
            self.history_table.setItem(i, 0, QTableWidgetItem(event_name))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{score_change:+d}"))
            self.history_table.setItem(i, 2, QTableWidgetItem(timestamp))

