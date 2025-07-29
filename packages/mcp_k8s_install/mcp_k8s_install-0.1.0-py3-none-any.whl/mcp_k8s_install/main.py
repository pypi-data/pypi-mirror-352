
from mcp_k8s_install.core.mcp_instance import mcp
from mcp_k8s_install.function.utils import utils
from mcp_k8s_install.function.install import install
from mcp_k8s_install.core.ssh_client import ssh_client,ssh_master_data, ssh_client_data


@mcp.tool()
def set_master_ssh(self, hostname: str, pwd: str, username='root', port=22) -> str:
    """master ssh 정보 설정"""
    return ssh_master_data.update_ssh_client(hostname=hostname, pwd=pwd, username=username, port=port)

def set_client_ssh(self, hostname: str, pwd: str, username='root', port=22) -> list:
    """client ssh 정보 설정"""
    ssh_client_data.append( ssh_client(hostname=hostname, pwd=pwd, username=username, port=port) )
    return ssh_client_data


@mcp.tool()
def notice(self,message:str) -> str:
    """연결 테스트하기"""
    return utils.notify(ssh_data= ssh_master_data, message= message)

@mcp.tool()
def exec(self, command:str) -> str:
    """커맨드 실행하기"""
    return utils.exec(ssh_data=ssh_master_data, command=command)

@mcp.tool()
def update(self) -> str:
    """dnf update: 장시간 걸리므로 계속 기다릴것 """
    return utils.update(ssh_data=ssh_master_data)

@mcp.tool()
async def k8s_master_install(self) -> str:
    """dnf update 수행 후 kubernetes(k8s) master 자동화 설치하기: 장시간 걸리므로 계속 기다릴것"""
    await install.k8s_master_install(ssh_data=ssh_master_data)
    ssh_master_data.set_token(token= await utils.exec(ssh_data=ssh_master_data, command="cat token.txt") )
    return "설치 완료"

@mcp.tool()
async def k8s_master_token(self) -> str:
    """k8s의 마스터 노드의 토큰 정보 확인"""
    if not ssh_master_data.token:
        ssh_master_data.set_token(await utils.exec(ssh_data=ssh_master_data, command="cat token.txt"))
    return ssh_master_data.token

# @mcp.tool()
# def k8s_client_install(self) -> list:
#     """kubernetes(k8s) client 자동화 설치하기"""
#     return install.k8s_client_install()



if __name__:
    mcp.run()