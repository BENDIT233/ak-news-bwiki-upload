---
name: ak-news-wiki-upload
description: 处理明日方舟官方新闻页面并上传到BWIKI。当用户提到处理明日方舟新闻、ak.hypergryph.com/news、明日方舟公告、需要将游戏官方通知上传到wiki时使用此技能。自动提取页面内容、下载上传图片、生成wiki格式并上传。
---

# ak-news-wiki-upload

将明日方舟官方新闻页面转换为wiki格式并上传到BWIKI。

## 触发场景

当用户出现以下任一情况时，必须使用此技能：
- 提供 `ak.hypergryph.com/news/` 相关URL并要求上传到wiki/BWIKI
- 请求处理明日方舟新闻页面并上传
- 提到"明日方舟公告上传wiki"、"方舟新闻上传"

## 输入格式

**必需参数：**
- URL: `https://ak.hypergryph.com/news/{ID}`
- SESSDATA: B站SESSDATA Cookie值（用于BWIKI登录认证）
- 页面标题（可选）：默认使用原网页标题

## 处理流程

### 步骤1：获取原始HTML内容

使用PowerShell获取页面：
```powershell
Invoke-WebRequest -Uri 'https://ak.hypergryph.com/news/{ID}' -UseBasicParsing
```

关键点：必须获取原始HTML内容，包含`<p>`, `<h3>`, `<strong>`, `<span style>`, `<br>`, `<img>`等HTML标签。

### 步骤2：提取内容

从返回的HTML中提取内容（网站结构已更新为直接渲染HTML）：

**提取方式：**
- **新闻ID**：从URL中提取 `/news/{ID}`
- **标题**：从 `<div class="_86483275">标题</div>` 提取
- **日期**：从 `<div class="_8f259902">2025 // 12 / 22</div>` 提取，转换为YYYYMMDD格式
- **正文内容**：从 `<div class="_0868052a">...</div>` 提取

**标题处理（关键）：**
- 英文方括号 `[]` 在MediaWiki标题中无效
- 必须将英文方括号替换为中文方括号：
```python
title = title.replace('[', '【').replace(']', '】')
```

内容包含 `<img>`, `<h1>`, `<p>`, `<strong>`, `<a>`, `<br>`, `<span style>` 等HTML标签

### 步骤3：处理图片（关键步骤）

1. **提取图片URL**：从HTML内容中提取所有 `<img src="...">` 标签的src属性
2. **下载图片**：使用 urllib 下载图片数据
3. **重命名图片**：按格式 `CN_{ID}_{N}.{ext}` 命名
   - `{ID}` = 新闻文章ID (cid)
   - `{N}` = 顺序编号 (1, 2, 3...)
   - `{ext}` = 原始格式 (jpg/png)
4. **上传图片到Wiki**：使用 BWikiClient.upload_file()
5. **生成wiki图片引用**：`[[file:CN_{ID}_{N}.{ext}|center]]`
6. **删除原始img标签**：从内容中移除 `<img ...>` 标签

### 步骤4：生成Wiki格式

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
[[file:CN_{ID}_2.png|center]]

{保留原始HTML格式的内容（已移除img标签）}
```

**重要注意事项：**
- ✅ 需要保持模板字段的完全一致
- ✅ 保留所有HTML标签（`<p>`, `<h3>`, `<strong>`, `<span style>`, `<br>`, `<a>`等）
- ✅ 删除原始 `<img>` 标签，用wiki图片引用替代
- ✅ 日期从displayTime时间戳转换为YYYYMMDD格式

### 步骤5：上传到BWIKI

**上传顺序：**
1. 先上传所有图片文件到Wiki
2. 再上传页面内容

```python
# 1. 上传图片
for img in images:
    img_data = download_image(img_url)
    client.upload_file(filename=img_filename, file_content=img_data)

# 2. 上传页面
client.edit_page(title=page_title, content=wiki_content)
```

## 关键实现细节

### Cookie设置（必须正确）
```python
cookie = http.cookiejar.Cookie(
    version=0, name='SESSDATA', value=sessdata,
    port=None, port_specified=False,
    domain='.biligame.com', domain_specified=True,
    domain_initial_dot=False,  # 关键：设为False
    path='/', path_specified=True,
    secure=False,  # 关键：设为False
    expires=None, discard=True,
    comment=None, comment_url=None, rest={}, rfc2109=False
)
```

### 必须先初始化会话
```python
def _init_session(self):
    req = urllib.request.Request(self.wiki_url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Referer", "https://bilibili.com")
    self.opener.open(req, timeout=30)
```

## 输出格式

返回上传结果：
- 成功：返回页面URL、上传的图片列表
- 失败：返回错误信息

## 注意事项

- Cookie设置：`domain_initial_dot=False`, `secure=False`
- 必须先访问wiki首页初始化会话
- 保留所有HTML标签以保持格式
- 使用UTF-8编码
- 图片必须先下载到本地，再上传到wiki
- **删除原始 `<img>` 标签**，用wiki图片引用替代
- **标题字符替换**：英文方括号 `[]` 需替换为中文方括号 `【】`，否则MediaWiki返回 `invalidtitle` 错误
- **HTML结构变更**：网站已从script内嵌JSON改为直接渲染HTML，需从div标签提取内容

## 脚本位置

脚本位于: `ak-news-wiki-upload/scripts/bwiki_uploader.py`

完整实现参考项目中的脚本。
