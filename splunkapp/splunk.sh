wget https://new-mounika.s3.amazonaws.com/splunk-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm
sudo yum install splunk-8.1.2-545206cc9f70-linux-2.6-x86_64.rpm -y
/opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --seed-passwd Administrator



/opt/splunk/bin/splunk restart
vi /opt/splunk/etc/apps/search/local/props.conf

[karthik]
BREAK_ONLY_BEFORE = <ExecutionLogModel>
MAX_EVENTS = 10000
