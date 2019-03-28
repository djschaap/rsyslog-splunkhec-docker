#!/bin/ash
set -e

if [ "$1" = "rsyslogd" ]; then
	shift

	# copy rsyslog.conf for persistence
	#   (disabled; this persistence complicates image upgrades)
	#if [ ! -r /config/rsyslog.conf ] ; then
	#	cp /default/rsyslog.conf /config/rsyslog.conf
	#fi

	if [ "$CUSTOMER_ID" = "" ] ; then
		echo "FATAL: CUSTOMER_ID is blank/empty; aborting"
		exit 1
	elif [ "$CUSTOMER_ID" = "00000" ] ; then
		echo "WARNING: CUSTOMER_ID is 00000"
	fi

	if [ -n "$HEC_HOST" -a -n "$HEC_TOKEN" ] ; then
		cp /default/splunk-hec.conf /config/splunk-hec.conf
		sed -i \
			-e "s/HEC_HOST/$HEC_HOST/" \
			-e "s/HEC_TOKEN/$HEC_TOKEN/" \
			/config/splunk-hec.conf
		#export ENABLE_HEC=on
	else
		rm -f /config/splunk-hec.conf
		echo "WARNING: Splunk forwarding disabled; set HEC_HOST and HEC_TOKEN"
		#export ENABLE_HEC=off
	fi

	exec /usr/sbin/rsyslogd "$@"
fi

exec "$@"
