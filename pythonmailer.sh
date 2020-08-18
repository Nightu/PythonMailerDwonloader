#!/bin/bash
### BEGIN INIT INFO
# Provides:          Python mailer daemon
# Required-Start:    python networking
# Required-Stop:     python
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start python mailer daemon
# Description:       Gives option to start, stop and restart daemon.
### END INIT INFO
NAME=mailerdaemonprocess
LOGFILE="/var/log/${NAME}.log"
DAEMON="python"
SCRIPT_PATH='/opt/mailer_daemon/MailerDaemonProcess.py'


case "$1" in
   start)
     $DAEMON $SCRIPT_PATH >> $LOGFILE 2>&1 &
     ;;
   stop)
     kill $(ps -aux | grep -i MailerDaemonProcess | awk 'NR==1{ print $2 }')
     ;;
   restart)
     echo "Restart daemon" >> $LOGFILE 2>&1 &
     kill $(ps -aux | grep -i MailerDaemonProcess | awk 'NR==1{ print $2 }')
     $DAEMON $SCRIPT_PATH >> $LOGFILE 2>&1 &
     echo "Daemon restarted successfully" >> $LOGFILE 2>&1 &
     ;;
esac

exit 0
