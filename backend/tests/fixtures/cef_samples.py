VALID_CEF_BRUTE_FORCE = (
    "CEF:0|ArcSight|Logger|7.2.0|authentication:100|Authentication Failure|7|"
    "src=185.220.101.47 dst=10.0.0.5 spt=45123 dpt=22 suser=root"
)

VALID_CEF_PORT_SCAN = (
    "CEF:0|Cisco|IDS|8.1|port_scan|Port Scan Detected|8|"
    "src=45.134.144.141 dst=10.0.0.1 dpt=22"
)

VALID_CEF_MALWARE = (
    "CEF:0|Symantec|AV|15.0|malware|Malware Detected|10|"
    "src=10.0.0.50 shost=workstation-001.corp.local sproc=explorer.exe msg=Trojan.GenericKD"
)

INVALID_CEF_TOO_FEW_PIPES = "CEF:0|ArcSight|Logger"
