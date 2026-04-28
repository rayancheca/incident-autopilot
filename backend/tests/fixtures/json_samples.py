import json

C2_BEACON = json.dumps({
    "event_type": "c2_beacon",
    "severity": "critical",
    "timestamp": "2024-04-28T10:00:00Z",
    "src_ip": "194.165.16.11",
    "dst_ip": "10.0.0.100",
    "src_host": "db-prod-01.corp.local",
    "message": "Suspicious outbound beacon to known C2 server",
    "username": "postgres",
})

DATA_EXFIL = json.dumps({
    "event_type": "data_exfiltration",
    "severity": "high",
    "timestamp": "2024-04-28T10:05:00Z",
    "src_ip": "10.0.0.100",
    "dst_ip": "185.220.101.47",
    "message": "Large data transfer to external IP",
    "bytes_transferred": 524288000,
})

LATERAL_MOVEMENT = json.dumps({
    "event_type": "lateral_movement",
    "level": "high",
    "ts": "2024-04-28T10:10:00Z",
    "src_host": "workstation-001.corp.local",
    "dst_host": "dc01.corp.local",
    "message": "SMB lateral movement attempt detected",
    "username": "jdoe",
})

INVALID_JSON = '{"incomplete": true'
