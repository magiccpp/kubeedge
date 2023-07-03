# kubeedge study
A quick study on kubeedge

## installation on master node
install minikube
https://minikube.sigs.k8s.io/docs/start/

find out raspberry pi listening on port 22
```
nmap -p 22 192.168.2.2-100
```

get minikube ip:
```
minikube ip    #the output is 192.168.49.2
```

initialize kubeedge
```
sudo keadm init –advertise-address="192.168.49.2" --profile version=v1.12.1 –kube-config=${HOME}/.kube/config

#if something is wrong, reset and try again
#sudo keadm reset –kube-config=${HOME}/.kube/config

# now you should see the master node status:


kubectl get all -n kubeedge
NAME                             READY   STATUS    RESTARTS   AGE
pod/cloudcore-6d76c7f978-zflh7   1/1     Running   0          32h

NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                             AGE
service/cloudcore   ClusterIP   10.104.197.29   <none>        10000/TCP,10001/TCP,10002/TCP,10003/TCP,10004/TCP   32h

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cloudcore   1/1     1            1           32h

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/cloudcore-6d76c7f978   1         1         1       32h
```


below commands are added by myself, to let raspberry access the minikube internal IP, you may find better approches.
```
sudo iptables -t nat -A PREROUTING -p tcp --dport 10000 -j DNAT --to-destination 192.168.49.2:10000
sudo iptables -A FORWARD -p tcp --dport 10000 -d 192.168.49.2 -j ACCEPT

sudo iptables -t nat -A PREROUTING -p tcp --dport 10002 -j DNAT --to-destination 192.168.49.2:10002
sudo iptables -A FORWARD -p tcp --dport 10002 -d 192.168.49.2 -j ACCEPT

```
get the token and we are finished with cloud side
```
keadm gettoken --kube-config=${HOME}/.kube/config
a5e8b42c28f395b978d14d391f9ec134677b0af661e9deb65a51861037b9ed82.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODc5ODQ4NzF9.L6ZpkJQd5qKK_kgN04j_0MqF3okyl6Beh2s14PoegVo
```

## installation on edge node
### install docker
```
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/raspbian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
# exit and login again.
```

### install kubeedge
```
wget https://github.com/kubeedge/kubeedge/releases/download/v1.12.1/keadm-v1.12.1-linux-arm.tar.gz
tar -zxvf keadm-v1.12.1-linux-arm.tar.gz
sudo cp keadm-v1.12.1-linux-arm/keadm/keadm /usr/local/bin/keadm
```
### start edge
```
sudo keadm join --cloudcore-ipport=192.168.49.2:10000 --token=a5e8b42c28f395b978d14d391f9ec134677b0af661e9deb65a51861037b9ed82.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODc5ODQ4NzF9.L6ZpkJQd5qKK_kgN04j_0MqF3okyl6Beh2s14PoegVo --kubeedge-version=v1.12.1 --cgroupdriver=systemd
```

```
systemctl start edgecore
systemctl status edgecore
```
it should be started.

if something is wrong on the edge, do below to reset
```
sudo docker stop $(docker ps -aq) && sudo docker rm $(docker ps -aq)
sudo rm -r /etc/kubeedge/
```

## deploy a pod 
from the master node I can see the 3 nodes
```
kubectl get nodes --show-labels
          STATUS   ROLES           AGE   VERSION                    LABELS
minikube       Ready    control-plane   34h   v1.26.3                    beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=minikube,kubernetes.io/os=linux,minikube.k8s.io/commit=08896fd1dc362c097c925146c4a0d0dac715ace0,minikube.k8s.io/name=minikube,minikube.k8s.io/primary=true,minikube.k8s.io/updated_at=2023_06_27T20_16_16_0700,minikube.k8s.io/version=v1.30.1,node-role.kubernetes.io/control-plane=,node.kubernetes.io/exclude-from-external-load-balancers=
raspberrypi    Ready    agent,edge      13h   v1.22.6-kubeedge-v1.12.1   beta.kubernetes.io/arch=arm,beta.kubernetes.io/os=linux,kubernetes.io/arch=arm,kubernetes.io/hostname=raspberrypi,kubernetes.io/os=linux,node-role.kubernetes.io/agent=,node-role.kubernetes.io/edge=
raspberrypi2   Ready    agent,edge      11h   v1.22.6-kubeedge-v1.12.1   beta.kubernetes.io/arch=arm,beta.kubernetes.io/os=linux,kubernetes.io/arch=arm,kubernetes.io/hostname=raspberrypi2,kubernetes.io/os=linux,node-role.kubernetes.io/agent=,node-role.kubernetes.io/edge=
```


Now we can deploy the image to the edge, I have created an image which contains a convolutional neural network for image classification.
```
kubectl apply -f single-node/mnist1.yaml
```

Now you can test the model on the edge node, 
copy the image to the edge node and issue below command, you will see the image is classified as '4'
```
curl -X POST -F "image=@./test_image.png" http://172.17.0.3:8080/predict
{"class": 4}
```
The container is ephemeral. Every time the web server processes an image, a grayscale image will be written to the local storage /mnt/volume.
Check if it works fine.


## startup GUI
on your master node, issue below command:
```
$ minikube dashboard
🤔  Verifying dashboard health ...
🚀  Launching proxy ...
🤔  Verifying proxy health ...
🎉  Opening http://127.0.0.1:43353/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/ in your default browser...
Opening in existing browser session.
libva error: vaGetDriverNameByIndex() failed with unknown libva error, driver_name = (null)
```
then you can check the status of your nodes, including CPU/RAM usage.

TO access the GUI from another computer, 
```
$kubectl proxy --address='0.0.0.0' --disable-filter=true
W0629 05:15:17.554860 2112861 proxy.go:175] Request filter disabled, your proxy is vulnerable to XSRF attacks, please be cautious
Starting to serve on [::]:8001
```
then I can access the GUI from another computer with the IP of master node
http://192.168.2.16:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/

## Subscribe to MQTT message
The demo code publish MQTT message on the topic "image_classfication", on the edge node, you could subscribe the topic with command:
```
mosquitto_sub -h 192.168.2.19 -p 1883  -t image_classification
```
Above command will wait for MQTT messages, when you send the image to the web server again:
```
curl -X POST -F "image=@./test_image.png" http://172.17.0.3:8080/predict
```

you will see a '4' appears, that is the MQTT message received by mosquitto_sub.


## Enable kubectl logs function
On master node, issue below to disable the kubeproxy on the edge node.
```
kubectl patch daemonset kube-proxy -n kube-system -p '{"spec": {"template": {"spec": {"affinity": {"nodeAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": {"nodeSelectorTerms": [{"matchExpressions": [{"key": "node-role.kubernetes.io/edge", "operator": "DoesNotExist"}]}]}}}}}}}'
```
Make sure you could access the port 10004 on cloud.
```
nc -zv 192.168.49.2 10004
```
Enable cloudStream

## Note
- the speed of the SD card is critical, use below command to test the speed:
```
dd if=/dev/zero of=/tmp/tempfile bs=1M count=100 conv=fdatasync,notrunc
```
- check if the performance of the raspberry pi is throttled:
```
$ vcgencmd get_throttled
throttled=0x0
```
Make sure the output is 'throttled=0x0' which indicates that the performance is not throttled.

