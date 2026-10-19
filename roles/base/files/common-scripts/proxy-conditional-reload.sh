#!/bin/bash
# reload SERVICE only if PACKAGE is installed.
# We use this throughout handlers/restart_services.yml
HOST=$(hostname -s)
SERVICE=$1
PACKAGE=$2

rpm -q $PACKAGE

INSTALLED=$?

if [[ ! -f "/etc/httpd/ticketkey.tkey" && "$HOST" =~ "^proxy" ]]; then
    # This host is not configured yet and not proxy host, do not try and restart httpd
    exit 0
fi

if [ $INSTALLED -eq 0 ]; then
    echo "Package $PACKAGE installed.  Attempting reload of $SERVICE."
    /sbin/service $SERVICE reload
    exit $?  # Exit with the /sbin/service status code
fi

# If the package wasn't installed, then pretend everything is fine.
echo "Package $PACKAGE not installed.  Skipping reload of $SERVICE."
exit 0
