import asyncio
import nonebot
from nonebot import require
from nonebot.adapters.onebot.v11 import MessageSegment
from typing import Dict, List, Set, Union
from datetime import datetime
import re

from . import plugin_config
from .data_source import get_top_stories, format_item

def parse_cron_expression(cron_expr: str) -> Dict[str, str]:
    parts = cron_expr.split()
    if len(parts) != 5:
        nonebot.logger.warning(f"Cron表达式格式错误: {cron_expr}，使用默认值: '0 8 * * *'")
        parts = ["0", "8", "*", "*", "*"]  # 默认每天早八
    
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }

scheduler = require("nonebot_plugin_apscheduler").scheduler

broadcasted_ids: Set[int] = set()

async def hacker_news_broadcast():
    global broadcasted_ids
    
    stories = await get_top_stories(plugin_config.broadcast_articles_count)
    if not stories:
        nonebot.logger.warning("获取热门文章失败，本次播报取消")
        return
    
    new_stories = [story for story in stories if story["id"] not in broadcasted_ids]
    if not new_stories:
        nonebot.logger.info("没有新的热门文章，本次播报取消")
        return
    
    group_list = plugin_config.broadcast_groups
    if not group_list:
        nonebot.logger.info("播报群组列表为空，无法进行播报")
        return

    # 更新已播报ID集合（保留最近100个）
    new_ids = [story["id"] for story in new_stories]
    broadcasted_ids.update(new_ids)
    if len(broadcasted_ids) > 100:
        broadcasted_ids = set(list(broadcasted_ids)[-100:])
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_format = plugin_config.broadcast_header_format
    message = f"{header_format.format(time=current_time)}\n\n"
    message += "\n\n".join([format_item(story) for story in new_stories])
    
    bot_list = nonebot.get_bots()
    if not bot_list:
        nonebot.logger.warning("没有Bot实例连接，无法播报热门文章")
        return
    
    for bot_id, bot in bot_list.items():
        group_list = plugin_config.broadcast_groups
        
        for group_id in group_list:
            try:
                await bot.send_group_msg(group_id=group_id, message=message)
                nonebot.logger.info(f"成功向群 {group_id} 播报热门文章")
            except Exception as e:
                nonebot.logger.error(f"向群 {group_id} 播报文章失败: {e}")
            
            # 避免频繁发送消息触发风控
            await asyncio.sleep(1)
