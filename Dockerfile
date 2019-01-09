FROM rsyslog/syslog_appliance_alpine:8.36.0-3.7
LABEL maintainer="djschaap@gmail.com"
RUN apk --no-cache add python \
  && apk --no-cache add --virtual .build-deps curl py2-pip \
  && pip install requests \
  && curl -o /usr/bin/omsplunkhec.py https://bitbucket.org/rfaircloth-splunk/rsyslog-omsplunk/raw/cca949cd5896d5a34be1e7358b3f3467977a4e1f/omsplunkhec.py \
  && chmod 0755 /usr/bin/omsplunkhec.py \
  && apk --no-cache del .build-deps
# wget fails with: TLS error from peer (alert code 40): handshake failure
# wget https://bitbucket.org/rfaircloth-splunk/rsyslog-omsplunk/raw/cca949cd5896d5a34be1e7358b3f3467977a4e1f/omsplunkhec.py
