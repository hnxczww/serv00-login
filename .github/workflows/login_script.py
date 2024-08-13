import json
import subprocess
import requests

# 读取 accounts.json 文件
with open('accounts.json') as f:
    servers = json.load(f)

# 登录函数
def login(server):
    username = server['username']
    password = server['password']
    panel = server['panel']
    
    # 模拟登录过程（根据实际情况修改）
    response = requests.post(f"http://{panel}/login", data={'username': username, 'password': password})
    
    if response.status_code == 200:
        print(f"登录成功: {username}@{panel}")
        return True
    else:
        print(f"登录失败: {username}@{panel}")
        return False

# 运行安装脚本函数
def run_install_scripts():
    scripts = [
        "https://raw.githubusercontent.com/ansoncloud8/am-serv00-socks5/main/install-socks5.sh",
        "https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-dashboard.sh",
        "https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-agent.sh"
    ]
    for script in scripts:
        subprocess.run(['bash', <(curl -s {script})], check=True)
        print(f"执行完脚本: {script}")

# 主程序
for server in servers:
    if login(server):
        run_install_scripts()
