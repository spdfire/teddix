#
# Regular cron jobs for the teddix package
#
0 4	* * *	root	[ -x /usr/bin/teddix_maintenance ] && /usr/bin/teddix_maintenance
