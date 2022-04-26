FROM zenika/alpine-chrome:latest

USER root
RUN apk add bash grep curl python3 python3-dev py3-pip pcre-tools


RUN mkdir -p /crawlalllinks

COPY requirements.txt /crawlalllinks/

RUN pip install -r /crawlalllinks/requirements.txt

# ENTRYPOINT 'bash'

# RUN pyppeteer-install

COPY sources/* /crawlalllinks/sources/

WORKDIR /crawlalllinks/sources

#ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["python3","crawlalllinks.py"]