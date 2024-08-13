import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os
import subprocess
import tempfile

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

async def execute_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"命令执行失败: {stderr.decode()}")
    else:
        print(f"命令执行成功: {stdout.decode()}")

    # 添加回车
    print("")  # 输出一个空行作为回车

async def download_and_execute_script(url):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_script:
            temp_script_name = temp_script.name

        # 下载脚本
        response = requests.get(url)
        if response.status_code == 200:
            with open(temp_script_name, 'wb') as f:
                f.write(response.content)
        else:
            print(f"下载脚本失败: {response.status_code}")
            return

        # 执行脚本
        await execute_command(f'bash {temp_script_name}')

        # 删除临时文件
        os.remove(temp_script_name)

    except Exception as e:
        print(f"下载或执行脚本时出错: {e}")

async def run_install_scripts():
    # 执行安装脚本
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-socks5/main/install-socks5.sh')
    await delay_time(5000)  # 等待5秒
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-dashboard.sh')
    await delay_time(5000)  # 等待5秒
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-agent.sh')
    await delay_time(5000)  # 等待5秒
    # 执行新添加的脚本
    await execute_command('./gaojilingjuli.sh')

async def login(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
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

        if is_logged_in:
            # 登录成功后执行安装脚本
            await run_install_scripts()

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        return False

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
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
            message += success_message + '\n'
            print(success_message)
        else:
            message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        # 每个账号登录后随机延迟
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
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os
import subprocess
import tempfile

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

async def execute_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"命令执行失败: {stderr.decode()}")
    else:
        print(f"命令执行成功: {stdout.decode()}")

    # 添加回车
    print("")  # 输出一个空行作为回车

async def download_and_execute_script(url):
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_script:
            temp_script_name = temp_script.name

        # 下载脚本
        response = requests.get(url)
        if response.status_code == 200:
            with open(temp_script_name, 'wb') as f:
                f.write(response.content)
        else:
            print(f"下载脚本失败: {response.status_code}")
            return

        # 执行脚本
        await execute_command(f'bash {temp_script_name}')

        # 删除临时文件
        os.remove(temp_script_name)

    except Exception as e:
        print(f"下载或执行脚本时出错: {e}")

async def run_install_scripts():
    # 执行安装脚本
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-socks5/main/install-socks5.sh')
    await delay_time(5000)  # 等待5秒
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-dashboard.sh')
    await delay_time(5000)  # 等待5秒
    await download_and_execute_script('https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-agent.sh')

async def login(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
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

        if is_logged_in:
            # 登录成功后执行安装脚本
            await run_install_scripts()

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        return False

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
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
            message += success_message + '\n'
            print(success_message)
        else:
            message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        # 每个账号登录后随机延迟
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
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
