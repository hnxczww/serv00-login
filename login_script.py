import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os
import subprocess

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

async def login(username, password, panel):
    global browser

    page = None
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

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

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()

def execute_script(script_path):
    try:
        result = subprocess.run([script_path], check=True, text=True, capture_output=True)
        print(f"脚本 {script_path} 执行成功，输出：{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"脚本 {script_path} 执行失败，错误：{e.stderr}")

async def update_crontab(commands):
    for command in commands:
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"命令 '{command}' 执行成功，输出：{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"命令 '{command}' 执行失败，错误：{e.stderr}")
        # 等待 5 秒
        await asyncio.sleep(5)

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
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
            message += success_message + '\n'
            print(success_message)

            # 执行 cron 命令
            cron_commands = [
                '(crontab -l; echo "@reboot pkill -kill -u ${USER} && nohup /home/${USER}/.s5/s5 -c /home/${USER}/.s5/config.json >/dev/null 2>&1 & && nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -',
                '(crontab -l; echo "*/12 * * * * pgrep -x \\"nezha-agent\\" > /dev/null || nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -'
            ]
            await update_crontab(cron_commands)

            # 等待 5 秒
            await asyncio.sleep(5)

            # 执行脚本
            script_path = './gaojilingjuli.sh'
            execute_script(script_path)

        else:
            message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)
        
    message += f'所有{serviceName}账号登录完成！'
    await send_telegram_message(message)
    print(f'所有{serviceName}账号登录完成！')

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
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，状态码：{response.status_code}")

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
