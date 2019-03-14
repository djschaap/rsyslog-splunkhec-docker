FROM rsyslog/syslog_appliance_alpine:8.36.0-3.7
LABEL maintainer="djschaap@gmail.com"
RUN apk --no-cache add python \
  && apk --no-cache add --virtual .build-deps curl py2-pip \
  && pip install requests \
  && sed -i -re 's/^(export ENABLE_LOGFILES\s*=\s*)/#\1/' \
     /home/appliance/internal/container_config \
  && apk --no-cache del .build-deps

#  && curl -o /config/omsplunkhec.py -k \
#     https://bitbucket.org/rfaircloth-splunk/rsyslog-omsplunk/raw/cca949cd5896d5a34be1e7358b3f3467977a4e1f/omsplunkhec.py \

# store omsplunkhec.py in /config as /usr/bin may be read-only
# wget fails with: TLS error from peer (alert code 40): handshake failure
#   wget https://bitbucket.org/rfaircloth-splunk/rsyslog-omsplunk/raw/cca949cd5896d5a34be1e7358b3f3467977a4e1f/omsplunkhec.py
# HACK: using curl -k due to Sentinel WSA interception
COPY config /config

#ENV CUSTOMER_ID=00000
ENV ENABLE_LOGFILES=off
#ENV HEC_HOST=splunk-hf
#ENV HEC_TOKEN=00000000-0000-0000-0000-000000000000
