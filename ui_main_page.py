from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QPushButton
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from database import get_all_students, get_all_events_in_date_range

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_student_rankings()

    def setup_ui(self):
        # 标题
        self.main_layout.addWidget(QLabel("<h1>学生积分排名</h1>"), alignment=Qt.AlignCenter)

        # 时间范围筛选
        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("起始日期:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        
        # 设置默认时间为当前周的周一
        today = datetime.now().date()
        days_since_monday = today.weekday()  # 0=Monday, 6=Sunday
        monday = today - timedelta(days=days_since_monday)
        self.start_date_edit.setDate(QDate.fromString(monday.strftime('%Y-%m-%d'), Qt.ISODate))
        
        date_filter_layout.addWidget(self.start_date_edit)

        date_filter_layout.addWidget(QLabel("结束日期:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        # 设置默认时间为今天
        self.end_date_edit.setDate(QDate.currentDate())
        date_filter_layout.addWidget(self.end_date_edit)

        self.filter_btn = QPushButton("筛选")
        date_filter_layout.addWidget(self.filter_btn)
        
        # 添加重置按钮
        self.reset_btn = QPushButton("重置到本周")
        date_filter_layout.addWidget(self.reset_btn)
        
        date_filter_layout.addStretch()
        self.main_layout.addLayout(date_filter_layout)

        # 积分排名表格
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(4)
        self.ranking_table.setHorizontalHeaderLabels(["排名", "学号", "姓名", "总积分"])
        self.ranking_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ranking_table.setEditTriggers(QTableWidget.NoEditTriggers) # 不可编辑
        self.ranking_table.setSelectionBehavior(QTableWidget.SelectRows) # 整行选择
        self.ranking_table.setAlternatingRowColors(True)  # 交替行颜色
        self.main_layout.addWidget(self.ranking_table)

        # 连接信号与槽
        self.filter_btn.clicked.connect(self.load_student_rankings)
        self.reset_btn.clicked.connect(self.reset_to_current_week)

    def reset_to_current_week(self):
        """重置时间范围到当前周"""
        today = datetime.now().date()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        self.start_date_edit.setDate(QDate.fromString(monday.strftime('%Y-%m-%d'), Qt.ISODate))
        self.end_date_edit.setDate(QDate.currentDate())
        
        # 重新加载数据
        self.load_student_rankings()

    def load_student_rankings(self):
        """加载学生积分排名"""
        start_date = self.start_date_edit.date().toString(Qt.ISODate)
        end_date = self.end_date_edit.date().toString(Qt.ISODate)

        # 获取所有学生
        students = get_all_students()
        student_info = {sid: {"name": name, "current_score": score} for sid, name, score in students}
        
        # 获取指定时间范围内的所有事件
        events = get_all_events_in_date_range(start_date, end_date)
        
        # 计算每个学生在指定时间范围内的积分变化
        student_scores = {}
        for student_id, name, current_score in students:
            student_scores[student_id] = {"name": name, "score": 0}
        
        # 累计积分变化
        for event in events:
            student_id, event_name, score_change, timestamp, event_type = event
            if student_id in student_scores:
                student_scores[student_id]["score"] += score_change

        # 根据积分排序（从高到低）
        sorted_students = sorted(student_scores.items(), key=lambda item: item[1]["score"], reverse=True)

        # 设置表格行数
        self.ranking_table.setRowCount(len(sorted_students))
        for i, (student_id, data) in enumerate(sorted_students):
            # 排名
            rank_item = QTableWidgetItem(str(i + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.ranking_table.setItem(i, 0, rank_item)
            
            # 学号
            id_item = QTableWidgetItem(student_id)
            id_item.setTextAlignment(Qt.AlignCenter)
            self.ranking_table.setItem(i, 1, id_item)
            
            # 姓名
            name_item = QTableWidgetItem(data["name"] if data["name"] else "无")
            name_item.setTextAlignment(Qt.AlignCenter)
            self.ranking_table.setItem(i, 2, name_item)
            
            # 总积分
            score_item = QTableWidgetItem(str(data["score"]))
            score_item.setTextAlignment(Qt.AlignCenter)
            # 根据积分设置颜色
            if data["score"] > 0:
                score_item.setForeground(Qt.darkGreen)
            elif data["score"] < 0:
                score_item.setForeground(Qt.darkRed)
            self.ranking_table.setItem(i, 3, score_item)