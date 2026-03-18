# AK News BWiki Uploader

将明日方舟官方新闻页面自动转换为Wiki格式并上传到BWIKI。

## 功能

- 自动抓取明日方舟官方新闻页面内容
- 下载并上传新闻图片到BWIKI
- 生成符合BWIKI文章模板格式的Wiki内容
- 自动上传页面到BWIKI

## 使用方法

```bash
python scripts/bwiki_uploader.py <news_url> <SESSDATA> [page_title]
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `news_url` | 明日方舟新闻页面URL，如 `https://ak.hypergryph.com/news/20241222` |
| `SESSDATA` | B站SESSDATA Cookie值（用于BWIKI登录认证） |
| `page_title` | 可选，自定义页面标题，默认使用原网页标题 |

### 示例

```bash
python scripts/bwiki_uploader.py https://ak.hypergryph.com/news/20241222 your_sessdata_value
```

## 获取 SESSDATA

1. 登录 [bilibili.com](https://www.bilibili.com)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Application > Cookies
4. 找到 `SESSDATA` 的值并复制

## 生成内容格式

上传的Wiki页面将使用以下模板格式：

```markdown
{{文章模板
|文章上级页面=公告
|时间=YYYYMMDD
|是否原创=否
|作者=【明日方舟】运营组
|来源=官方网站
|原文地址=https://ak.hypergryph.com/news/xxx
|危险等级=
}}

[[file:CN_xxx_1.jpg|center]]
[[file:CN_xxx_2.png|center]]

{新闻正文内容}
```

## 依赖

- Python 3.x
- 仅使用标准库，无需额外安装依赖

## 许可证

MIT License
