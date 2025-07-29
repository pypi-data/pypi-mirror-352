import httpx
import time
import nonebot
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime

from . import plugin_config
BASE_URL = plugin_config.api_base_url

# 获取前N条热门文章
async def get_top_stories(limit: int = 5) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/topstories.json", timeout=plugin_config.api_timeout)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            stories = []
            for story_id in story_ids:
                story = await get_item_details(story_id)
                if story:
                    stories.append(story)
            
            return stories
        except Exception as e:
            nonebot.logger.error(f"Error fetching top stories: {e}")
            return []

# 获取前N条最新文章
async def get_new_stories(limit: int = 5) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/newstories.json", timeout=plugin_config.api_timeout)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            stories = []
            for story_id in story_ids:
                story = await get_item_details(story_id)
                if story:
                    stories.append(story)
            
            return stories
        except Exception as e:
            nonebot.logger.error(f"Error fetching new stories: {e}")
            return []

# 获取前N条最佳文章
async def get_best_stories(limit: int = 5) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/beststories.json", timeout=plugin_config.api_timeout)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            stories = []
            for story_id in story_ids:
                story = await get_item_details(story_id)
                if story:
                    stories.append(story)
            
            return stories
        except Exception as e:
            nonebot.logger.error(f"Error fetching best stories: {e}")
            return []

# 获取特定ID的项目详情
async def get_item_details(item_id: int) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/item/{item_id}.json", timeout=plugin_config.api_timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            nonebot.logger.error(f"Error fetching item {item_id}: {e}")
            return None

# 获取文章及其评论
async def get_story_with_comments(story_id: int, comment_limit: int = 3) -> Optional[Dict[str, Any]]:
    story = await get_item_details(story_id)
    if not story:
        return None
    
    comments = []
    if "kids" in story and story["kids"]:
        comment_ids = story["kids"][:comment_limit]
        for comment_id in comment_ids:
            comment = await get_item_details(comment_id)
            if comment:
                comments.append(comment)
    
    return {
        "story": story,
        "comments": comments
    }

# 格式化单个文章
def format_item(item: Dict[str, Any]) -> str:
    title = item.get("title", "No title")
    url = item.get("url", "")
    by = item.get("by", "anon")
    time_str = datetime.fromtimestamp(item.get("time", 0)).strftime("%Y-%m-%d %H:%M")
    score = item.get("score", 0)
    comments_count = item.get("descendants", 0)
    
    result = f"[POST] {title}\n"
    if url:
        result += f"[URL] {url}\n"
    result += f"[BY] {by} | [TIME] {time_str}\n"
    result += f"[SCORE] {score} | [COMMENTS] {comments_count}\n"
    result += f"[ID] {item.get('id', 'unknown')}"
    
    return result

# 格式化文章及其评论
def format_item_with_comments(story: Dict[str, Any], comments: List[Dict[str, Any]]) -> str:
    
    result = format_item(story)
    if comments:
        result += "\n\n[COMMENTS]"
        for i, comment in enumerate(comments, 1):
            comment_text = comment.get("text", "").replace("<p>", "\n").replace("</p>", "")
            comment_by = comment.get("by", "anon")
            comment_time = datetime.fromtimestamp(comment.get("time", 0)).strftime("%Y-%m-%d %H:%M")
            
            result += f"\n\n{i}. [BY] {comment_by} | [TIME] {comment_time}\n"
            result += f"{comment_text}"
    else:
        result += "\n\n[COMMENTS] None"
    
    return result
