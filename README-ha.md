# kubeedge HA study
This is for kubeedge HA version, we will use AKS(Azure Kubernetes Service) to show the demo.

## Pre-requisites
You have created AKS and can connect to the AKS with command line tool kubectl. Please check Azure document to finish it.

## Install Master Node
install service account, cluster role, service, etc
```
cd ha
kubectl create -f 01-ha-prepare.yaml
kubectl create -f 01-5-service.yaml
```

Now check the public IP address:
```
kubectl  get svc -n kubeedge
```
find the external-ip in the output. i.e. 20.240.36.190

open 02-ha-configmap.yaml, modify 'advertiseAddress' to the external-ip you found in above step, then issue:
```
kubectl create -f 02-ha-configmap.yaml
kubectl create -f 03-ha-deployment.yaml
```

now you have installed master node, verify with command:
```
$ kubectl  get node -n kubeedge
NAME                                STATUS   ROLES               AGE   VERSION
aks-agentpool-39110649-vmss000004   Ready    agent               68m   v1.25.6
aks-agentpool-39110649-vmss000005   Ready    agent               65m   v1.25.6
```

```
$ kubectl  get pods -n kubeedge
NAME                         READY   STATUS    RESTARTS   AGE
cloudcore-5dbdf6d86d-pwm9z   1/1     Running   0          3h11m
cloudcore-5dbdf6d86d-xhv2h   1/1     Running   0          3h11m
```

To get the token for edge nodes:
```
kubectl get secret -nkubeedge tokensecret -o=jsonpath='{.data.tokendata}' | base64 -d
```
You should get the token.

## Install edge node
The installation is same as description in single node version, please see README.md, 

Note:
- The --cloudcore-ipport for command 'keadm join' is the external-ip you got above.
- On my raspbian 11 version, only keadm version 1.12.1 works. although the version in the master node is 1.14.0

## Batch deployment
To deploy a model to hundreds of edge nodes, we need batch deployment. The batch deployment is implemented through the package 'helm'.

A helm chart is implmented in the folder chart/, you could check the templates/template.yaml and values.yaml. The file template.yaml includes the persistent volume, persistent volume claim and pod, the file value.yaml includes the variables of each edge node.

When above 2 files are configured properly, just issue the command
```
helm install mnist-image-classification chart/
```
Above will deploy the model to all nodes described in values.yaml.

To uninstall:
```
helm uninstall mnist-image-classification
```

