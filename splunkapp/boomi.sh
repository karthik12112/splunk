#!/bin/bash
wget https://new-mounika.s3.amazonaws.com/splunkforwarder-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm
sudo yum install splunkforwarder-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm -y
vi /opt/splunkforwarder/etc/system/local/inputs.conf
[monitor:///opt/Boomi_AtomSphere/Atom/Atom_mounikaAWS/execution/history/*/execution-*/process_log.xml]
host=kk
sourcetype=karthik
time_before_close = 15
multiline_event_extra_waittime = true

vi /opt/splunkforwarder/etc/system/local/user-seed.conf
[user_info]
USERNAME = splunkadmin
PASSWORD = !QSYk68bI^$P2hXV^c2H7s(B
/opt/splunkforwarder/bin/splunk start --answer-yes --no-prompt --accept-license
/opt/splunkforwarder/bin/splunk add forward-server 18.237.49.246:9997
/opt/splunkforwarder/bin/splunk add monitor /var/log/cloud-init-output.log -sourcetype linux_secure



/opt/splunkforwarder/bin/splunk restart
