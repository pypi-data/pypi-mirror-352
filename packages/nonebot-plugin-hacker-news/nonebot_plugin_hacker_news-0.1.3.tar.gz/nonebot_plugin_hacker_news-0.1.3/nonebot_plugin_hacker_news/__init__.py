import httpx
import nonebot
import asyncio
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

from nonebot import on_command, require, get_plugin_config
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config
plugin_config = get_plugin_config(Config)

from .data_source import (
    get_top_stories,
    get_new_stories,
    get_best_stories,
    get_item_details,
    get_story_with_comments,
    format_item,
    format_item_with_comments,
)

from . import broadcaster

__plugin_meta__ = PluginMetadata(
    name="Hacker News",
    description="获取Hacker News热门文章并进行播报",
    usage="""
    使用方法:
    /hn：获取Hacker News热门文章，默认获取前5条
    /hn top [数量]：获取热门文章，默认5条
    /hn new [数量]：获取最新文章，默认5条
    /hn best [数量]：获取最佳文章，默认5条
    /hn item [ID]：获取特定文章详情
    /hn comments [ID]：获取特定文章及其评论
    
    定时播报控制:
    /hn_broadcast on - 开启定时播报
    /hn_broadcast off - 关闭定时播报
    /hn_broadcast status - 查看播报状态
    /hn_broadcast mode [interval|cron] - 设置播报模式
    /hn_broadcast interval 秒数 - 设置播报间隔(最小60秒)
    /hn_broadcast cron '分 时 日 月 星期' - 设置播报时间
    例如: hn_broadcast cron '0 8 * * *' 表示每天早上8点
    /hn_broadcast header '格式字符串' - 设置播报消息头部格式
    例如: '[重要通知] {time} HN更新'
    """,
    config=Config,
    extra={},
    type="application",
    homepage="https://github.com/perfsakuya/nonebot-plugin-hacker-news",
    supported_adapters={"~onebot.v11"},
)

def auto_start_broadcast():
    if not plugin_config.auto_broadcast:
        return
        
    try:
        scheduler = require("nonebot_plugin_apscheduler").scheduler
        job = scheduler.get_job("hacker_news_auto_broadcast")

        if job:
            return

        if plugin_config.broadcast_mode == "cron":
            cron_params = broadcaster.parse_cron_expression(plugin_config.broadcast_cron)
            scheduler.add_job(
                broadcaster.hacker_news_broadcast,
                "cron",
                id="hacker_news_auto_broadcast",
                **cron_params
            )
            nonebot.logger.info(f"启动定时播报: '{plugin_config.broadcast_cron}'")
        else:
            scheduler.add_job(
                broadcaster.hacker_news_broadcast,
                "interval",
                seconds=plugin_config.broadcast_interval,
                id="hacker_news_auto_broadcast"
            )
            nonebot.logger.info(f"启动定时播报: 每 {plugin_config.broadcast_interval} 秒播报一次")
    except Exception as e:
        nonebot.logger.error(f"启动定时播报失败: {e}")

auto_start_broadcast()

hacker_news = on_command("hn", aliases={"hackernews"}, priority=5, block=True)

