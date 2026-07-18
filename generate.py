import os
import requests
import re
import qrcode
from io import BytesIO
import base64

REPO = os.getenv('GITHUB_REPOSITORY')
TOKEN = os.getenv('GITHUB_TOKEN')
USER = REPO.split('/')[0] if REPO else 'merryAndrew'

url = f'https://api.github.com/repos/{REPO}/issues?state=all&per_page=100'
headers = {'Authorization': f'token {TOKEN}'}
issues = requests.get(url, headers=headers).json()

cards = []
for issue in issues:
    if 'pull_request' in issue:
        continue
    title = issue['title']
    body = issue['body'] or ''

    gender = re.search(r'性别[：:]\s*(.+)', body)
    date = re.search(r'体检日期[：:]\s*(.+)', body)
    id_num = re.search(r'身份证[：:]\s*(.+)', body)
    img_match = re.search(r'!\[.*?\]\((https?://[^\s]+)\)', body)
    img_url = img_match.group(1) if img_match else './one.jpg'  # 默认本地

    name = title.split('_')[0] if '_' in title else title
    date_display = date.group(1) if date else '未选择日期 (有效期一年)'

    # 生成专属二维码（内容指向该证详情页）
    page_url = f'https://{USER}.github.io/Healths/?id={title}'
    qr = qrcode.make(page_url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    # ---------- 使用“复制纯净代码”的样式 ----------
    card = f'''
    <div class="cert-wrapper" data-title="{title}">
        <div class="cert-module top-card">
            <div class="top-title">广东省食品从业人员健康证明</div>
            <div class="top-content">
                <div class="text-container">
                    <div class="info-line">
                        <span class="label">姓 名</span>
                        <span class="colon">∶</span>
                        <span class="content">{name}</span>
                        <span class="gender-separator"></span>
                        <span class="label">性 别</span>
                        <span class="colon">∶</span>
                        <span class="content">{gender.group(1) if gender else '男'}</span>
                    </div>
                    <div class="id-group">
                        <div class="info-line">
                            <span class="label">身份证号码</span>
                            <span class="colon">∶</span>
                            <span class="content">{id_num.group(1) if id_num else '无'}</span>
                        </div>
                        <div class="info-line">(或其它有效证明)</div>
                    </div>
                    <div class="info-line">
                        <span class="label">体检单位</span>
                        <span class="colon">∶</span>
                        <span class="content">广州东仁医院</span>
                    </div>
                    <div class="info-line last-line">
                        <span class="label">体检日期</span>
                        <span class="colon">∶</span>
                        <span class="content">{date_display}</span>
                    </div>
                </div>
                <div class="photo">
                    <img src="{img_url}" alt="持证人照片">
                </div>
            </div>
        </div>
        <div class="cert-module middle-card">
            <div class="middle-line">广东省食品从业人员</div>
            <div class="middle-line">健康证明</div>
        </div>
        <div class="bottom-card">
            <div class="qrcode-area">
                <div class="qrcode-img">
                    <img src="data:image/png;base64,{qr_base64}" alt="防伪二维码">
                </div>
                <div class="qrcode-title">此健康信息已上报平台</div>
            </div>
        </div>
    </div>
    '''
    cards.append(card)

cards.reverse()

# 完整HTML模板（完全复刻“复制纯净代码”的样式）
html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>健康证查询</title>
    <link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: "Microsoft Yahei", sans-serif;
            background-color: #e9e9e9;
            padding: 10px;
        }}
        .cert-wrapper {{
            max-width: 450px;
            margin: 0 auto 20px auto;
        }}
        .cert-module {{
            background: #f8f8f8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.35);
            width: 100%;
            height: 180px;
        }}
        .top-card {{
            font-size: 11px;
            display: flex;
            flex-direction: column;
            height: 100%;
            margin-top: 5px;
        }}
        .top-title {{
            text-align: center;
            font-size: 16px;
            color: #333;
            margin-top: 5px;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        .top-content {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex: 1;
        }}
        .text-container {{
            width: 65%;
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        .info-line {{
            margin-bottom: 8px;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 1px;
        }}
        .label {{}}
        .colon {{}}
        .content {{ font-weight: bold; }}
        .gender-separator {{ margin-left: 10px; }}
        .id-group {{
            margin-bottom: 8px;
        }}
        .id-group .info-line {{
            margin-bottom: 0;
            line-height: 1.2;
        }}
        .last-line {{
            margin-top: auto;
            margin-bottom: 10px;
        }}
        .photo {{
            width: 70px;
            height: 90px;
            border: 1px solid #ddd;
            margin-left: 10px;
        }}
        .photo img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .middle-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #333;
            text-align: center;
            width: 100%;
            height: 180px;
            font-weight: bold;
        }}
        .middle-line {{
            margin: 5px 0;
        }}
        .bottom-card {{
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            font-size: 11px;
            text-align: center;
            background: #f8f8f8;
            box-shadow: 0 8px 16px rgba(0,0,0,0.35);
        }}
        .qrcode-area {{
            text-align: center;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .qrcode-img {{
            width: 120px;
            height: 120px;
            margin: 0 auto 10px;
        }}
        .qrcode-img img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
        .qrcode-title {{
            color: #333;
            margin-bottom: 0;
            font-size: 13px;
            font-weight: bold;
        }}
        .notice {{
            background-color: #fffbeb;
            border: 1px solid #ffeeba;
            border-radius: 8px;
            padding: 12px;
            font-size: 10px;
        }}
        .notice-title {{
            color: #856404;
            font-weight: bold;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
        }}
        .exclamation-icon {{
            margin-right: 5px;
            font-size: 12px;
            background-color: yellow;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #856404;
        }}
        .notice-content {{
            color: #856404;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    {''.join(cards)}
    <script>
        (function() {{
            const params = new URLSearchParams(window.location.search);
            const id = params.get('id');
            if (id) {{
                const wrappers = document.querySelectorAll('.cert-wrapper');
                let found = false;
                wrappers.forEach(w => {{
                    const title = w.getAttribute('data-title');
                    if (title === id) {{
                        w.style.display = 'block';
                        found = true;
                    }} else {{
                        w.style.display = 'none';
                    }}
                }});
                if (!found) {{
                    wrappers.forEach(w => w.style.display = 'block');
                }}
            }}
        }})();
    </script>
</body>
</html>'''

os.makedirs('dist', exist_ok=True)
with open('dist/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ 生成成功！")
