import os
import requests
import re
from datetime import datetime

REPO = os.getenv('GITHUB_REPOSITORY')
TOKEN = os.getenv('GITHUB_TOKEN')

# 获取所有 Issue
url = f'https://api.github.com/repos/{REPO}/issues?state=all&per_page=100'
headers = {'Authorization': f'token {TOKEN}'}
issues = requests.get(url, headers=headers).json()

cards = []
for issue in issues:
    if 'pull_request' in issue:
        continue
    title = issue['title']
    body = issue['body'] or ''
    created = issue['created_at']

    gender = re.search(r'性别[：:]\s*(.+)', body)
    date = re.search(r'体检日期[：:]\s*(.+)', body)
    id_num = re.search(r'身份证[：:]\s*(.+)', body)

    img_match = re.search(r'!\[.*?\]\((https?://[^\s]+)\)', body)
    img_url = img_match.group(1) if img_match else './one.jpg'

    name = title.split('_')[0] if '_' in title else title
    date_display = date.group(1) if date else '未选择日期'

    card = f'''
    <div class="cert-module top-card">
        <div class="top-title">广东省食品从业人员健康证明</div>
        <div class="top-content">
            <div class="text-container">
                <div class="info-line">
                    <span style="font-weight: bold;">姓 名</span>
                    <span>∶</span>
                    <span id="displayName">{name}</span>
                    <span class="gender-separator" style="font-weight: bold;">性 别</span>
                    <span>∶</span>
                    <span id="displayGender">{gender.group(1) if gender else '男'}</span>
                </div>
                <div class="id-group">
                    <div class="info-line">
                        <span style="font-weight: bold;">身份证号码</span>
                        <span>∶</span>
                        <span id="displayId">{id_num.group(1) if id_num else '无'}</span>
                    </div>
                    <div class="info-line">(或其它有效证明)</div>
                </div>
                <div class="info-line">
                    <span style="font-weight: bold;">体检单位</span>
                    <span>∶</span>
                    <span>广州东仁医院</span>
                </div>
                <div class="info-line last-line">
                    <span style="font-weight: bold;">体检日期</span>
                    <span>∶</span>
                    <span id="displayDate">{date_display}</span>
                </div>
            </div>
            <div class="photo">
                <div class="seal-container">
                    <img class="seal-img" src="https://raw.githubusercontent.com/merryAndrew/imge/main/than.png" alt="印章图片">
                </div>
                <img src="{img_url}" alt="持证人照片">
            </div>
        </div>
    </div>
    '''
    cards.append(card)

cards.reverse()

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
            background-color: #e0d6c7;
            padding: 10px;
            min-height: 100vh;
        }}
        .app-wrapper {{
            max-width: 450px;
            margin: 0 auto;
        }}
        .photo .seal-container {{
            position: absolute !important;
            top: 44px !important;
            left: -47px !important;
            z-index: 999 !important;
        }}
        .photo .seal-img {{
            width: 63px !important;
            height: 63px !important;
            object-fit: contain !important;
            opacity: 1 !important;
            display: block !important;
        }}
        .cert-module {{
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100%;
            height: 180px;
        }}
        .top-card {{
            font-size: 11px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .top-title {{
            text-align: center;
            font-size: 16px;
            color: #333;
            font-weight: bold;
        }}
        .top-content {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .text-container {{
            width: 65%;
        }}
        .info-line {{
            margin-bottom: 8px;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 1px;
        }}
        .id-group {{
            margin-bottom: 8px;
        }}
        .id-group .info-line {{
            margin-bottom: 0;
            line-height: 1.2;
        }}
        .last-line {{
            margin-bottom: 0;
        }}
        .photo {{
            width: 70px;
            height: 90px;
            border: 1px solid #ddd;
            margin-left: 10px;
            position: relative !important;
            overflow: visible !important;
        }}
        .photo img[alt="持证人照片"] {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            position: relative;
            z-index: 1;
        }}
        .middle-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #333;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .middle-line {{
            margin: 5px 0;
        }}
        .bottom-card {{
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 11px;
        }}
        .qrcode-area {{
            text-align: center;
            margin-bottom: 15px;
        }}
        .qrcode-title {{
            color: #333;
            margin-bottom: 10px;
            font-size: 13px;
        }}
        .qrcode-img {{
            width: 140px;
            height: 140px;
            margin: 0 auto;
        }}
        .qrcode-img img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
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
        }}
        .notice-content {{
            color: #856404;
            line-height: 1.4;
        }}
        .gender-separator {{
            margin-left: 15px;
        }}
        .card-wrapper {{
            margin-bottom: 20px;
        }}
        .card-wrapper .bottom-card {{
            margin-top: -8px;
        }}
    </style>
</head>
<body>
    <div class="app-wrapper">
        {''.join(cards)}
    </div>
</body>
</html>'''

os.makedirs('dist', exist_ok=True)
with open('dist/index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ 生成成功！")
