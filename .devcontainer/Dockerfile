FROM debian:9   

# sdk version
ARG SDK_VERSION_SHORT=15978945
ARG SDK_SOURCE=https://azuremlsdktestpypi.azureedge.net/CLI-SDK-Runners-Validation/$SDK_VERSION_SHORT
ARG SDK_VERSION_LONG=0.1.0.$SDK_VERSION_SHORT
ARG AZ_EXTENSION_SOURCE=https://azuremlsdktestpypi.azureedge.net/CLI-SDK-Runners-Validation/$SDK_VERSION_SHORT/azure_cli_ml-0.1.0.$SDK_VERSION_SHORT-py3-none-any.whl

# create vsonline
ARG USERNAME=vsonline
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /home/$USERNAME/conda/bin:/home/$USERNAME/.local/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git apt-utils sudo vim htop && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# create vsonline
RUN groupadd --gid $USER_GID $USERNAME && \ 
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get install -y sudo && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME
    
# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME  

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /home/$USERNAME/conda && \
    /home/$USERNAME/conda/bin/pip install --extra-index-url=$SDK_SOURCE azure-cli azureml-defaults==$SDK_VERSION_LONG azureml-pipeline-wrapper[notebooks]==$SDK_VERSION_LONG azureml-pipeline-core==$SDK_VERSION_LONG azure.storage.blob && \
    # /home/$USERNAME/conda/bin/pip install --extra-index-url=$SDK_SOURCE azure-cli && \
    az extension add --source $AZ_EXTENSION_SOURCE --pip-extra-index-urls $SDK_SOURCE --yes --debug && \
    whoami && \
    whoami

USER root

RUN whoami && \
    whoami && \
    ln -s /home/$USERNAME/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". ~/conda/etc/profile.d/conda.sh" >> /home/$USERNAME/.bashrc && \
    echo "conda activate base" >> /home/$USERNAME/.bashrc

ENV TINI_VERSION v0.16.1
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]