@hacker_news.handle()
async def handle_hacker_news(event: MessageEvent, args: Message = CommandArg()):
    arg_text = args.extract_plain_text().strip()
    cmd_parts = arg_text.split()
    
    # 默认处理，没有参数就获取热门文章
    if not arg_text:
        await hacker_news.send("正在获取Hacker News热门文章...")
        stories = await get_top_stories(5)
        if stories:
            formatted_stories = "\n\n".join([format_item(story) for story in stories])
            await hacker_news.finish(f"[HOT] Hacker News Top Stories\n\n{formatted_stories}")
        else:
            await hacker_news.finish("获取文章失败，请稍后再试。")
        return
    
    # 获取热门文章
    if cmd_parts[0].lower() == "top":
        count = 5  # 默认获取5条
        if len(cmd_parts) > 1 and cmd_parts[1].isdigit():
            count = min(int(cmd_parts[1]), 10)  # 限制最多获取10条
        
        await hacker_news.send(f"正在获取{count}条热门文章...")
        stories = await get_top_stories(count)
        if stories:
            formatted_stories = "\n\n".join([format_item(story) for story in stories])
            await hacker_news.finish(f"[HOT] Hacker News Top Stories\n\n{formatted_stories}")
        else:
            await hacker_news.finish("获取文章失败，请稍后再试。")
        return
    
    # 获取最新文章
    elif cmd_parts[0].lower() == "new":
        count = 5
        if len(cmd_parts) > 1 and cmd_parts[1].isdigit():
            count = min(int(cmd_parts[1]), 10)
        
        await hacker_news.send(f"正在获取{count}条最新文章...")
        stories = await get_new_stories(count)
        if stories:
            formatted_stories = "\n\n".join([format_item(story) for story in stories])
            await hacker_news.finish(f"[NEW] Hacker News Latest Stories\n\n{formatted_stories}")
        else:
            await hacker_news.finish("获取文章失败，请稍后再试。")
        return
    
    # 获取最佳文章
    elif cmd_parts[0].lower() == "best":
        count = 5
        if len(cmd_parts) > 1 and cmd_parts[1].isdigit():
            count = min(int(cmd_parts[1]), 10)
        
        await hacker_news.send(f"正在获取{count}条最佳文章...")
        stories = await get_best_stories(count)
        if stories:
            formatted_stories = "\n\n".join([format_item(story) for story in stories])
            await hacker_news.finish(f"[BEST] Hacker News Best Stories\n\n{formatted_stories}")
        else:
            await hacker_news.finish("获取文章失败，请稍后再试。")
        return
    
    # 获取特定文章详情
    elif cmd_parts[0].lower() == "item" and len(cmd_parts) > 1 and cmd_parts[1].isdigit():
        item_id = int(cmd_parts[1])
        await hacker_news.send(f"正在获取文章详情（ID: {item_id}）...")
        item = await get_item_details(item_id)
        if item:
            formatted_item = format_item(item)
            await hacker_news.finish(f"[DETAIL] Story Details\n\n{formatted_item}")
        else:
            await hacker_news.finish(f"获取文章 {item_id} 失败，请检查ID是否正确。")
        return
    
    # 获取文章及其评论
    elif cmd_parts[0].lower() == "comments" and len(cmd_parts) > 1 and cmd_parts[1].isdigit():
        item_id = int(cmd_parts[1])
        await hacker_news.send(f"正在获取文章及评论（ID: {item_id}）...")
        result = await get_story_with_comments(item_id, 3)  # 获取前3条评论
        if result:
            formatted_result = format_item_with_comments(result['story'], result['comments'])
            await hacker_news.finish(f"[THREAD] Story With Comments\n\n{formatted_result}")
        else:
            await hacker_news.finish(f"获取文章 {item_id} 及其评论失败，请检查ID是否正确。")
        return
    
    else:
        await hacker_news.finish(__plugin_meta__.usage)

# 定时播报控制命令
hacker_news_broadcast = on_command("hn_broadcast", aliases={"hn广播"}, priority=5, block=True)

