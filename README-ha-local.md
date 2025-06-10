1. install kubeadm...
   https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/

2. setup containerd with /etc/containerd/config.toml
```
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "registry.k8s.io/pause:3.10"
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
      SystemdCgroup = true
```

kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

3. sudo kubeadm init --apiserver-advertise-address=192.168.2.60


sudo kubeadm reset -f
sudo systemctl stop kubelet
sudo systemctl disable kubelet



Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.2.60:6443 --token 5iumd6.anuburarkpk0iskr \
        --discovery-token-ca-cert-hash sha256:0ebb04e9ecec5ab9677c1898a8d6905d0ffedea429ee4a5ee119ff90132b0b84


kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml


