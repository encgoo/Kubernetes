# Kubernetes

This is a POC project for using Kubernetes/Docker/Flask API. Dependencies
* Minikube
* Docker
* python Flask

The above techniques are used to demo an online spell checker 
implemented using butterfly filter in python.

## Project structure 
The structure of this repo
* Minikube
    * Docker
        * Flask
            * BloomFilter
            
## Approach
Do it from inside out. 
1. First go to the BloomFilter folder to test the bloom filter as a standalone python program. 
Make sure you can generate a bitmap.bin file. This file is used by others.
2. Go to the Flask folder, make sure you can use the bloomfilter from a flask server
3. Go to the Docker folder, make sure you can use the flask server in a docker container.
4. Back to this folder, and try Kubernetes.

## Minikube
Here we follow this [post](https://linuxhint.com/kubernetes-getting-started/) and use Minikube on Linux to create
local Kubernetes cluster.

### Environment
This is running on virtual machine of Debian 9 using virtualbox. To setup minikube of virtual machine, follow this
[post](https://medium.com/@vovaprivalov/setup-minikube-on-virtualbox-7cba363ca3bc). The above post has instruction about
installing kubectl as well. 

### Steps
1. Make sure you follow the steps in the Approach section above to build and test the docker image. Run ```docker image ls```
and you shall see scweb is listed there.
2. Start minikube. Since we are using virtual machine, need to start it with vm_driver=none as suggested by 
this [post](https://medium.com/@vovaprivalov/setup-minikube-on-virtualbox-7cba363ca3bc).
```sudo -E minikube start --vm-driver=none```

Use ```kubectl cluster-info``` to make sure minikube is running.
3. Run a node ```kubectl run my-node --image=scweb --port=5000 --image-pull-policy=Never```
4. Check deployment ```kubectl get deployments```
5. Check pods ```kubectl get pods```
6. Create a servide ```kubectl expose deploment my-node --type=LoadBalancer```
7. Check service ```kubectl get services``` Take note of the PORT(S) of my-node. 
![screenshot](images/ports.png)
In this example, port 30471 is mapped to the port 5000 of the docker container. 
8. Use the port information above to test the deployment/service. 
For our example here, use http://localhost:30471/check

### Stop and clean up
```kubectl delete service my-node```

```kubectl delete deployment my-node```

```minikube stop```
            
 