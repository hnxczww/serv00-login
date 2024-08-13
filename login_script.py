import subprocess
import sys
import asyncio
import asyncssh

def install(package):
    """安装指定的 Python 包"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 检查并安装 asyncssh 模块
try:
    import asyncssh
except ImportError:
    print("未安装 asyncssh，正在安装...")
    install('asyncssh')

async def execute_command(client, command):
    """执行命令并打印返回数据"""
    print(f"执行命令: {command}")
    async with client.create_process(command) as proc:
        stdout, stderr = await proc.communicate()
        
        # 打印命令的标准输出
        print("标准输出：")
        print(stdout.decode().strip())

        # 打印命令的标准错误（如果有）
        if stderr:
            print("标准错误：")
            print(stderr.decode().strip())

        # 打印命令的退出状态码
        exit_status = proc.returncode
        print(f"退出状态码: {exit_status}")
        print("-" * 40)  # 分隔符

async def process_server(server):
    """处理单个服务器的连接和命令执行"""
    hostname = server["panel"]
    port = 22  # 默认的 SSH 端口
    username = server["username"]
    password = server["password"]
    script_path = './gaojilingjuli.sh'

    # 创建 SSH 客户端实例
    try:
        async with asyncssh.connect(
            hostname, port, username=username, password=password,
            known_hosts=None  # 禁用主机密钥验证
        ) as client:
            print(f"连接成功到 {hostname}")

            # 设置 crontab 任务
            print("设置 crontab 任务...")
            cron_commands = [
                '(crontab -l; echo "@reboot pkill -kill -u ${USER} && nohup /home/${USER}/.s5/s5 -c /home/${USER}/.s5/config.json >/dev/null 2>&1 & && nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -',
                '(crontab -l; echo "*/12 * * * * pgrep -x \\"nezha-agent\\" > /dev/null || nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -'
            ]

            for command in cron_commands:
                await execute_command(client, command)
                await asyncio.sleep(5)  # 异步等待 5 秒以确保 crontab 任务被正确设置

            # 打印当前目录（可选）
            await execute_command(client, 'pwd')

            # 执行 shell 脚本
            print(f"准备执行脚本: {script_path}")
            await execute_command(client, f"bash {script_path}")

    except asyncssh.HostKeyNotVerifiable as e:
        print(f"主机密钥不可验证: {e}")
    except Exception as e:
        print(f"在服务器 {hostname} 上发生异常: {e}")

async def main():
    servers = [
        {"username": "hnxpzjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "WFA77", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczwwq", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczww66", "password": "Hnxczww86", "panel": "panel8.serv00.com"}
    ]

    tasks = [process_server(server) for server in servers]
    await asyncio.gather(*tasks)  # 并发执行所有服务器任务

if __name__ == "__main__":
    asyncio.run(main())
