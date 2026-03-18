import urllib.request
import urllib.parse
import json
import http.cookiejar
import sys
import re
from datetime import datetime


class BWikiClient:
    def __init__(self, wiki_name: str, sessdata: str):
        self.wiki_name = wiki_name
        self.api_url = "https://wiki.biligame.com/%s/api.php" % wiki_name
        self.wiki_url = "https://wiki.biligame.com/%s" % wiki_name
        self.sessdata = sessdata

        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

        cookie = http.cookiejar.Cookie(
            version=0,
            name='SESSDATA',
            value=self.sessdata,
            port=None,
            port_specified=False,
            domain='.biligame.com',
            domain_specified=True,
            domain_initial_dot=False,
            path='/',
            path_specified=True,
            secure=False,
            expires=None,
            discard=True,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False
        )
        self.cookie_jar.set_cookie(cookie)
        self._init_session()

    def _init_session(self):
        try:
            req = urllib.request.Request(self.wiki_url, method="GET")
            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            req.add_header("Referer", "https://bilibili.com")
            self.opener.open(req, timeout=30)
        except:
            pass

    def _request(self, method="GET", params=None, data=None):
        url = self.api_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": self.wiki_url,
            "Origin": "https://bilibili.com"
        }

        request_data = None

        if method == "GET" and params:
            query_string = urllib.parse.urlencode(params)
            url = "%s?%s" % (self.api_url, query_string)
        elif method == "POST":
            if data:
                request_data = urllib.parse.urlencode(data).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=request_data, headers=headers, method=method)
            with self.opener.open(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {'error': str(e)}

    def check_login(self):
        params = {
            'action': 'query',
            'meta': 'userinfo',
            'uiprop': 'groups|rights',
            'format': 'json'
        }
        result = self._request('GET', params)

        if 'query' in result and 'userinfo' in result['query']:
            user_info = result['query']['userinfo']
            if 'anon' not in user_info:
                self.username = user_info['name']
                self.user_id = user_info['id']
                return True, user_info
        return False, result

    def get_csrf_token(self):
        params = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        result = self._request('GET', params)

        if 'query' in result and 'tokens' in result['query']:
            return result['query']['tokens']['csrftoken']
        return None

    def upload_file(self, filename: str, file_content: bytes, description: str = "", comment: str = "") -> tuple:
        token = self.get_csrf_token()
        if not token:
            return False, {'error': '无法获取CSRF令牌'}

        boundary = "----WebKitFormBoundary" + ''.join([str(i % 10) for i in range(16)])
        body_parts = []

        form_data = {
            'action': 'upload',
            'filename': filename,
            'text': description,
            'comment': comment,
            'token': token,
            'format': 'json',
            'ignorewarnings': '1'
        }

        for key, value in form_data.items():
            body_parts.append(
                '--%s\r\n' % boundary +
                'Content-Disposition: form-data; name="%s"\r\n\r\n' % key +
                '%s\r\n' % value
            )

        body_parts.append(
            '--%s\r\n' % boundary +
            'Content-Disposition: form-data; name="file"; filename="%s"\r\n' % filename +
            'Content-Type: application/octet-stream\r\n\r\n'
        )

        body = ''.join(body_parts).encode('utf-8') + file_content + ('\r\n--%s--\r\n' % boundary).encode('utf-8')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "multipart/form-data; boundary=%s" % boundary,
            "Referer": self.wiki_url
        }

        try:
            req = urllib.request.Request(self.api_url, data=body, headers=headers, method="POST")
            with self.opener.open(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))

                if 'upload' in result and result['upload'].get('result') == 'Success':
                    result['upload']['url'] = "https://wiki.biligame.com/%s/文件:%s" % (self.wiki_name, urllib.parse.quote(filename))
                    return True, result['upload']

                return False, result
        except Exception as e:
            return False, {'error': str(e)}

    def edit_page(self, title: str, content: str, summary: str = ""):
        token = self.get_csrf_token()
        if not token:
            return False, {'error': '无法获取CSRF令牌'}

        data = {
            'action': 'edit',
            'title': title,
            'text': content,
            'summary': summary,
            'token': token,
            'format': 'json',
            'bot': 'true'
        }

        result = self._request('POST', data=data)

        if 'edit' in result and result['edit'].get('result') == 'Success':
            result['edit']['url'] = "https://wiki.biligame.com/%s/%s" % (self.wiki_name, urllib.parse.quote(title))
            return True, result['edit']

        return False, result


