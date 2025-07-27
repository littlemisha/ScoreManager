# PyInstaller 打包说明

## 问题解决

原代码在PyInstaller打包后无法运行的主要原因是路径问题。已修复的内容：

### 1. 路径获取逻辑修复 (database.py)
```python
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
```

### 2. 主程序优化 (main.py)
- 添加了高DPI支持
- 改进了应用程序初始化
- 增强了错误处理

### 3. PyInstaller配置文件 (main.spec)
- 明确指定了PySide6相关模块
- 优化了打包配置

## 推荐的打包命令

### 方法1：使用配置文件（推荐）
```bash
pyinstaller main.spec
```

### 方法2：直接命令行
```bash
pyinstaller --onefile --windowed --name=ScoreManager main.py
```

### 方法3：详细配置
```bash
pyinstaller --onefile --windowed --name=ScoreManager --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtWidgets --hidden-import=PySide6.QtGui main.py
```

## 打包后的文件结构

打包成功后，exe文件运行时会在同目录下自动创建data文件夹：

```
ScoreManager.exe
data/
├── students.csv
├── score_events.csv
├── score_rules.csv
└── settings.json
```

## 测试建议

1. 在打包前先测试Python脚本是否正常运行
2. 打包后在不同的目录下测试exe文件
3. 确认data文件夹能正常创建和读写

## 常见问题解决

### 问题1：exe运行时闪退
- 使用命令行运行exe查看错误信息
- 检查是否缺少必要的DLL文件

### 问题2：找不到模块
- 在spec文件中添加hiddenimports
- 使用--hidden-import参数

### 问题3：路径问题
- 确认使用了修复后的get_data_dir()函数
- 检查sys.frozen的判断逻辑

## 版本兼容性

- Python 3.7+
- PySide6 6.0+
- PyInstaller 4.0+

