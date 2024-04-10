FROM python:3.10-bullseye
ADD . /flask
WORKDIR /flask
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirement.txt
RUN pip install openai==0.28
RUN pip install py_eureka_client
RUN pip install numpy
