import paramiko
from mcp_k8s_install.core.ssh_client import ssh_client
class utils_tools():

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def notify(self, ssh_data: ssh_client, message: str) -> str:
        self.ssh.connect(hostname=ssh_data.hostname,
                    port=ssh_data.port,
                    username=ssh_data.username,
                    password=ssh_data.pwd,
                    allow_agent=True,
                    look_for_keys=True)

        try:
            stdin, stdout, error = self.ssh.exec_command(f'wall {message}')
            status = stdout.channel.recv_exit_status()

            if status == 0: # 정상 실행 완료
                output = stdout.read().decode()
                return output
            else: # 에러 출력문
                error = error.read().decode()
                return "에러 발생" + error

        except paramiko.AuthenticationException:
            return "인증 실패: 사용자 이름 또는 비밀번호를 확인하세요."
        except paramiko.SSHException as sshException:
            return f"SSH 예외 발생: {sshException}"
        except Exception as e:
            return f"알 수 없는 오류 발생: {e}"

        finally:
            self.ssh.close()

    async def exec(self, ssh_data: ssh_client, command: str):
        self.ssh.connect(hostname=ssh_data.hostname,
                    port=ssh_data.port,
                    username=ssh_data.username,
                    password=ssh_data.pwd,
                    allow_agent=True,
                    look_for_keys=True)

        try:
            stdin, stdout, error = self.ssh.exec_command(command)
            status = stdout.channel.recv_exit_status()

            if status == 0: # 정상 실행 완료
                output = stdout.read().decode()
                return output
            else: # 에러 출력문
                error = error.read().decode()
                return "에러 발생" + error

        except paramiko.AuthenticationException:
            return "인증 실패: 사용자 이름 또는 비밀번호를 확인하세요."
        except paramiko.SSHException as sshException:
            return f"SSH 예외 발생: {sshException}"
        except Exception as e:
            return f"알 수 없는 오류 발생: {e}"

        finally:
            self.ssh.close()

    def update(self, ssh_data: ssh_client):

        self.exec(ssh_data=ssh_data, command="sudo dnf -y update")
        return "업데이트 완료"

utils = utils_tools()