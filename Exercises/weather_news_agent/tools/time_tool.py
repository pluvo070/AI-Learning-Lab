from datetime import datetime
from langchain.tools import tool

@tool
def get_current_time():
    """获取当前的日期和时间。在搜索天气或新闻前应先调用此工具确定日期。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")