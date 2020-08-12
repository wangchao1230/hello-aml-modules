#### Steps to create your own image

1. Login in to docker: ```docker login```		
2. Make an empty directory and move the ```Dockerfile``` into it. Modify this ```Dockerfile``` as you like.
3. Build an image named ```my_image```:  ```docker build -t my_image .```
4. Give this image a tag : ```docker tag my_image littlehaes/azureml-sdk``` Attention: you need to change ```littlehaes``` to your own docker account name.
5. Push this image to the docker hub: ```docker push littlehaes/azureml-sdk```



