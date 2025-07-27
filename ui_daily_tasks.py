from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateEdit, QListWidget, QCheckBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from database import (get_all_students, get_all_daily_task_rules, add_daily_task_event, 
                     get_all_daily_task_events)

class DailyTasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 标题
        self.main_layout.addWidget(QLabel("<h1>每日任务记分</h1>"), alignment=Qt.AlignCenter)

        # 任务记分操作
        task_layout = QVBoxLayout()
        task_layout.addWidget(QLabel("<h3>每日任务记分</h3>"))

        # 日期和任务选择
        date_task_layout = QHBoxLayout()
        
        date_task_layout.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_task_layout.addWidget(self.date_edit)

        date_task_layout.addWidget(QLabel("任务:"))
        self.task_combo = QComboBox()
        self.task_combo.setPlaceholderText("选择每日任务")
        date_task_layout.addWidget(self.task_combo)

        date_task_layout.addStretch()
        task_layout.addLayout(date_task_layout)

        # 学生选择区域
        student_selection_layout = QVBoxLayout()
        student_selection_layout.addWidget(QLabel("<h4>选择学生</h4>"))

        # 全选/全不选按钮
        select_buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.deselect_all_btn = QPushButton("全不选")
        select_buttons_layout.addWidget(self.select_all_btn)
        select_buttons_layout.addWidget(self.deselect_all_btn)
        select_buttons_layout.addStretch()
        student_selection_layout.addLayout(select_buttons_layout)

        # 学生复选框列表
        self.student_scroll_area = QScrollArea()
        self.student_scroll_area.setWidgetResizable(True)
        self.student_scroll_area.setMaximumHeight(200)
        
        self.student_widget = QWidget()
        self.student_checkboxes_layout = QVBoxLayout(self.student_widget)
        self.student_scroll_area.setWidget(self.student_widget)
        
        student_selection_layout.addWidget(self.student_scroll_area)

        # 提交按钮
        submit_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交记分")
        self.submit_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 16px; background-color: #4CAF50; color: white; }")
        submit_layout.addWidget(self.submit_btn)
        submit_layout.addStretch()
        student_selection_layout.addLayout(submit_layout)

        task_layout.addLayout(student_selection_layout)
        self.main_layout.addLayout(task_layout)

        # 每日任务历史
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("<h3>每日任务历史</h3>"))

        history_search_layout = QHBoxLayout()
        history_search_layout.addWidget(QLabel("查询学号:"))
        self.history_student_id_input = QLineEdit()
        self.history_student_id_input.setPlaceholderText("请输入学号")
        history_search_layout.addWidget(self.history_student_id_input)
        self.search_history_btn = QPushButton("查询历史")
        history_search_layout.addWidget(self.search_history_btn)
        self.load_all_history_btn = QPushButton("显示所有记录")
        history_search_layout.addWidget(self.load_all_history_btn)
        history_search_layout.addStretch()
        history_layout.addLayout(history_search_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["学号", "任务名称", "积分奖励", "时间"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)

        self.main_layout.addLayout(history_layout)

        # 连接信号与槽
        self.task_combo.currentTextChanged.connect(self.on_task_selected)
        self.select_all_btn.clicked.connect(self.select_all_students)
        self.deselect_all_btn.clicked.connect(self.deselect_all_students)
        self.submit_btn.clicked.connect(self.submit_task_scores)
        self.search_history_btn.clicked.connect(self.load_task_history)
        self.load_all_history_btn.clicked.connect(self.load_all_task_history)

    def load_data(self):
        """加载数据"""
        self.load_tasks()
        self.load_students()
        self.load_all_task_history()

    def load_tasks(self):
        """加载每日任务到下拉框"""
        self.task_combo.clear()
        tasks = get_all_daily_task_rules()
        for task_name, score_value in tasks:
            self.task_combo.addItem(f"{task_name} (+{score_value}分)", (task_name, score_value))

    def load_students(self):
        """加载学生复选框"""
        # 清除现有复选框
        for i in reversed(range(self.student_checkboxes_layout.count())):
            child = self.student_checkboxes_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # 添加学生复选框
        self.student_checkboxes = []
        students = get_all_students()
        for student_id, name, score in students:
            display_text = f"{student_id}"
            if name:
                display_text += f" - {name}"
            display_text += f" (当前积分: {score})"
            
            checkbox = QCheckBox(display_text)
            checkbox.setProperty("student_id", student_id)
            self.student_checkboxes.append(checkbox)
            self.student_checkboxes_layout.addWidget(checkbox)

    def on_task_selected(self):
        """当选择任务时的处理"""
        pass  # 可以在这里添加任务选择后的逻辑

    def select_all_students(self):
        """全选学生"""
        for checkbox in self.student_checkboxes:
            checkbox.setChecked(True)

    def deselect_all_students(self):
        """全不选学生"""
        for checkbox in self.student_checkboxes:
            checkbox.setChecked(False)

    def submit_task_scores(self):
        """提交任务记分"""
        # 获取选择的任务
        current_data = self.task_combo.currentData()
        if not current_data:
            QMessageBox.warning(self, "输入错误", "请选择一个每日任务！")
            return

        task_name, score_value = current_data
        
        # 获取选择的日期
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        timestamp = f"{selected_date} {datetime.now().strftime('%H:%M:%S')}"

        # 获取选择的学生
        selected_students = []
        for checkbox in self.student_checkboxes:
            if checkbox.isChecked():
                student_id = checkbox.property("student_id")
                selected_students.append(student_id)

        if not selected_students:
            QMessageBox.warning(self, "输入错误", "请至少选择一个学生！")
            return

        # 批量记分
        success_count = 0
        failed_students = []

        for student_id in selected_students:
            try:
                if add_daily_task_event(student_id, task_name, score_value, timestamp):
                    success_count += 1
                else:
                    failed_students.append(student_id)
            except Exception as e:
                failed_students.append(student_id)
                print(f"为学生 {student_id} 记分失败: {e}")

        # 显示结果
        if success_count > 0:
            result_msg = f"成功为 {success_count} 名学生记分！\n任务: {task_name}\n积分: +{score_value}\n日期: {selected_date}"
            if failed_students:
                result_msg += f"\n\n失败的学生: {', '.join(failed_students)}"
            QMessageBox.information(self, "记分完成", result_msg)
            
            # 刷新数据
            self.load_students()  # 刷新学生积分显示
            self.load_all_task_history()  # 刷新历史记录
            
            # 清除选择
            self.deselect_all_students()
        else:
            QMessageBox.warning(self, "记分失败", f"所有学生记分都失败了！\n失败的学生: {', '.join(failed_students)}")

    def load_task_history(self, student_id=None):
        """加载指定学生的每日任务历史"""
        if student_id is None:
            student_id = self.history_student_id_input.text().strip()
        
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        if not student_id:
            return

        # 获取所有每日任务事件，然后筛选指定学生
        all_tasks = get_all_daily_task_events()
        student_tasks = [t for t in all_tasks if t[0] == student_id]
        
        self.history_table.setRowCount(len(student_tasks))
        for i, task in enumerate(student_tasks):
            self.history_table.setItem(i, 0, QTableWidgetItem(task[0]))  # 学号
            self.history_table.setItem(i, 1, QTableWidgetItem(task[1]))  # 任务名称
            self.history_table.setItem(i, 2, QTableWidgetItem(f"+{task[2]}"))  # 积分奖励
            self.history_table.setItem(i, 3, QTableWidgetItem(task[3]))  # 时间

    def load_all_task_history(self):
        """加载所有每日任务历史"""
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        tasks = get_all_daily_task_events()
        self.history_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.history_table.setItem(i, 0, QTableWidgetItem(task[0]))  # 学号
            self.history_table.setItem(i, 1, QTableWidgetItem(task[1]))  # 任务名称
            self.history_table.setItem(i, 2, QTableWidgetItem(f"+{task[2]}"))  # 积分奖励
            self.history_table.setItem(i, 3, QTableWidgetItem(task[3]))  # 时间

