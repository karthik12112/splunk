#!/bin/bash
wget https://new-mounika.s3.amazonaws.com/splunkforwarder-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm
sudo yum install splunkforwarder-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm -y
vi /opt/splunkforwarder/etc/system/local/inputs.conf
[monitor:///opt/Boomi_AtomSphere/Atom/Atom_mounikaAWS/execution/history/*/execution-*/process_log.xml]
host=mounika
sourcetype=log4net_xml
/opt/splunkforwarder/bin/splunk start --answer-yes --no-prompt --accept-license
/opt/splunkforwarder/bin/splunk add forward-server 52.27.156.126:9997
/opt/splunkforwarder/bin/splunk add monitor /var/log/cloud-init-output.log -sourcetype linux_secure
