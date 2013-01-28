#!/bin/sh
#
#For grandcloud hosts without public ip
#
# Passive Host Check Test Script
#
CMD="/usr/sbin/send_nsca"
CFG="/etc/nagios/send_nsca.cfg"
SERVER="nagios.bposervers.com"
DIR="/usr/lib64/nagios/plugins"
#CMD="gc-mob02;0;Host Status"

#/bin/echo $CMD | /usr/sbin/send_nsca -H nagios.bposervers.com -d ';' -c $CFG
#CMD="gc-mob02;0;LOAD"
#/bin/echo $CMD | /usr/sbin/send_nsca -H nagios.bposervers.com -d ';' -c $CFG
host_name="gc-mob02"
svc_name=$1

Load_ARG="-w 5 -c 10"

rm -f /tmp/nsca.out

check() {

case "$1" in
load)
  output=`$DIR/check_load $Load_ARG`
  status=`echo $?`
  echo $output
  echo "$host_name	LOAD	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

sda2)
  output=`$DIR/check_disk -w 20% -c 10% -p /dev/xvda2`
  status=`echo $?`
  echo $output
  echo "$host_name	DISK sda2	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

sda3)
  output=`$DIR/check_disk -w 20% -c 10% -p /dev/xvda3`
  status=`echo $?`
  echo $output
  echo "$host_name	DISK sda3	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

ssh)
  output=`$DIR/check_ssh -H 127.0.0.1`
  status=`echo $?`
  echo $output
  echo "$host_name	SSH	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

swap)
  output=`$DIR/check_swap -w 30 -c 20`
  status=`echo $?`
  echo $output
  echo "$host_name	SWAP	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

process)
  output=`$DIR/check_procs -w 150 -c 200`
  status=`echo $?`
  echo $output
  echo "$host_name	TOTAL PROCESSES	$status	$output">/tmp/nsca.out
  $CMD -H $SERVER -c $CFG </tmp/nsca.out
  ;;

*)
  echo "$0: load|sda2|sda3|ssh|swap|process"
  ;;
 
esac

}

check process
check swap
check ssh
check sda3
check sda2
check load
exit 0 
