#!/bin/bash
# If you want to create your own image. Modify the Dockerfile. Then run this shell script: bash build_image.sh
# We highly recommend to use image instead of Dockerfile in 'devcontainer.json'
# Because pulling an image is much faster than building an image

# Input the username of your docker hub
echo -e '\nPlease input the username of your docker hub'
echo -e 'Username: \c'
read line
USERNAME=$line
# Login to your docker hub
docker login -u ${USERNAME}
# Get the lataest version number of azureml sdk as the image tag
SDK_VERSION_SHORT=`curl -s https://modulesdkpreview.blob.core.windows.net/sdk/preview/version.txt`
SDK_VERSION_SHORT=${SDK_VERSION_SHORT:0:8}
# The repository name displayed on docker hub
REPOSITORY_NAME=modulesdkpreview
# The complete name of the image with a tag
TARGET_NAME=${USERNAME}/${REPOSITORY_NAME}:$SDK_VERSION_SHORT
LATEST_NAME=${USERNAME}/${REPOSITORY_NAME}:latest
# Build an image from a Dockerfile
docker build -t ${TARGET_NAME} .
# Check whether the build process is executed successfully
if [[ $? != 0 ]]; then
        echo 'Build failed. Please check your Dockerfile'
        exit
fi
docker push ${TARGET_NAME}
# Update the latest version
docker tag ${TARGET_NAME} ${LATEST_NAME}
docker push ${LATEST_NAME}
# Update the image name in devcontainer.json
quote='"'
cmd="sed -i 's/^\t${quote}image${quote}:.*$/\t${quote}image${quote}:${quote}${USERNAME}\/${REPOSITORY_NAME}${quote},/' devcontainer.json"
eval ${cmd}