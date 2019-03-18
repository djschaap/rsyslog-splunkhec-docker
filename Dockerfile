FROM alpine:3.9
LABEL maintainer="djschaap@gmail.com"
VOLUME /config /work /logs
RUN apk --no-cache add python \
  && apk --no-cache add --virtual .build-deps \
  && apk --no-cache add \
     liblognorm \
     py2-pip \
     rsyslog \
     rsyslog-mmjsonparse \
     rsyslog-mmnormalize \
     rsyslog-mmutf8fix \
  && pip install requests \
  && apk --no-cache del .build-deps \
  && addgroup -S rsyslog \
  && adduser -S -D -s /bin/sh rsyslog rsyslog \
  && chown -R rsyslog.rsyslog /logs /work

COPY config /config
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["rsyslogd", "-f", "/config/rsyslog.conf", "-n"]

EXPOSE 5140/udp 5141/udp 5142/udp 5143/udp 5145/udp

ENV CUSTOMER_ID 00000
ENV ENABLE_LOG_DEBUG off
ENV ENABLE_LOG_FILES off
#ENV ENABLE_STATISTICS on
ENV HEC_HOST splunk-hf
ENV HEC_TOKEN ""
ENV TZ UTC
