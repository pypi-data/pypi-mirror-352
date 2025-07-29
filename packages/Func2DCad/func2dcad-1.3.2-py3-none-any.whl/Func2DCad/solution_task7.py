import paramiko
import getpass
import sys
import ssh_config

def ssh_connect(hostname: str, port: int, username: str, password: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, port=port,
                       username=username, password=password, timeout=10)
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
    print("=== Задача 7: Поля сообщения geometry_msgs/Twist ===")
    ssh_client = ssh_connect(
        ssh_config.HOSTNAME, ssh_config.PORT, ssh_config.USERNAME, ssh_config.PASSWORD)

    # Попробуем ROS1
    out, err = run_command(ssh_client, "rosmsg show geometry_msgs/Twist")
    if err:
        # Если не получилось, пробуем ROS2
        out2, err2 = run_command(
            ssh_client, "ros2 interface show geometry_msgs/msg/Twist")
        if out2:
            print("Поля сообщения geometry_msgs/msg/Twist (ROS 2):")
            print(out2)
        else:
            print(
                "Ошибка при 'rosmsg show geometry_msgs/Twist' и 'ros2 interface show geometry_msgs/msg/Twist':")
            print(err or err2)
    else:
        print("Поля сообщения geometry_msgs/Twist (ROS 1):")
        print(out)

    ssh_client.close()


if __name__ == "__main__":
    main()
