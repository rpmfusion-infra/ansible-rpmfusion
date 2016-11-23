#!/bin/bash

CONFFILE=/etc/mailman-migration.conf

set -e 

export PATH=$PATH:$(dirname $(realpath $0)) # make yamlget available

BASEDIR=`yamlget basedir $CONFFILE`
CONFDIR=`yamlget confdir $CONFFILE`
INDEXDIR=$BASEDIR/fulltext_index

# Give database rights to the non-admin user (must be done before loading initial data)
sleep $[ ( $RANDOM % 10 )  + 1 ]s # avoid simultaneous lockups on parallel servers. Yes, this is dirty.
$BASEDIR/bin/pg-give-rights.py > /dev/null

echo "static files"
django-admin collectstatic --clear --noinput --verbosity 0 --pythonpath $CONFDIR --settings settings
django-admin compress --pythonpath $CONFDIR --settings settings
echo "db migration"
django-admin migrate --pythonpath $CONFDIR --settings settings_admin --noinput
echo "load initial data"
django-admin loaddata $CONFDIR/initial-data.json --pythonpath $CONFDIR --settings settings
mkdir -p $INDEXDIR
chown apache:apache -R $INDEXDIR

# SELinux contexts
echo "SELinux contexts"
restorecon -r "$BASEDIR"

# Run unit tests
echo "unit tests"
django-admin test --pythonpath $CONFDIR --settings settings_test hyperkitty postorius

# Reload Apache to flush the python cache
systemctl reload httpd

# Clean the cache
systemctl restart memcached
