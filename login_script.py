import paramiko
import time

# 需要访问的面板信息
panels = [
    {"username": "hnxpzjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
    {"username": "hnxczjww", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
    {"username": "WFA77", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
    {"username": "hnxczwwq", "password": "Hnxczww86", "panel": "panel8.serv00.com"},
    {"username": "hnxczww66", "password": "Hnxczww86", "panel": "panel8.serv00.com"}
]

# 需要执行的脚本
script_path = './gaojilingjuli.sh'

# 需要添加的 cron 作业
install_agent_cron_commands = [
    'bash -c "curl -s https://raw.githubusercontent.com/ansoncloud8/am-serv00-nezha/main/install-agent.sh | bash"'
]

reboot_cron_command = [
    '(crontab -l; echo "@reboot pkill -kill -u ${USER} && nohup /home/${USER}/.s5/s5 -c /home/${USER}/.s5/config.json >/dev/null 2>&1 & && nohup /home/${USER}/.nezha-agent/start.sh >/dev/null 2>&1 &") | crontab -'
]

# 逐个访问面板
for panel in panels:
    hostname = panel["panel"]
    username = panel["username"]
    password = panel["password"]

    try:
        # 创建 SSH 客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接到面板
        ssh.connect(hostname, username=username, password=password)
        print(f"成功连接到 {hostname}，用户：{username}")

        # 检查脚本文件是否存在
        stdin, stdout, stderr = ssh.exec_command(f'ls -l {script_path}')
        file_check_output = stdout.read().decode()
        if 'No such file or directory' in file_check_output:
            print(f"文件 {script_path} 不存在。")
        else:
            # 执行脚本
            stdin, stdout, stderr = ssh.exec_command(f'bash {script_path}')
            script_output = stdout.read().decode()
            script_error = stderr.read().decode()

            if script_output:
                print(f"脚本执行输出来自 {hostname}:")
                print(script_output)
            if script_error:
                print(f"脚本执行错误来自 {hostname}:")
                print(script_error)

        # 执行安装代理的 cron 命令
        for cron_command in install_agent_cron_commands:
            print(f"正在执行安装代理的 cron 命令: {cron_command}")
            stdin, stdout, stderr = ssh.exec_command(cron_command)
            time.sleep(1)  # 等待一秒钟以确保 cron 作业被添加
            cron_output = stdout.read().decode()
            cron_error = stderr.read().decode()

            if cron_output:
                print(f"安装代理的 cron 命令输出来自 {hostname}:")
                print(cron_output)
            if cron_error:
                print(f"安装代理的 cron 命令错误来自 {hostname}:")
                print(cron_error)

        # 执行重启时的 cron 命令
        for cron_command in reboot_cron_command:
            print(f"正在执行重启时的 cron 命令: {cron_command}")
            stdin, stdout, stderr = ssh.exec_command(cron_command)
            time.sleep(1)  # 等待一秒钟以确保 cron 作业被添加
            cron_output = stdout.read().decode()
            cron_error = stderr.read().decode()

            if cron_output:
                print(f"重启时的 cron 命令输出来自 {hostname}:")
                print(cron_output)
            if cron_error:
                print(f"重启时的 cron 命令错误来自 {hostname}:")
                print(cron_error)

        # 关闭 SSH 连接
        ssh.close()
    except Exception as e:
        print(f"连接到 {hostname} 失败，用户：{username}，错误：{e}")
