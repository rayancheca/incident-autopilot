VALID_SYSLOG_3164_AUTH = (
    "<34>Apr 28 10:15:33 dc01.corp.local sshd[1234]: "
    "Failed password for root from 185.220.101.47 port 52234 ssh2"
)

VALID_SYSLOG_3164_SUDO = (
    "<85>Apr 28 11:00:01 workstation-001.corp.local sudo[5678]: "
    "jdoe : TTY=pts/0 ; PWD=/home/jdoe ; USER=root ; COMMAND=/bin/bash"
)

VALID_SYSLOG_5424_FIREWALL = (
    "<165>1 2024-04-28T10:15:33.456Z firewall01 iptables 2345 BLOCK "
    '[fw@1234 action="DROP" src="194.165.16.11" dst="10.0.0.1" dpt="443"] '
    "Blocked inbound connection"
)
