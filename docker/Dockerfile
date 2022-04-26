FROM python:3.10-buster

USER root

RUN mkdir -p /supptruder/sources
RUN mkdir -p /supptruder/database
RUN mkdir -p /supptruder/tampers


COPY requirements.txt /supptruder/

RUN pip install -r /supptruder/requirements.txt

COPY sources/* /supptruder/sources/
COPY tampers/* /supptruder/tampers/
COPY database/* /supptruder/database/
COPY supptruder.py /supptruder/

WORKDIR /supptruder

# ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["python3","supptruder.py"]