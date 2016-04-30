#!/bin/bash

RSYNC_FLAGS='-az --no-motd'

function syncHttpLogs {

    # in case we missed a run or two.. try to catch up the last 3 days.
    for d in 1 2 3
    do
        HOST=$1
	# some machines store stuff in old format. some new.
        if [ "$2" = "old" ]; then
            YESTERDAY=$(/bin/date -d "-$d days" +%Y-%m-%d)
        else
            YESTERDAY=$(/bin/date -d "-$d days" +%Y%m%d)
        fi
        YEAR=$(/bin/date -d "-$d days" +%Y)
        MONTH=$(/bin/date -d "-$d days" +%m)
        DAY=$(/bin/date -d "-$d days" +%d)
        /bin/mkdir -p /var/log/hosts/$HOST/$YEAR/$MONTH/$DAY/http
        cd /var/log/hosts/$HOST/$YEAR/$MONTH/$DAY/http/

        for f in $(/usr/bin/rsync $RSYNC_FLAGS --list-only $HOST::log/httpd/*$YESTERDAY* | awk '{ print $5 }')
        do
            DEST=$(echo $f | /bin/sed s/-$YESTERDAY//)
            /usr/bin/rsync $RSYNC_FLAGS $HOST::log/httpd/$f ./$DEST
        done
    done
}

syncHttpLogs koji01.rpmfusion.org
syncHttpLogs pkgs01.rpmfusion.org
## eof
