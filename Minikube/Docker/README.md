# Docker

Following this [post](https://stackify.com/docker-tutorial/) to build a docker image.

Note we are going to use python3 here.

## Build
```docker build -t scweb .```
This builds an image called scweb. Note our [Dockerfile](Dockerfile) ADD the Flask folder as the /app folder for the image.

## Check image
```docker image ls```
You shall see an image called scweb.

## Run 
```docker run --name webapp -p 8080:5000 -d scweb```
Running this image and map 8080 of the host to 5000. Note that the Flask [app](Flask/app.py) is listening to 5000. That is
why we need to map it to 8080 of the host.

Note "-d" means detached mode. 

Then use a browser to go to http://localhost:8080/check
![screen_shot](images/Docker.png).
Ok, our spell checker knows about photon and even quark, but not gluon. So it doesn't really understand Quantum Physics.

## Connect to docker container
* ```docker ps``` shows all the containers. Pay attention to the name. Our container shall be there.
* ```docker exec -it _container_id_ /bin/bash``` allows you to enter to the container and run /bin/bash there. This
goes into the /app folder. Use 'ls' to show all the files installed.
* ```exit``` to exit the container.

## Stop container
```docker stop webapp```

Now
```docker ps``` shows nothing.

## Remove container
```docker rm webapp```

## Next
Now the docker image is ready for use. Go up and try Kubernetes.