@hacker_news_broadcast.handle()
async def handle_broadcast_control(event: MessageEvent, args: Message = CommandArg()):
    scheduler = require("nonebot_plugin_apscheduler").scheduler
    arg_text = args.extract_plain_text().strip().lower() 
    if arg_text == "on" or arg_text == "开启":
        job = scheduler.get_job("hacker_news_auto_broadcast")
        if job:
            await hacker_news_broadcast.finish("定时播报已经处于开启状态！")

        if plugin_config.broadcast_mode == "cron":
            # 使用cron模式
            cron_params = broadcaster.parse_cron_expression(plugin_config.broadcast_cron)
            scheduler.add_job(
                broadcaster.hacker_news_broadcast,
                "cron",
                id="hacker_news_auto_broadcast",
                **cron_params
            )
            await hacker_news_broadcast.finish(f"定时播报已开启！使用定时模式，cron表达式: '{plugin_config.broadcast_cron}'")
        else:
            # 使用间隔模式
            scheduler.add_job(
                broadcaster.hacker_news_broadcast,
                "interval",
                seconds=plugin_config.broadcast_interval,
                id="hacker_news_auto_broadcast"
            )
            await hacker_news_broadcast.finish(f"定时播报已开启！使用间隔模式，每 {plugin_config.broadcast_interval} 秒播报一次")
    
    # 关闭定时播报
    elif arg_text == "off" or arg_text == "关闭":
        job = scheduler.get_job("hacker_news_auto_broadcast")
        if job:
            scheduler.remove_job("hacker_news_auto_broadcast")
            await hacker_news_broadcast.finish("定时播报已关闭！")
        else:
            await hacker_news_broadcast.finish("定时播报已经处于关闭状态！")
    
    # 查看定时播报状态
    elif arg_text == "status" or arg_text == "状态":
        job = scheduler.get_job("hacker_news_auto_broadcast")
        if job:
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            mode = "定时模式" if plugin_config.broadcast_mode == "cron" else "间隔模式"
            mode_detail = f"cron表达式: '{plugin_config.broadcast_cron}'" if plugin_config.broadcast_mode == "cron" else f"间隔: {plugin_config.broadcast_interval} 秒"
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header_format = plugin_config.broadcast_header_format
            
            await hacker_news_broadcast.finish(
                f"[STATUS] 定时播报已开启\n"
                f"模式: {mode}\n"
                f"设置: {mode_detail}\n"
                f"下次播报时间: {next_run}\n"
                f"播报文章数量: {plugin_config.broadcast_articles_count}\n"
                f"播报群组数量: {len(plugin_config.broadcast_groups)}\n"
                f"播报头部格式: '{header_format}'"
            )
        else:
            await hacker_news_broadcast.finish("定时播报当前已关闭。")
    
    # 设置播报间隔（间隔模式）
    elif arg_text.startswith("interval ") or arg_text.startswith("间隔 "):
        parts = arg_text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            await hacker_news_broadcast.finish("间隔设置格式错误，请使用: hn_broadcast interval 数字(秒)")
            return
        
        interval = int(parts[1])
        if interval < 60:
            await hacker_news_broadcast.finish("播报间隔不能小于60秒，以防止频繁播报。")
            return
        
        # 更新配置
        plugin_config.broadcast_interval = interval
        plugin_config.broadcast_mode = "interval"
        
        # 重新设置任务间隔
        job = scheduler.get_job("hacker_news_auto_broadcast")
        if job:
            scheduler.reschedule_job("hacker_news_auto_broadcast", trigger="interval", seconds=interval)
            await hacker_news_broadcast.finish(f"定时播报间隔已设置为 {interval} 秒，使用间隔模式。")
        else:
            await hacker_news_broadcast.finish(f"定时播报间隔已设置为 {interval} 秒，使用间隔模式，但播报功能当前已关闭。")
    
    # 设置定时播报时间（cron模式）
    elif arg_text.startswith("cron ") or arg_text.startswith("定时 "):
        parts = arg_text.split(maxsplit=1)
        if len(parts) != 2:
            await hacker_news_broadcast.finish("定时设置格式错误，请使用: hn_broadcast cron '分 时 日 月 星期'")
            return
        
        cron_expr = parts[1].strip().strip("'").strip('"')
        if not re.match(r"^(\S+\s+){4}\S+$", cron_expr):
            await hacker_news_broadcast.finish("cron表达式格式错误，正确格式为: '分 时 日 月 星期'，例如 '0 8 * * *' 表示每天早上8点")
            return
        
        try:
            # 测试cron表达式是否有效
            cron_params = broadcaster.parse_cron_expression(cron_expr)
            
            # 更新配置
            plugin_config.broadcast_cron = cron_expr
            plugin_config.broadcast_mode = "cron"
            
            # 重新设置定时任务
            job = scheduler.get_job("hacker_news_auto_broadcast")
            if job:
                scheduler.reschedule_job("hacker_news_auto_broadcast", trigger="cron", **cron_params)
                await hacker_news_broadcast.finish(f"定时播报时间已设置为 '{cron_expr}'，使用定时模式。")
            else:
                await hacker_news_broadcast.finish(f"定时播报时间已设置为 '{cron_expr}'，使用定时模式，但播报功能当前已关闭。")
        except Exception as e:
            await hacker_news_broadcast.finish(f"设置定时播报时间失败: {e}")
    
    # 设置播报模式
    elif arg_text.startswith("mode ") or arg_text.startswith("模式 "):
        parts = arg_text.split()
        if len(parts) != 2 or parts[1] not in ["interval", "cron", "间隔", "定时"]:
            await hacker_news_broadcast.finish("模式设置格式错误，请使用: hn_broadcast mode [interval|cron]")
            return
        
        mode = parts[1]
        if mode in ["cron", "定时"]:
            plugin_config.broadcast_mode = "cron"
            await hacker_news_broadcast.finish(f"定时播报模式已设置为定时模式，将按照 '{plugin_config.broadcast_cron}' 进行播报。")
        else:
            plugin_config.broadcast_mode = "interval"
            await hacker_news_broadcast.finish(f"定时播报模式已设置为间隔模式，将每隔 {plugin_config.broadcast_interval} 秒进行播报。")
            
    # 设置播报消息头部格式
    elif arg_text.startswith("header ") or arg_text.startswith("头部 "):
        parts = arg_text.split(maxsplit=1)
        if len(parts) != 2:
            await hacker_news_broadcast.finish("头部格式设置错误，请使用: hn_broadcast header '格式字符串'")
            return
        
        header_format = parts[1].strip().strip("'").strip('"')

        plugin_config.broadcast_header_format = header_format
        
        # 提供一个当前时间的示例，展示效果
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        example = header_format.format(time=current_time)
        
        await hacker_news_broadcast.finish(f"定时播报头部格式已设置为: '{header_format}'\n示例效果: '{example}'")
    
    # 使用帮助
    else:
        usage = """
定时播报控制命令:
/hn_broadcast on - 开启定时播报
/hn_broadcast off - 关闭定时播报
/hn_broadcast status - 查看定时播报状态
/hn_broadcast mode [interval|cron] - 设置播报模式(间隔或定时)
/hn_broadcast interval 秒数 - 设置播报间隔(最小60秒)
/hn_broadcast cron '分 时 日 月 星期' - 设置播报时间(cron表达式)
  例如: hn_broadcast cron '0 8 * * *' 表示每天早上8点
  例如: hn_broadcast cron '0 8,20 * * *' 表示每天早上8点和晚上8点
  例如: hn_broadcast cron '0 */2 * * *' 表示每2小时的整点
/hn_broadcast header '格式字符串' - 设置播报消息头部格式
  例如: '[重要通知] {time} HN更新'
        """
        await hacker_news_broadcast.finish(usage)
