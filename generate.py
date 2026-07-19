import os
import sys
import requests
import re
import qrcode
from io import BytesIO
import base64
import traceback

try:
    REPO = os.getenv('GITHUB_REPOSITORY')
    TOKEN = os.getenv('GITHUB_TOKEN')
    if not REPO or not TOKEN:
        print("❌ 环境变量 GITHUB_REPOSITORY 或 GITHUB_TOKEN 未设置")
        sys.exit(1)

    USER = REPO.split('/')[0]

    # ---------- 分页获取所有 Issues ----------
    headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    issues = []
    page = 1
    while True:
        url = f'https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={page}'
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"⚠️ API 请求失败，状态码: {resp.status_code}")
            print(resp.text[:300])
            sys.exit(1)
        data = resp.json()
        if not data:
            break
        issues.extend(data)
        page += 1
        # 安全退出：如果返回数量少于100，说明已是最后一页
        if len(data) < 100:
            break

    print(f"📡 获取到 {len(issues)} 个 Issue")

    def extract_first_image(text):
        if not text:
            return None
        match = re.search(r'!\[.*?\]\((https?://[^\s]+)\)', text)
        if match:
            return match.group(1)
        match = re.search(r'<img[^>]+src="(https?://[^\s"]+)"', text)
        if match:
            return match.group(1)
        match = re.search(r'(https?://[^\s]+\.(?:png|jpg|jpeg|gif|webp|svg))', text)
        if match:
            return match.group(1)
        return None

    def build_card(issue, style='A'):
        title = issue.get('title', '未知')
        body = issue.get('body') or ''
        comments_url = issue.get('comments_url')
        comments = []
        if comments_url:
            try:
                resp = requests.get(comments_url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    comments = resp.json()
            except:
                pass
        all_text = body
        for comment in comments:
            all_text += ' ' + comment.get('body', '')

        # 安全提取
        gender_match = re.search(r'性别[：:]\s*(.+)', all_text)
        gender = gender_match.group(1).strip() if gender_match else '男'
        date_match = re.search(r'体检日期[：:]\s*(.+)', all_text)
        date_display = date_match.group(1).strip() if date_match else '未选择日期 (有效期一年)'
        id_match = re.search(r'身份证[：:]\s*(.+)', all_text)
        id_num = id_match.group(1).strip() if id_match else '无'

        img_url = extract_first_image(all_text)
        if not img_url:
            img_url = 'https://via.placeholder.com/70x90?text=No+Photo'
        print(f"📸 标题 '{title}' 的图片链接: {img_url}")

        name = title.split('_')[0] if '_' in title else title

        page_url = f'https://{USER}.github.io/Healths/?id={title}'
        qr = qrcode.make(page_url)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        # 国内镜像资源
        font_awesome_cdn = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
        seal_img_url = 'https://mirror.ghproxy.com/raw.githubusercontent.com/merryAndrew/imge/main/than.png'

        if style == 'A':
            return f'''
            <div class="cert-wrapper" data-title="{title}">
                <div class="cert-module top-card">
                    <div class="top-title">广东省食品从业人员健康证明</div>
                    <div class="top-content">
                        <div class="text-container">
                            <div class="info-line">
                                <span style="font-weight: bold;">姓 名</span>
                                <span>∶</span>
                                <span>{name}</span>
                                <span class="gender-separator" style="font-weight: bold;">性 别</span>
                                <span>∶</span>
                                <span>{gender}</span>
                            </div>
                            <div class="id-group">
                                <div class="info-line">
                                    <span style="font-weight: bold;">身份证号码</span>
                                    <span>∶</span>
                                    <span>{id_num}</span>
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
                                <span>{date_display}</span>
                            </div>
                        </div>
                        <div class="photo">
                            <div class="seal-container">
                                <img class="seal-img" src="{seal_img_url}" alt="印章图片">
                            </div>
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
                        <div class="qrcode-title">防伪标识二维码</div>
                        <div class="qrcode-img">
                            <img src="data:image/png;base64,{qr_base64}" alt="防伪二维码">
                        </div>
                    </div>
                    <div class="notice">
                        <div class="notice-title">
                            <i class="fas fa-exclamation-circle exclamation-icon"></i>
                            关于申请实体证明通知：
                        </div>
                        <div class="notice-content">目前实体证明申请的入口已经关闭，全面推广电子证，请广大从业人员和用人单位积极使用。如对查询信息存疑，请与体检机构联系。</div>
                    </div>
                </div>
            </div>
            '''
        else:
            return f'''
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
                                <span class="content">{gender}</span>
                            </div>
                            <div class="id-group">
                                <div class="info-line">
                                    <span class="label">身份证号码</span>
                                    <span class="colon">∶</span>
                                    <span class="content">{id_num}</span>
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

    cards_A = []
    cards_B = []
    for issue in issues:
        if 'pull_request' in issue:  # 忽略 PR 对应的伪 Issue
            continue
        cards_A.append(build_card(issue, 'A'))
        cards_B.append(build_card(issue, 'B'))

    cards_A.reverse()
    cards_B.reverse()

    font_awesome_cdn = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'

    html_A = f'''<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>健康证服务-证件查询</title>
        <link rel="stylesheet" href="{font_awesome_cdn}">
        <style>...（省略，与原来相同）...</style>
    </head>
    <body>
        <div class="app-wrapper">
            {''.join(cards_A)}
        </div>
        <script>...（省略）...</script>
    </body>
    </html>'''

    html_B = f'''<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>健康证查询</title>
        <link rel="stylesheet" href="{font_awesome_cdn}">
        <style>...（省略）...</style>
    </head>
    <body>
        {''.join(cards_B)}
        <script>...（省略）...</script>
    </body>
    </html>'''

    os.makedirs('dist', exist_ok=True)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html_B)
    with open('dist/card.html', 'w', encoding='utf-8') as f:
        f.write(html_A)

    print("✅ 生成成功！已生成 index.html 和 card.html")

except Exception as e:
    print("❌ 脚本执行异常:", e)
    traceback.print_exc()
    sys.exit(1)
