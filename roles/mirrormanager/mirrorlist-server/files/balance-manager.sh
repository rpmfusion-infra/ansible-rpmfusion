#!/bin/bash

CURL=`which curl`
if [ -z "$CURL" ]; then
  echo "curl not found"
  exit 1
fi

server="localhost"
port="80"
manager="balancer-manager"

while getopts "s:p:m:" opt; do
  case "$opt" in
    s)
      server=$OPTARG
      ;;
    p)
      port=$OPTARG
      ;;
    m)
      manager=$OPTARG
      ;;
  esac
done

shift $(($OPTIND - 1))
action=$1


list_balancers() {
  $CURL -s "http://${server}:${port}/${manager}" | grep "balancer://" | sed "s/.*balancer:\/\/\(.*\)<\/a>.*/\1/"
}

list_workers() {
  balancer=$1
  if [ -z "$balancer" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  list-workers  balancer_name"
    echo "  balancer_name :    balancer name"
    exit 1
  fi
  $CURL -s "http://${server}:${port}/${manager}" | grep "/balancer-manager?b=${balancer}&amp;w" | sed "s/.*href='\(.[^']*\).*/\1/" | sed "s/.*w=\(.*\)&.*/\1/"
}

enable() {
  balancer=$1
  worker=$2
  if [ -z "$balancer" ] || [ -z "$worker" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  enable  balancer_name  worker_route"
    echo "  balancer_name :    balancer/cluster name"
    echo "  worker_route  :    worker route e.g.) ajp://192.1.2.3:8009"
    exit 1
  fi

  nonce=`$CURL -s "http://${server}:${port}/${manager}" | grep nonce | grep "${balancer}" | sed "s/.*nonce=\(.*\)['\"].*/\1/" | tail -n 1`
  if [ -z "$nonce" ]; then
    echo "balancer_name ($balancer) not found"
    exit 1
  fi

  echo "Enabling $2 of $1..."
  $CURL -s -o /dev/null -XPOST "http://${server}:${port}/${manager}?" -d b="${balancer}" -d w="${worker}" -d nonce="${nonce}" -d w_status_D=0 -H "Referer: http://${server}:${port}/${manager}?"
  sleep 2
  status
}

disable() {
  balancer=$1
  worker=$2
  if [ -z "$balancer" ] || [ -z "$worker" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  disable  balancer_name  worker_route"
    echo "  balancer_name :    balancer/cluster name"
    echo "  worker_route  :    worker route e.g.) ajp://192.1.2.3:8009"
    exit 1
  fi

  echo "Disabling $2 of $1..."
  nonce=`$CURL -s "http://${server}:${port}/${manager}" | grep nonce | grep "${balancer}" | sed "s/.*nonce=\(.*\)['\"].*/\1/" | tail -n 1`
  if [ -z "$nonce" ]; then
    echo "balancer_name ($balancer) not found"
    exit 1
  fi

  $CURL -s -o /dev/null -XPOST "http://${server}:${port}/${manager}?" -d b="${balancer}" -d w="${worker}" -d nonce="${nonce}" -d w_status_D=1 -H "Referer: http://${server}:${port}/${manager}?"
  sleep 2
  status
}

status() {
  $CURL -s "http://${server}:${port}/${manager}" | grep "href" | sed "s/<[^>]*>/ /g"
}

case "$1" in
  list-balancer)
    list_balancers "${@:2}"
	;;
  list-worker)
    list_workers "${@:2}"
	;;
  enable)
    enable "${@:2}"
	;;
  disable)
    disable "${@:2}"
	;;
  status)
    status "${@:2}"
	;;
  *)
    echo "Usage: $0 {list-balancer|list-worker|enable|disable|status}"
	echo ""
	echo "Options: "
	echo "    -s server"
	echo "    -p port"
	echo "    -m balancer-manager-context-path"
	echo ""
	echo "Commands: "
	echo "    list-balancer"
	echo "    list-worker  balancer-name"
	echo "    enable   balancer_name  worker_route"
	echo "    disable  balancer_name  worker_route"
    exit 1
esac

exit $?
