# If you want to create your own image. Modify the Dockerfile. Then run this shell script: bash build_image.sh
# We highly recommend to use image instead of Dockerfile in 'devcontainer.json'
# Because pulling an image is much faster than building an image

# input the username of your docker hub
echo -e '\nPlease input the username of your docker hub'
echo -e 'Username: \c'
read line
USERNAME=$line
# login to your docker hub
docker login -u ${USERNAME}
# get the lataest version number of azureml sdk as the image tag
SDK_VERSION_SHORT=`curl -s https://modulesdkpreview.blob.core.windows.net/sdk/preview/version.txt`
SDK_VERSION_SHORT=${SDK_VERSION_SHORT:0:8}
# the repository name displayed on docker hub
REPOSITORY_NAME=azureml-sdk
# the complete name of the image with a tag
TARGET_NAME=${USERNAME}/${REPOSITORY_NAME}:$SDK_VERSION_SHORT
LATEST_NAME=${USERNAME}/${REPOSITORY_NAME}:latest
# build an image from a Dockerfile
docker build -t ${TARGET_NAME} .
docker push ${TARGET_NAME}
# update the latest version
docker tag ${TARGET_NAME} ${LATEST_NAME}
docker push ${LATEST_NAME}