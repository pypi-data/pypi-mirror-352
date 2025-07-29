import paramiko
import getpass
import sys
import ssh_config

def ssh_connect(hostname: str, port: int, username: str, password: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, port=port, username=username, password=password, timeout=10)
    except Exception as e:
        print(f"Ошибка подключения по SSH: {e}")
        sys.exit(1)
    return client

def run_command(ssh_client: paramiko.SSHClient, command: str):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    out = stdout.read().decode("utf-8")
    err = stderr.read().decode("utf-8")
    return out.strip(), err.strip()

def main():
    print("=== Задача 8: Определение IP-адреса агроровера ===")
    ssh_client = ssh_connect(ssh_config.HOSTNAME, ssh_config.PORT, ssh_config.USERNAME, ssh_config.PASSWORD)
    
    # Пробуем ifconfig
    out, err = run_command(ssh_client, "ifconfig | grep 'inet '")
    if out:
        print("Вывод ifconfig (фильтр 'inet '):")
        print(out)
    else:
        # fallback: ip addr show
        out2, err2 = run_command(ssh_client, "ip addr show | grep 'inet '")
        if out2:
            print("Вывод ip addr show (фильтр 'inet '):")
            print(out2)
        else:
            print("Не удалось получить IP через ifconfig и ip addr:")
            print(err or err2)
    
    ssh_client.close()

if __name__ == "__main__":
    main()
