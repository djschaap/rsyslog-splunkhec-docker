#!/bin/ash
set -e

if [ "$1" = "rsyslogd" ]; then
	shift

	if [ -n "$HEC_HOST" -a -n "$HEC_TOKEN" ] ; then
		cp /config/splunk-hec.src /config/splunk-hec.conf
		sed -i \
			-e "s/HEC_HOST/$HEC_HOST/" \
			-e "s/HEC_TOKEN/$HEC_TOKEN/" \
			/config/splunk-hec.conf
		export ENABLE_HEC=on
	else
		rm -f /config/splunk-hec.conf
		export ENABLE_HEC=off
	fi

	exec /usr/sbin/rsyslogd "$@"
fi

exec "$@"
