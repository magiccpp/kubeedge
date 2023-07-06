# Kubernetes Bare Metal Installation
A quick guide for k8s with containerd. The key is to install CNI base and Calico plugin, Otherwise it will not work.

## Install docker and k8s
```
sudo apt update
sudo apt install docker.io
sudo docker --version
sudo systemctl enable docker
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

## Install CNI base
You need to install CNI before you initialize k8s
```
wget https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz
mkdir -p /opt/cni/bin
tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.3.0.tgz 
```

## Install Calico Plugin
Under this directory, you could find calico.yaml, edit the file, find the line:
- name: CALICO_IPV4POOL_CIDR
change its value to the IP range you will assign to pods. i.e.
10.244.0.0/16

Then
```
kubectl apply -f calico.yaml
```

## Initialize K8s
```
sudo kubeadm init --apiserver-advertise-address=192.168.2.22 --pod-network-cidr=192.168.2.0/24
```

After few seconds, the node should be ready:
```
$ kubectl get node
NAME         STATUS   ROLES           AGE   VERSION
k8s-master   Ready    control-plane   13h   v1.27.3
```

## Test K8s
Create a new file nginx-pod.yaml which contains:
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.19.0
    ports:
    - containerPort: 80
```
Then
```
kubectl apply -f nginx-pod.yaml
kubectl port-forward --address 192.168.2.22 pod/nginx 8080:8080
```

Browse http://192.168.2.22:8080 you should see nginx page.


