import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# telegram消息
message = 'serv00&ct8自动化脚本运行\n'

async def login_and_run_script(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        # 等待页面加载
        await page.waitForSelector('#id_username')
        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)

        await page.type('#id_username', username)
        await page.type('#id_password', password)

        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('无法找到登录按钮')

        await page.waitForNavigation()
        
        # 等待登录完成并验证
        await page.waitForSelector('a[href="/logout/"]')
        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        if is_logged_in:
            print(f'{serviceName}账号 {username} 登录成功')
            # 确保脚本执行按钮存在
            await page.waitForSelector('button.execute-script', timeout=60000)  # 60秒超时
            script_button = await page.querySelector('button.execute-script')  # 请根据实际情况调整选择器
            if script_button:
                await script_button.click()
                # 等待脚本执行完成的反馈
                await page.waitForSelector('div.script-execution-status', timeout=60000)  # 60秒超时
                status = await page.evaluate('''() => document.querySelector('div.script-execution-status').innerText''')
                return status
            else:
                raise Exception('无法找到执行脚本的按钮')
        else:
            print(f'{serviceName}账号 {username} 登录失败')
            return '登录失败'

    except Exception as e:
        print(f'{serviceName}账号 {username} 执行任务时出现错误: {e}')
        return '执行任务时出现错误'

    finally:
        if page:
            await page.close()

async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panel']

        serviceName = 'ct8' if 'ct8' in panel else 'serv00'
        status = await login_and_run_script(username, password, panel)

        now_utc = format_to_iso(datetime.utcnow())
        now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
        if status == '登录成功':
            success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功并执行脚本！'
            message += success_message + '\n'
            print(success_message)
        else:
            message += f'{serviceName}账号 {username} 登录或执行脚本失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录或执行脚本失败，请检查{serviceName}账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)
        
    message += f'所有{serviceName}账号登录和脚本执行完成！'
    await send_telegram_message(message)
    print(f'所有{serviceName}账号登录和脚本执行完成！')

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': '问题反馈❓',
                        'url': 'https://t.me/yxjsjl'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
