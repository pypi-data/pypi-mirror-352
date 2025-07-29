from pydantic import BaseModel
from typing import Optional, List, Union

class Config(BaseModel):
    api_base_url: str = "https://hacker-news.firebaseio.com/v0"
    api_timeout: int = 10  # 请求超时时间，单位秒
    
    auto_broadcast: bool = False  # 是否开启定时播报功能
    broadcast_interval: int = 3600  # 定时播报间隔，单位秒
    broadcast_mode: str = "interval"  # 播报模式，"interval"为间隔模式，"cron"为定时模式
    broadcast_cron: str = "0 8 * * *"  # cron表达式，默认每天早上8点
    max_items_per_request: int = 10  # 单次请求最大获取条数
    broadcast_groups: List[int] = []  # 定时播报的群组列表
    broadcast_articles_count: int = 5  # 每次播报的文章数量
    broadcast_header_format: str = "[BROADCAST] {time} Hacker News Update"  # 播报消息头部格式，{time}会被替换为当前时间
