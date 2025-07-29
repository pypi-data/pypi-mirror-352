# nonebot-plugin-hacker-news

获取 Hacker News 热门文章的Nonebot插件, 支持获取热门、最新、最佳文章以及文章详情和评论

## 安装

### 通过 pip 安装

```bash
pip install nonebot-plugin-hacker-news
```

### 通过 nb-cli 安装

```bash
nb plugin install nonebot-plugin-hacker-news
```

## 基本命令

``` plaintext
/hn：获取Hacker News热门文章，默认获取前5条
/hn top [数量]：获取热门文章，默认5条
/hn new [数量]：获取最新文章，默认5条
/hn best [数量]：获取最佳文章，默认5条
/hn item [ID]：获取特定文章详情
/hn comments [ID]：获取特定文章及其评论
```

## 定时播报控制

``` plaintext
/hn_broadcast on：开启定时播报功能
/hn_broadcast off：关闭定时播报功能
/hn_broadcast status：查看定时播报状态
/hn_broadcast mode [interval|cron]：设置播报模式(间隔或定时)
/hn_broadcast interval [秒数]：设置播报间隔(最小60秒)
/hn_broadcast cron [表达式]：设置每天固定时间播报，格式为"分 时 日 月 星期"
```

## 配置

```python
api_base_url = "https://hacker-news.firebaseio.com/v0"
api_timeout = 10  # 请求超时时间，单位秒

auto_broadcast = False  # 是否开启定时播报
broadcast_mode = "interval"  # "interval"为间隔模式，"cron"为定时模式
broadcast_interval = 3600  # 定时播报间隔，单位秒
broadcast_cron = "0 8 * * *"  # cron表达式，默认每天早上八点
max_comments_depth = 3  # 获取评论的最大深度
max_items_per_request = 10  # 单次请求最大获取条数
broadcast_groups = [123456789]  # 定时播报群组列表
broadcast_articles_count = 5  # 每次播报的文章数量
```
