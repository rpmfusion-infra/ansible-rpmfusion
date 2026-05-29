#! /bin/sh -e

for host in $(ansible maintainer_test --list-host | tail -n +2); do

echo " ======== Host: $host ========"

ssh "$host" dnf --refresh -y up

if [ "$(ssh $host who | wc -l)" = "1" ]; then
  ansible -m reboot "$host"
  ssh "$host" rkhunter --propupd
else
  echo " ** Skipping reboot as Users on: $host"
fi

done
