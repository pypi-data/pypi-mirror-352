import paramiko
from mcp_k8s_install.core.ssh_client import ssh_client

class install_tools:

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    async def exec(self, ssh_data: ssh_client, commands: list) -> list:

        log = []
        self.ssh.connect(hostname=ssh_data.hostname,
                         port=ssh_data.port,
                         username=ssh_data.username,
                         password=ssh_data.pwd,
                         allow_agent=False,
                         look_for_keys=False)
        try:
            for command in commands:
                stdin, stdout, error = self.ssh.exec_command(command)

                if stdout.channel.recv_exit_status() == 0:
                    txt = stdout.read().decode()
                    if txt:
                        log.append( stdout.read().decode() )
                else:
                    log.append( error.read().decode() )
                    break
        finally:
            self.ssh.close()
            return log




    async def k8s_master_install(self, ssh_data: ssh_client) -> str:
        commands = [
            # linux settings
            'sudo setenforce 0',
            "sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config",
            'sudo systemctl stop firewalld; sudo systemctl disable firewalld',
            "sudo swapoff -a && sed -i '/ swap / s/^/#/' /etc/fstab",
            """cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF""",
            "sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
            'sudo dnf install -y containerd.io iproute-tc',
            'sudo modprobe br_netfilter',
            'sudo modprobe overlay',
            'sudo sysctl --system',
            'sudo systemctl start containerd',
            """cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/repodata/repomd.xml.key
EOF""",
            'sudo dnf install -y kubelet kubectl kubeadm',
            'sudo systemctl start kubelet; sudo systemctl enable kubelet',

            # k8s settings
            'sudo rm /etc/containerd/config.toml',
            'sudo containerd config default | sudo tee /etc/containerd/config.toml',
            'sudo systemctl restart containerd',
            'sudo ip route del 10.0.0.0/8; sudo ip route add 10.0.0.0/16 dev enp0s3; sudo systemctl restart NetworkManager',
            "sudo kubeadm init --pod-network-cidr=10.244.0.0/16 | tail -n 2 > token.txt",
            'mkdir -p $HOME/.kube',
            'sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config',
            'sudo chown $(id -u):$(id -g) $HOME/.kube/config',
            'kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml'
            ]

        await self.exec(ssh_data=ssh_data, commands=commands)
        return "install Complete"

    def k8s_client_install(self, ssh_data: ssh_client):

        commands = [
            # linux settings
            'sudo setenforce 0',
            "sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config",
            'sudo systemctl stop firewalld',
            'sudo systemctl disable firewalld',
            "sudo swapoff -a && sed -i '/ swap / s/^/#/' /etc/fstab",
            """cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF""",
            "sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
            'sudo dnf install -y containerd.io iproute-tc',
            'sudo modprobe br_netfilter',
            'sudo modprobe overlay',
            'sudo sysctl --system',
            'sudo systemctl start containerd',
            """cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.29/rpm/repodata/repomd.xml.key
EOF""",
            'sudo dnf install -y kubelet kubectl kubeadm',
            'sudo systemctl start kubelet; sudo systemctl enable kubelet',
        ]
        return self.exec(ssh_data=ssh_data, commands=commands)

install = install_tools()

