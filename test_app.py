
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# 确保可以导入database模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from database import init_db, add_student, get_all_students, update_student_name, delete_student, get_student_by_id, \
                     add_score_rule, get_all_score_rules, delete_score_rule, \
                     add_score_event, get_score_events_by_student, \
                     add_reward_event, get_reward_events_by_student

class TestDatabaseFunctions(unittest.TestCase):

    def setUp(self):
        # 设置一个临时的数据库文件用于测试
        self.test_db_path = os.path.join(os.path.dirname(__file__), 'data', 'test_score_manager.db')
        # 备份原始的get_db_path，并替换为测试路径
        self.original_get_db_path = MagicMock(return_value=self.test_db_path)
        patcher = patch('database.get_db_path', self.original_get_db_path)
        self.mock_get_db_path = patcher.start()
        self.addCleanup(patcher.stop)

        # 每次测试前初始化数据库
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        init_db()

    def tearDown(self):
        # 每次测试后删除数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_add_student(self):
        self.assertTrue(add_student('S001', '张三'))
        self.assertFalse(add_student('S001', '李四')) # 重复学号
        students = get_all_students()
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0][0], 'S001')
        self.assertEqual(students[0][1], '张三')
        self.assertEqual(students[0][2], 0)

    def test_update_student_name(self):
        add_student('S002', '王五')
        update_student_name('S002', '王小五')
        student = get_student_by_id('S002')
        self.assertEqual(student[1], '王小五')

    def test_delete_student(self):
        add_student('S003', '赵六')
        delete_student('S003')
        student = get_student_by_id('S003')
        self.assertIsNone(student)

    def test_add_score_rule(self):
        self.assertTrue(add_score_rule('做操+1', 1))
        self.assertFalse(add_score_rule('做操+1', 2)) # 重复规则名
        rules = get_all_score_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0][0], '做操+1')
        self.assertEqual(rules[0][1], 1)

    def test_delete_score_rule(self):
        add_score_rule('迟到-2', -2)
        delete_score_rule('迟到-2')
        rules = get_all_score_rules()
        self.assertEqual(len(rules), 0)

    def test_add_score_event(self):
        add_student('S004', '钱七')
        add_score_rule('好人好事+5', 5)
        add_score_event('S004', '好人好事+5', 5)
        student = get_student_by_id('S004')
        self.assertEqual(student[2], 5)
        events = get_score_events_by_student('S004')
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0], '好人好事+5')
        self.assertEqual(events[0][1], 5)

    def test_add_reward_event(self):
        add_student('S005', '孙八')
        add_score_event('S005', '初始积分', 100)
        add_reward_event('S005', '铅笔', 10)
        student = get_student_by_id('S005')
        self.assertEqual(student[2], 90)
        rewards = get_reward_events_by_student('S005')
        self.assertEqual(len(rewards), 1)
        self.assertEqual(rewards[0][0], '铅笔')
        self.assertEqual(rewards[0][1], 10)

if __name__ == '__main__':
    unittest.main()



