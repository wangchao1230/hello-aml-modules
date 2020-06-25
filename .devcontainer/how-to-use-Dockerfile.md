#### Steps to create your own image

1. login in to docker: ```docker login```		
2. make an empty directory and move the ```Dockerfile``` into it. Modify this ```Dockerfile``` as you like.
3. build an image and name it as mine:  ```docker build -t mine .```
4. give this image a tag : ```docker tag mine littlehaes/azureml-demo``` Attention: you need to change ```littlehaes``` to the repository name in your docker hub
5. push this image to the your docker hub: ```docker push littlehaes/azureml-demo```



