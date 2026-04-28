export type AlertFormat = 'cef' | 'syslog_3164' | 'syslog_5424' | 'json'
export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface GeoInfo {
  country_code: string
  country_name: string
  city: string | null
  asn: string | null
  is_known_vpn: boolean
}

export interface ThreatIntelInfo {
  reputation_score: number
  is_known_bad: boolean
  categories: string[]
  source: string
}

export interface AssetInfo {
  hostname: string
  tier: 'CROWN_JEWEL' | 'STANDARD' | 'LOW' | 'UNKNOWN'
  owner_team: string | null
  os: string | null
}

export interface NormalizedEvent {
  id: string
  timestamp: string
  source_format: AlertFormat
  severity: AlertSeverity
  event_type: string
  source_ip: string | null
  dest_ip: string | null
  source_host: string | null
  dest_host: string | null
  src_port: number | null
  dest_port: number | null
  username: string | null
  process_name: string | null
  message: string
  raw_fields: Record<string, unknown>
  geo: GeoInfo | null
  threat_intel: ThreatIntelInfo | null
  asset: AssetInfo | null
  ingested_at: string
}

export interface RawAlertIn {
  raw: string
  format_hint?: AlertFormat
}
