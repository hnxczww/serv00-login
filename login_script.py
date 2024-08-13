import paramiko
import time

def install_package(package):
    """安装指定的 Python 包"""
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    # 远程服务器的凭据
    hostname = 'panel8.serv00.com'
    port = 22  # 默认的 SSH 端口
    username = 'hnxczwwq'
    password = 'Hnxczww86'
    script_path = './gaojilingjuli.sh'

    # 创建 SSH 客户端实例
    client = paramiko.SSHClient()

    # 自动添加服务器的主机密钥（使用时请谨慎）
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接到远程服务器
        print("正在尝试连接到远程服务器...")
        client.connect(hostname, port, username, password)
        print("连接成功")

        # 打印当前目录（可选）
        stdin, stdout, stderr = client.exec_command('pwd')
        print(f"远程当前工作目录: {stdout.read().decode().strip()}")

        # 打印 shell 脚本的路径（可选）
        print(f"准备执行脚本: {script_path}")

        # 执行 shell 脚本
        command = f"bash {script_path}"
        print(f"执行命令: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        # 打印脚本的标准输出
        print("脚本输出：")
        for line in iter(stdout.readline, ''):
            print(line.strip())

        # 打印脚本的标准错误（如果有）
        error = stderr.read().decode()
        if error:
            print("脚本错误：")
            print(error)

        # 打印执行过程中的所有日志（在脚本的运行过程中）
        while not stdout.channel.exit_status_ready():
            time.sleep(1)
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode()
                print(output, end='')

        # 打印脚本的退出状态码
        exit_status = stdout.channel.recv_exit_status()
        print(f"脚本退出状态码: {exit_status}")

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        # 关闭连接
        client.close()
        print("连接关闭")

if __name__ == "__main__":
    main()
