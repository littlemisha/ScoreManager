from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from database import get_all_students, add_reward_event, get_all_reward_events, get_all_reward_rules

class RewardsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 标题
        self.main_layout.addWidget(QLabel("<h1>积分兑换</h1>"), alignment=Qt.AlignCenter)

        # 兑换操作
        exchange_layout = QVBoxLayout()
        exchange_layout.addWidget(QLabel("<h3>兑换奖品/惩罚</h3>"))

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("学号:"))
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("请输入学号")
        form_layout.addWidget(self.student_id_input)

        form_layout.addWidget(QLabel("兑换项目:"))
        self.reward_combo = QComboBox()
        self.reward_combo.setEditable(True)
        self.reward_combo.setPlaceholderText("选择或输入兑换项目")
        form_layout.addWidget(self.reward_combo)

        form_layout.addWidget(QLabel("积分消耗:"))
        self.score_cost_input = QLineEdit()
        self.score_cost_input.setPlaceholderText("请输入积分消耗")
        self.score_cost_input.setValidator(self.create_int_validator())
        form_layout.addWidget(self.score_cost_input)

        self.exchange_btn = QPushButton("兑换")
        form_layout.addWidget(self.exchange_btn)
        form_layout.addStretch()
        exchange_layout.addLayout(form_layout)

        self.main_layout.addLayout(exchange_layout)

        # 兑换历史
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("<h3>兑换历史</h3>"))

        history_search_layout = QHBoxLayout()
        history_search_layout.addWidget(QLabel("查询学号:"))
        self.history_student_id_input = QLineEdit()
        self.history_student_id_input.setPlaceholderText("请输入学号")
        history_search_layout.addWidget(self.history_student_id_input)
        self.search_history_btn = QPushButton("查询历史")
        history_search_layout.addWidget(self.search_history_btn)
        self.load_all_history_btn = QPushButton("显示所有兑换记录")
        history_search_layout.addWidget(self.load_all_history_btn)
        history_search_layout.addStretch()
        history_layout.addLayout(history_search_layout)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["学号", "兑换项目", "积分消耗", "时间"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)

        self.main_layout.addLayout(history_layout)

        # 连接信号与槽
        self.exchange_btn.clicked.connect(self.exchange_action)
        self.search_history_btn.clicked.connect(self.load_reward_history)
        self.load_all_history_btn.clicked.connect(self.load_all_reward_history)
        self.reward_combo.currentTextChanged.connect(self.on_reward_selected)

    def create_int_validator(self):
        from PySide6.QtGui import QIntValidator
        return QIntValidator()

    def load_data(self):
        """加载学生数据和兑换规则"""
        students = get_all_students()
        print(f"加载了 {len(students)} 名学生数据")
        
        # 加载兑换规则到下拉框
        self.load_reward_rules()

    def load_reward_rules(self):
        """加载兑换规则到下拉框"""
        self.reward_combo.clear()
        rules = get_all_reward_rules()
        for rule_name, score_cost in rules:
            self.reward_combo.addItem(f"{rule_name} ({score_cost}分)", (rule_name, score_cost))

    def on_reward_selected(self):
        """当选择兑换项目时，自动填入积分消耗"""
        current_data = self.reward_combo.currentData()
        if current_data:
            rule_name, score_cost = current_data
            self.score_cost_input.setText(str(score_cost))

    def exchange_action(self):
        student_id = self.student_id_input.text().strip()
        reward_name = self.reward_combo.currentText().strip()
        score_cost_str = self.score_cost_input.text().strip()

        if not student_id or not reward_name or not score_cost_str:
            QMessageBox.warning(self, "输入错误", "学号、兑换项目和积分消耗都不能为空！")
            return

        try:
            score_cost = int(score_cost_str)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "积分消耗必须是整数！")
            return

        try:
            # 使用新的兑换事件函数
            if add_reward_event(student_id, reward_name, score_cost):
                QMessageBox.information(self, "成功", f"学生 {student_id} 已成功兑换 '{reward_name}'，消耗积分 {score_cost}！")
                self.student_id_input.clear()
                self.reward_combo.setCurrentIndex(-1)
                self.score_cost_input.clear()
                self.load_all_reward_history()  # 刷新兑换历史记录
            else:
                QMessageBox.warning(self, "失败", "兑换失败，请检查学号是否存在或积分是否足够。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"兑换失败: {e}")

    def load_reward_history(self, student_id=None):
        """加载指定学生的兑换历史"""
        if student_id is None:
            student_id = self.history_student_id_input.text().strip()
        
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        if not student_id:
            return

        # 获取所有兑换事件，然后筛选指定学生
        all_rewards = get_all_reward_events()
        student_rewards = [r for r in all_rewards if r[0] == student_id]
        
        self.history_table.setRowCount(len(student_rewards))
        for i, reward in enumerate(student_rewards):
            self.history_table.setItem(i, 0, QTableWidgetItem(reward[0]))  # 学号
            self.history_table.setItem(i, 1, QTableWidgetItem(reward[1]))  # 兑换项目
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{reward[2]}"))  # 积分消耗
            self.history_table.setItem(i, 3, QTableWidgetItem(reward[3]))  # 时间

    def load_all_reward_history(self):
        """加载所有兑换历史"""
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        rewards = get_all_reward_events()
        self.history_table.setRowCount(len(rewards))
        for i, reward in enumerate(rewards):
            self.history_table.setItem(i, 0, QTableWidgetItem(reward[0]))  # 学号
            self.history_table.setItem(i, 1, QTableWidgetItem(reward[1]))  # 兑换项目
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{reward[2]}"))  # 积分消耗
            self.history_table.setItem(i, 3, QTableWidgetItem(reward[3]))  # 时间