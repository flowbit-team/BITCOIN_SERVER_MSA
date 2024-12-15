FROM python:3.10-bullseye
ADD . /flask
WORKDIR /flask
RUN pip install --upgrade pip
RUN #apt-get update && apt-get install -y libhdf5-dev
RUN pip install -r requirement.txt
RUN pip install openai==0.28
RUN pip install py_eureka_client
RUN pip install numpy
RUN #python -u main.py