def download_image(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://ak.hypergryph.com/"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def extract_images_from_html(html_content: str, news_id: str) -> list:
    img_pattern = r'<img\s+src="([^"]+)"'
    matches = re.findall(img_pattern, html_content)

    images = []
    for i, url in enumerate(matches):
        ext = 'jpg'
        if url.endswith('.png') or '.png' in url:
            ext = 'png'

        images.append({
            'url': url,
            'filename': "CN_%s_%d.%s" % (news_id, i + 1, ext),
            'index': i + 1
        })

    return images


def process_news_content(html_content: str, url: str):
    # Extract news ID from URL
    id_match = re.search(r'/news/(\d+)', url)
    news_id = id_match.group(1) if id_match else 'unknown'

    # Try to find title in HTML
    title_match = re.search(r'<div class="_86483275">([^<]+)</div>', html_content)
    if not title_match:
        title_match = re.search(r'<title>([^<]+)\s*-\s*明日方舟</title>', html_content)
    title = title_match.group(1).strip() if title_match else '未命名'
    
    # Replace invalid wiki title characters
    title = title.replace('[', '【').replace(']', '】')

    # Try to find date in HTML (format: 2025 // 12 / 22)
    date_match = re.search(r'<div class="_8f259902">(\d+)\s*//\s*(\d+)\s*/\s*(\d+)</div>', html_content)
    if date_match:
        year = date_match.group(1)
        month = date_match.group(2).zfill(2)
        day = date_match.group(3).zfill(2)
        date_str = year + month + day
    else:
        date_str = datetime.now().strftime('%Y%m%d')

    # Find content div - try multiple patterns
    content_match = re.search(r'<div class="_0868052a">([\s\S]*?)</div></div></div></div></div></div><div class="_61725cbe">', html_content)
    if not content_match:
        content_match = re.search(r'<div class="_0868052a">([\s\S]*?)</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', html_content)

    if content_match:
        content = content_match.group(1)
    else:
        # Fallback: try to extract content area
        content_match = re.search(r'<div class="_0868052a">(.*?)</div>', html_content, re.DOTALL)
        content = content_match.group(1) if content_match else ''

    return {
        'id': news_id,
        'title': title,
        'author': '【明日方舟】运营组',
        'date': date_str,
        'content': content
    }


def upload_news_to_wiki(url: str, sessdata: str, page_title: str = None) -> dict:
    import subprocess

    cmd = "powershell -Command \"Invoke-WebRequest -Uri '%s' -UseBasicParsing | Select-Object -ExpandProperty Content\"" % url
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

    html_content = result.stdout

    news_info = process_news_content(html_content, url)
    if not news_info:
        return {'success': False, 'error': '无法解析文章内容'}

    news_id = news_info['id']
    if not page_title:
        page_title = news_info['title']

    date_str = news_info['date']
    author = news_info['author']
    content = news_info['content']

    images = extract_images_from_html(content, news_id)

    wiki_image_refs = ""
    for img in images:
        wiki_image_refs += "[[file:%s|center]]\n" % img['filename']

    content_without_img = re.sub(r'<img\s+[^>]*>', '', content)

    wiki_content = """{{文章模板
|文章上级页面=公告
|时间=%s
|是否原创=否
|作者=%s
|来源=官方网站
|原文地址=%s
|危险等级=
}}

%s
%s""" % (date_str, author, url, wiki_image_refs, content_without_img)

    client = BWikiClient("arknights", sessdata)

    success, user = client.check_login()
    if not success:
        return {'success': False, 'error': '登录失败: %s' % user}

    uploaded_images = []
    for img in images:
        try:
            img_data = download_image(img['url'])
            up_success, up_result = client.upload_file(
                filename=img['filename'],
                file_content=img_data,
                description="明日方舟新闻图片 %s" % news_id
            )
            uploaded_images.append({
                'filename': img['filename'],
                'success': up_success,
                'result': up_result
            })
        except Exception as e:
            uploaded_images.append({
                'filename': img['filename'],
                'success': False,
                'error': str(e)
            })

    edit_success, edit_result = client.edit_page(
        title=page_title,
        content=wiki_content,
        summary="自动上传：明日方舟新闻 %s" % news_id
    )

    return {
        'success': edit_success,
        'page_title': page_title,
        'date': date_str,
        'news_id': news_id,
        'uploaded_images': uploaded_images,
        'edit_result': edit_result
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python bwiki_uploader.py <news_url> <SESSDATA> [page_title]")
        sys.exit(1)

    url = sys.argv[1]
    sessdata = sys.argv[2]
    page_title = sys.argv[3] if len(sys.argv) > 3 else None

    result = upload_news_to_wiki(url, sessdata, page_title)
    print(json.dumps(result, ensure_ascii=False, indent=2))
