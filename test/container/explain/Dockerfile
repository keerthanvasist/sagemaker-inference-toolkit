# Get MMS Base Python 3.6 CPU image on Ubuntu 16.04 base
FROM awsdeeplearningteam/mxnet-model-server:base-cpu-py3.6

LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true
LABEL com.amazonaws.sagemaker.capabilities.multi-models=true

# Setup Environment for MME
ENV SAGEMAKER_PROGRAM=inference.py
ENV SAGEMAKER_MULTI_MODEL=false
ENV SAGEMAKER_BIND_TO_PORT=${SAGEMAKER_BIND_TO_PORT:-8080}

# Update MMS version
RUN pip3 install multi-model-server

WORKDIR /

RUN mkdir /opt/ml
RUN mkdir /opt/ml/model

COPY sagemaker_inference.tar.gz /sagemaker_inference.tar.gz

RUN pip3 install --no-cache-dir /sagemaker_inference.tar.gz \
 && rm /sagemaker_inference.tar.gz

COPY explain/mms-entrypoint.py /usr/local/bin/dockerd-entrypoint.py

RUN mkdir -p /home/model-server/
COPY explain/inference.py /opt/ml/model/inference.py

EXPOSE 8080

ENTRYPOINT ["python", "/usr/local/bin/dockerd-entrypoint.py"]
CMD ["serve"]
