import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout
from PySide6.QtCore import Qt

from database import init_db
from ui_main_page import MainPage
from ui_settings import SettingsPage
from ui_scoring import ScoringPage
from ui_rewards import RewardsPage
from ui_daily_tasks import DailyTasksPage
from ui_history import HistoryPage

class ScoreManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("班级积分管理系统")
        self.setGeometry(100, 100, 1200, 800) # 调整窗口大小以适应更多内容

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget) # 使用QHBoxLayout来放置导航和内容区域

        self.stacked_widget = QStackedWidget()
        
        self.init_db_connection()
        self.init_ui()

    def init_ui(self):
        # 导航按钮区域
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10) # 设置边距
        nav_layout.setSpacing(10) # 设置按钮间距

        self.btn_main_page = QPushButton("主页 (积分排名)")
        self.btn_settings = QPushButton("设置")
        self.btn_scoring = QPushButton("记分")
        self.btn_rewards = QPushButton("兑换")
        self.btn_daily_tasks = QPushButton("每日任务")
        self.btn_history = QPushButton("历史记录")

        # 设置按钮样式
        button_style = "QPushButton { padding: 10px; font-size: 16px; }"
        self.btn_main_page.setStyleSheet(button_style)
        self.btn_settings.setStyleSheet(button_style)
        self.btn_scoring.setStyleSheet(button_style)
        self.btn_rewards.setStyleSheet(button_style)
        self.btn_daily_tasks.setStyleSheet(button_style)
        self.btn_history.setStyleSheet(button_style)

        nav_layout.addWidget(self.btn_main_page)
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addWidget(self.btn_scoring)
        nav_layout.addWidget(self.btn_rewards)
        nav_layout.addWidget(self.btn_daily_tasks)
        nav_layout.addWidget(self.btn_history)
        nav_layout.addStretch() # 将按钮推到顶部

        # 创建导航区域的容器
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedWidth(200) # 设置导航区域宽度
        nav_widget.setStyleSheet("QWidget { background-color: #f0f0f0; }")

        # 页面区域
        self.main_page = MainPage()
        self.settings_page = SettingsPage()
        self.scoring_page = ScoringPage()
        self.rewards_page = RewardsPage()
        self.daily_tasks_page = DailyTasksPage()
        self.history_page = HistoryPage()

        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.scoring_page)
        self.stacked_widget.addWidget(self.rewards_page)
        self.stacked_widget.addWidget(self.daily_tasks_page)
        self.stacked_widget.addWidget(self.history_page)

        # 将导航和页面区域添加到主布局
        self.main_layout.addWidget(nav_widget)
        self.main_layout.addWidget(self.stacked_widget)

        # 连接信号与槽
        self.btn_main_page.clicked.connect(lambda: self.switch_page(0))
        self.btn_settings.clicked.connect(lambda: self.switch_page(1))
        self.btn_scoring.clicked.connect(lambda: self.switch_page(2))
        self.btn_rewards.clicked.connect(lambda: self.switch_page(3))
        self.btn_daily_tasks.clicked.connect(lambda: self.switch_page(4))
        self.btn_history.clicked.connect(lambda: self.switch_page(5))

        # 默认显示主页
        self.switch_page(0)

    def init_db_connection(self):
        """初始化数据库连接"""
        try:
            init_db()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {e}")

    def switch_page(self, index):
        """切换页面"""
        self.stacked_widget.setCurrentIndex(index)
        
        # 刷新当前页面的数据
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
        elif hasattr(current_widget, 'load_students'):
            current_widget.load_students()
        elif hasattr(current_widget, 'load_student_rankings'):
            current_widget.load_student_rankings()

def main():
    """主函数，处理PyInstaller兼容性"""
    # 设置应用程序属性
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("班级积分管理系统")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("ScoreManager")
    
    window = ScoreManagerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

