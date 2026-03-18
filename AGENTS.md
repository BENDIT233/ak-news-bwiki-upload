# ak-news - 明日方舟新闻BWIKI上传工具

自动处理明日方舟官方新闻页面并上传到BWIKI的CLI工具集。

## 项目概述

本项目用于自动化处理明日方舟官方网站新闻，提取内容、下载图片、生成Wiki格式，并上传到BWIKI（明日方舟BWIKI）。

## 目录结构

```
ak-news/
├── AGENTS.md          # 本文件 - 项目上下文说明
├── SESSDATA.txt       # B站SESSDATA Cookie（用于BWIKI登录认证）
└── .iflow/
    └── skills/
        └── ak-news-wiki-upload/
            ├── SKILL.md              # Skill定义和处理流程
            └── scripts/
                └── bwiki_uploader.py # 核心上传脚本
```

## 使用方法

### 基本用法

```bash
python .iflow/skills/ak-news-wiki-upload/scripts/bwiki_uploader.py <news_url> <SESSDATA> [page_title]
```

**参数说明:**
- `news_url`: 明日方舟官方新闻URL，格式 `https://ak.hypergryph.com/news/{ID}`
- `SESSDATA`: B站SESSDATA Cookie值
- `page_title`: (可选) 自定义页面标题，默认使用原标题

### 示例

```bash
python .iflow/skills/ak-news-wiki-upload/scripts/bwiki_uploader.py \
    "https://ak.hypergryph.com/news/4946" \
    "your_sessdata_value"
```

## SESSDATA 获取

SESSDATA 是B站的登录凭证，用于BWIKI API认证。

1. 登录 bilibili.com
2. 打开浏览器开发者工具 (F12)
3. 在 Application > Cookies 中找到 `SESSDATA`
4. 将值保存到 `SESSDATA.txt`

## 处理流程

1. **获取HTML** - 从官方网站获取新闻页面原始HTML
2. **提取内容** - 从HTML div标签提取标题、日期、正文
3. **处理图片** - 下载图片并重命名为 `CN_{ID}_{N}.{ext}` 格式
4. **生成Wiki格式** - 使用文章模板生成MediaWiki格式内容
5. **上传** - 先上传图片，再上传页面内容

## 关键注意事项

### 标题处理
- 英文方括号 `[]` 在MediaWiki标题中无效
- 必须替换为中文方括号 `【】`

### HTML结构
- 网站已从script内嵌JSON改为直接渲染HTML
- 标题: `<div class="_86483275">`
- 日期: `<div class="_8f259902">` (格式: `YYYY // MM / DD`)
- 正文: `<div class="_0868052a">`

### Cookie设置
- `domain_initial_dot=False`
- `secure=False`
- 必须先访问wiki首页初始化会话

## Wiki输出格式

```markdown
{{文章模板
|文章上级页面=公告
|时间=YYYYMMDD
|是否原创=否
|作者=【明日方舟】运营组
|来源=官方网站
|原文地址={URL}
|危险等级=
}}

[[file:CN_{ID}_1.jpg|center]]
{正文内容（保留HTML标签，已移除img标签）}
```

## 相关链接

- 明日方舟官网: https://ak.hypergryph.com/
- 明日方舟BWIKI: https://wiki.biligame.com/arknights/
