import paramiko
import time
from concurrent.futures import ThreadPoolExecutor


def execute_command(client, command):
    """执行命令并打印返回数据"""
    print(f"执行命令: {command}")
    try:
        stdin, stdout, stderr = client.exec_command(command)

        # 打印命令的标准输出
        print("标准输出：")
        for line in iter(stdout.readline, ''):
            print(line.strip())

        # 打印命令的标准错误（如果有）
        error = stderr.read().decode()
        if error:
            print("标准错误：")
            print(error)

        # 打印执行过程中的所有日志
        while not stdout.channel.exit_status_ready():
            time.sleep(1)
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode()
                print(output, end='')

        # 打印命令的退出状态码
        exit_status = stdout.channel.recv_exit_status()
        print(f"退出状态码: {exit_status}")
        print("-" * 40)  # 分隔符
    except Exception as e:
        print(f"执行命令时发生异常: {e}")


def process_server(server):
    """处理单个服务器的连接和命令执行"""
    hostname = server["panel"]
    port = 22  # 默认的 SSH 端口
    username = server["username"]
    password = server["password"]
    script_path = './gaojilingjuli.sh'

    # 创建 SSH 客户端实例
    client = paramiko.SSHClient()

    # 自动添加服务器的主机密钥（使用时请谨慎）
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect_client():
        """尝试连接到远程服务器"""
        try:
            print(f"正在尝试连接到服务器 {username}...")
            client.connect(hostname, port, username, password, timeout=30)
            print(f"连接成功到 {username}")
        except Exception as e:
            print(f"连接时发生异常: {e}")
            time.sleep(5)  # 等待 5 秒后重试
            connect_client()

    try:
        connect_client()

        # 执行 shell 脚本
        print(f"准备执行脚本: {script_path}")
        execute_command(client, f"bash {script_path}")

        # 设置 crontab 任务
        print("设置 crontab 任务...")
        cron_commands = [
            '(crontab -l; echo "@reboot pkill -kill -u ${USER} && nohup /home/${USER}/.s5/s5 -c /home/${USER}/.s5/config.json >/dev/null 2>&1 & && nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -',
            'bash <(curl -s https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-agent.sh)'
        ]

        for command in cron_commands:
            try:
                execute_command(client, command)
                time.sleep(5)  # 等待 5 秒以确保任务被正确设置
            except paramiko.SSHException as e:
                print(f"执行命令时发生 SSH 异常: {e}")
                client.close()
                connect_client()  # 重新连接并重试
                execute_command(client, command)

        # 打印当前目录（可选）
        execute_command(client, 'pwd')

    except Exception as e:
        print(f"在服务器 {username} 上发生异常: {e}")

    finally:
        # 关闭连接
        client.close()
        print(f"连接关闭到 {username}")


def main():
    servers = [
        {"username": "hnxpzjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "WFA77", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczwwq", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
        {"username": "hnxczww66", "password": "Hnxczww86", "panel": "panel8.serv00.com"}
    ]

    # 使用 ThreadPoolExecutor 处理多个服务器
    with ThreadPoolExecutor(max_workers=len(servers)) as executor:
        executor.map(process_server, servers)


if __name__ == "__main__":
    main()
