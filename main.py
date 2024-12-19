import sys
import logging
from PyQt6.QtWidgets import QApplication
from app.ui.windows.main_window import MainWindow
from app.database.sqlite import DatabaseManager

def setup_logging():
    """配置日志"""
    # 创建日志格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 配置文件处理器
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 添加处理器
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 设置其他模块的日志级别
    logging.getLogger('app').setLevel(logging.INFO)
    
    # 记录初始化完成
    root_logger.info("日志系统初始化完成")

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 初始化数据库
    db_manager = DatabaseManager("novels.db")
    db_manager.init_database()
    
    # 创建并显示主窗口
    window = MainWindow(db_manager)
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 