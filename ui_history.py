from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDateEdit, QCheckBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from database import (get_all_students, get_all_events_in_date_range, search_events_by_rule_name,
                     get_all_score_rules_names, get_all_reward_rules_names, get_all_daily_task_rules_names)

class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 标题
        self.main_layout.addWidget(QLabel("<h1>历史记录查询</h1>"), alignment=Qt.AlignCenter)

        # 筛选条件区域
        filter_group = QGroupBox("筛选条件")
        filter_layout = QFormLayout(filter_group)

        # 时间范围
        time_range_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))  # 默认30天前
        self.start_date_edit.setCalendarPopup(True)
        time_range_layout.addWidget(QLabel("从:"))
        time_range_layout.addWidget(self.start_date_edit)
        
        time_range_layout.addWidget(QLabel("到:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        time_range_layout.addWidget(self.end_date_edit)
        time_range_layout.addStretch()
        
        filter_layout.addRow("时间范围:", time_range_layout)

        # 学生筛选
        student_layout = QHBoxLayout()
        self.student_filter_checkbox = QCheckBox("按学生筛选")
        self.student_combo = QComboBox()
        self.student_combo.setEnabled(False)
        student_layout.addWidget(self.student_filter_checkbox)
        student_layout.addWidget(self.student_combo)
        student_layout.addStretch()
        filter_layout.addRow("学生:", student_layout)

        # 事件类型筛选
        event_type_layout = QHBoxLayout()
        self.event_type_filter_checkbox = QCheckBox("按事件类型筛选")
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItem("积分记录", "score")
        self.event_type_combo.addItem("兑换记录", "reward")
        self.event_type_combo.addItem("每日任务", "daily_task")
        self.event_type_combo.setEnabled(False)
        event_type_layout.addWidget(self.event_type_filter_checkbox)
        event_type_layout.addWidget(self.event_type_combo)
        event_type_layout.addStretch()
        filter_layout.addRow("事件类型:", event_type_layout)

        # 规则名称筛选
        rule_layout = QHBoxLayout()
        self.rule_filter_checkbox = QCheckBox("按规则筛选")
        self.rule_combo = QComboBox()
        self.rule_combo.setEditable(True)
        self.rule_combo.setEnabled(False)
        rule_layout.addWidget(self.rule_filter_checkbox)
        rule_layout.addWidget(self.rule_combo)
        rule_layout.addStretch()
        filter_layout.addRow("规则名称:", rule_layout)

        # 查询按钮
        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("查询")
        self.search_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 16px; background-color: #2196F3; color: white; }")
        self.reset_btn = QPushButton("重置")
        self.export_btn = QPushButton("导出结果")
        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        filter_layout.addRow("操作:", button_layout)

        self.main_layout.addWidget(filter_group)

        # 结果显示区域
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout(result_group)

        # 结果统计
        self.result_stats_label = QLabel("查询结果: 0 条记录")
        result_layout.addWidget(self.result_stats_label)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["学号", "学生姓名", "事件名称", "积分变化", "时间", "事件类型"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setAlternatingRowColors(True)
        result_layout.addWidget(self.result_table)

        self.main_layout.addWidget(result_group)

        # 连接信号与槽
        self.student_filter_checkbox.toggled.connect(self.student_combo.setEnabled)
        self.event_type_filter_checkbox.toggled.connect(self.event_type_combo.setEnabled)
        self.rule_filter_checkbox.toggled.connect(self.rule_combo.setEnabled)
        self.search_btn.clicked.connect(self.search_history)
        self.reset_btn.clicked.connect(self.reset_filters)
        self.export_btn.clicked.connect(self.export_results)

    def load_data(self):
        """加载数据"""
        self.load_students()
        self.load_rules()
        # 默认查询最近30天的记录
        self.search_history()

    def load_students(self):
        """加载学生到下拉框"""
        self.student_combo.clear()
        students = get_all_students()
        for student_id, name, score in students:
            display_text = f"{student_id}"
            if name:
                display_text += f" - {name}"
            self.student_combo.addItem(display_text, student_id)

    def load_rules(self):
        """加载所有规则到下拉框"""
        self.rule_combo.clear()
        
        # 添加积分规则
        score_rules = get_all_score_rules_names()
        for rule in score_rules:
            self.rule_combo.addItem(f"[积分] {rule}", rule)
        
        # 添加兑换规则
        reward_rules = get_all_reward_rules_names()
        for rule in reward_rules:
            self.rule_combo.addItem(f"[兑换] {rule}", rule)
        
        # 添加每日任务规则
        task_rules = get_all_daily_task_rules_names()
        for rule in task_rules:
            self.rule_combo.addItem(f"[任务] {rule}", rule)

    def search_history(self):
        """执行历史记录查询"""
        try:
            # 获取筛选条件
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            student_id = None
            if self.student_filter_checkbox.isChecked():
                student_id = self.student_combo.currentData()
            
            event_type = None
            if self.event_type_filter_checkbox.isChecked():
                event_type = self.event_type_combo.currentData()
            
            # 执行查询
            if self.rule_filter_checkbox.isChecked():
                rule_name = self.rule_combo.currentText()
                if rule_name.startswith("["):
                    # 移除前缀
                    rule_name = rule_name.split("] ", 1)[1] if "] " in rule_name else rule_name
                events = search_events_by_rule_name(rule_name, start_date, end_date)
                # 如果还有其他筛选条件，进一步过滤
                if student_id or event_type:
                    filtered_events = []
                    for event in events:
                        if student_id and event[0] != student_id:
                            continue
                        if event_type and event[4] != event_type:
                            continue
                        filtered_events.append(event)
                    events = filtered_events
            else:
                events = get_all_events_in_date_range(start_date, end_date, student_id, event_type)
            
            # 显示结果
            self.display_results(events)
            
        except Exception as e:
            QMessageBox.critical(self, "查询错误", f"查询历史记录时发生错误：\n{str(e)}")

    def display_results(self, events):
        """显示查询结果"""
        self.result_table.clearContents()
        self.result_table.setRowCount(len(events))
        
        # 获取学生信息映射
        students = get_all_students()
        student_names = {sid: name for sid, name, _ in students}
        
        # 事件类型映射
        event_type_map = {
            "score": "积分记录",
            "reward": "兑换记录", 
            "daily_task": "每日任务"
        }
        
        for i, event in enumerate(events):
            student_id, event_name, score_change, timestamp, event_type = event
            
            # 学号
            self.result_table.setItem(i, 0, QTableWidgetItem(student_id))
            
            # 学生姓名
            student_name = student_names.get(student_id, "未知")
            self.result_table.setItem(i, 1, QTableWidgetItem(student_name))
            
            # 事件名称
            self.result_table.setItem(i, 2, QTableWidgetItem(event_name))
            
            # 积分变化
            score_text = f"{score_change:+d}"  # 显示正负号
            score_item = QTableWidgetItem(score_text)
            if score_change > 0:
                score_item.setForeground(Qt.darkGreen)
            elif score_change < 0:
                score_item.setForeground(Qt.darkRed)
            self.result_table.setItem(i, 3, score_item)
            
            # 时间
            self.result_table.setItem(i, 4, QTableWidgetItem(timestamp))
            
            # 事件类型
            type_text = event_type_map.get(event_type, event_type)
            self.result_table.setItem(i, 5, QTableWidgetItem(type_text))
        
        # 更新统计信息
        total_records = len(events)
        total_score_change = sum(event[2] for event in events)
        self.result_stats_label.setText(f"查询结果: {total_records} 条记录，总积分变化: {total_score_change:+d}")

    def reset_filters(self):
        """重置筛选条件"""
        # 重置时间范围为最近30天
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        
        # 重置复选框
        self.student_filter_checkbox.setChecked(False)
        self.event_type_filter_checkbox.setChecked(False)
        self.rule_filter_checkbox.setChecked(False)
        
        # 重置下拉框
        self.student_combo.setCurrentIndex(0)
        self.event_type_combo.setCurrentIndex(0)
        self.rule_combo.setCurrentIndex(0)
        
        # 重新查询
        self.search_history()

    def export_results(self):
        """导出查询结果"""
        try:
            from PySide6.QtWidgets import QFileDialog
            import csv
            
            # 选择保存文件
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "导出查询结果", 
                f"历史记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV文件 (*.csv);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            # 导出数据
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入标题行
                headers = ["学号", "学生姓名", "事件名称", "积分变化", "时间", "事件类型"]
                writer.writerow(headers)
                
                # 写入数据行
                for row in range(self.result_table.rowCount()):
                    row_data = []
                    for col in range(self.result_table.columnCount()):
                        item = self.result_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "导出成功", f"查询结果已导出到：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出查询结果时发生错误：\n{str(e)}")

    def load_data(self):
        """刷新数据"""
        self.load_students()
        self.load_rules()
        self.search_history()

