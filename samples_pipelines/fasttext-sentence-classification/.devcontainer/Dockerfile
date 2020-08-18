FROM debian:9   

# user information
ARG USERNAME=vsonline
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# miniconda
ARG CONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh
ARG CONDA_DIR=/home/$USERNAME/.conda
ARG CONDA_ENV_NAME=azureml
ARG CONDA_ENV_DIR=$CONDA_DIR/envs/$CONDA_ENV_NAME
ARG PYTHON_VERSION=3.7

# sdk version
ARG SDK_VERSION_URL=https://modulesdkpreview.blob.core.windows.net/sdk/preview/version.txt

# env
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH $CONDA_DIR/bin:$CONDA_ENV_DIR/bin:$PATH

# install common softwares
RUN groupadd --gid 800 docker && \
    apt-get update --fix-missing && \
    apt-get install -y apt-utils sudo apt-transport-https wget bzip2 ca-certificates curl gnupg-agent software-properties-common git vim htop tmux && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# add a user named $USERNAME
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    usermod -aG docker $USERNAME && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# change the user
USER $USERNAME

# install azureml sdk
RUN wget --quiet $CONDA_URL -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm -f ~/miniconda.sh && \
    conda init bash && \
    conda create -y -n $CONDA_ENV_NAME python=$PYTHON_VERSION && \
    SDK_VERSION_SHORT=`curl -s $SDK_VERSION_URL` && \
    SDK_VERSION_SHORT=`echo $SDK_VERSION_SHORT | cut -c1-8` && \
    SDK_INDEX=CLI-SDK-Runners-Validation && \
    SDK_SOURCE=https://azuremlsdktestpypi.azureedge.net/$SDK_INDEX/$SDK_VERSION_SHORT && \
    SDK_VERSION_LONG=0.1.0.$SDK_VERSION_SHORT && \
    AZ_EXTENSION_SOURCE=https://azuremlsdktestpypi.azureedge.net/$SDK_INDEX/$SDK_VERSION_SHORT/azure_cli_ml-0.1.0.$SDK_VERSION_SHORT-py3-none-any.whl && \
    $CONDA_DIR/envs/$CONDA_ENV_NAME/bin/pip install pandas azure-cli azureml-pipeline-wrapper[notebooks]==$SDK_VERSION_LONG azureml-dataset-runtime[fuse]==$SDK_VERSION_LONG --extra-index-url=$SDK_SOURCE && \
    az extension add --source $AZ_EXTENSION_SOURCE --pip-extra-index-urls $SDK_SOURCE --yes

# change the user
USER root

# init
ENV TINI_VERSION v0.16.1
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]
