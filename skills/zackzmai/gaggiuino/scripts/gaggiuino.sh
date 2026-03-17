#!/usr/bin/env bash
# Gaggiuino API wrapper script
# Usage: gaggiuino.sh <command> [args]
# Commands: status, profiles, latest-shot, shot <id>, select-profile <id>

set -euo pipefail

BASE_URL="${GAGGIUINO_BASE_URL:-http://gaggiuino.local}"
TIMEOUT=10

api_get() {
  curl -sf --max-time "$TIMEOUT" "${BASE_URL}$1" 2>/dev/null
}

api_post() {
  curl -sf --max-time "$TIMEOUT" -X POST "${BASE_URL}$1" 2>/dev/null
}

cmd_status() {
  local raw
  raw=$(api_get "/api/system/status") || { echo '{"error": "Cannot connect to Gaggiuino"}' ; exit 1; }
  echo "$raw" | python3 -c "
import sys, json
raw = json.load(sys.stdin)
s = raw[0] if isinstance(raw, list) else {}
result = {
    'online': True,
    'state': 'brewing' if s.get('brewSwitchState') == 'true' else ('steaming' if s.get('steamSwitchState') == 'true' else 'idle'),
    'temp': {'current': float(s.get('temperature', 0)), 'target': float(s.get('targetTemperature', 0))},
    'pressure': float(s.get('pressure', 0)),
    'weight': float(s.get('weight', 0)),
    'water': int(s.get('waterLevel', 0)),
    'profile': {'id': int(s.get('profileId', 0)), 'name': s.get('profileName', 'Unknown')}
}
print(json.dumps(result, ensure_ascii=False, indent=2))
"
}

cmd_profiles() {
  local raw
  raw=$(api_get "/api/profiles/all") || { echo '{"error": "Cannot fetch profiles"}' ; exit 1; }
  echo "$raw" | python3 -c "
import sys, json
profiles = json.load(sys.stdin)
result = []
for p in profiles:
    result.append({
        'id': p.get('id'),
        'name': p.get('name'),
        'selected': p.get('selected') == 'true'
    })
print(json.dumps(result, ensure_ascii=False, indent=2))
"
}

cmd_latest_shot() {
  local shot_id
  shot_id=$(api_get "/api/shots/latest" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r[0]['lastShotId'] if isinstance(r, list) else r.get('lastShotId', ''))" 2>/dev/null) \
    || { echo '{"error": "Cannot get latest shot ID"}' ; exit 1; }
  cmd_shot "$shot_id"
}

cmd_shot() {
  local id="${1:?Shot ID required}"
  if [[ ! "$id" =~ ^[0-9]+$ ]]; then echo '{"error": "Invalid shot ID"}'; exit 1; fi
  local raw
  raw=$(api_get "/api/shots/$id") || { echo '{"error": "Cannot get shot '$id'"}' ; exit 1; }
  echo "$raw" | python3 -c "
import sys, json
from datetime import datetime

d = json.load(sys.stdin)
dp = d.get('datapoints', {})
shot_id = d.get('id')
duration = d.get('duration', 0) / 10
ts = datetime.fromtimestamp(d.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')

prof = d.get('profile', {})
phases = []
if prof and 'phases' in prof:
    for p in prof['phases']:
        phases.append({
            'name': p.get('name'),
            'type': p.get('type'),
            'target': p.get('target'), # contains start, end, curve
            'duration': p.get('stopConditions', {}).get('time', 0) / 1000,
            'restriction': p.get('restriction') # Flow restriction
        })

# Downsample to 1Hz (Original data is usually 10Hz)
times = dp.get('timeInShot', [])
n = len(times)
if n > 0:
    # We pick indices where time is closest to 0.0, 1.0, 2.0...
    indices = []
    last_half_sec = -1
    for i, t in enumerate(times):
        # t is in deciseconds (1/10s). We want a sample every 5 deciseconds (0.5s).
        half_sec = int(t / 5)
        if half_sec > last_half_sec:
            indices.append(i)
            last_half_sec = half_sec
    
    downsampled = []
    for i in indices:
        downsampled.append({
            't': times[i]/10,
            'p': dp.get('pressure', [0]*n)[i]/10,
            'tp': dp.get('targetPressure', [0]*n)[i]/10,
            'f': dp.get('pumpFlow', [0]*n)[i]/10,
            'tf': dp.get('targetPumpFlow', [0]*n)[i]/10,
            'w': dp.get('shotWeight', [0]*n)[i]/10,
            'wf': dp.get('weightFlow', [0]*n)[i]/10,
            'temp': dp.get('temperature', [0]*n)[i]/10
        })

    result = {
        'shot_id': shot_id,
        'timestamp': ts,
        'duration': duration,
        'sampling': '2Hz',
        'profile': {
            'name': prof.get('name'),
            'temp': prof.get('waterTemperature'),
            'phases': phases
        },
        'stats': {
            'final_weight': dp.get('shotWeight', [0])[-1]/10 if dp.get('shotWeight') else 0,
            'total_water': dp.get('waterPumped', [0])[-1]/10 if dp.get('waterPumped') else 0,
            'max_flow': max(dp.get('pumpFlow', [0]))/10 if dp.get('pumpFlow') else 0
        },
        'data_2hz': downsampled
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
else:
    print(json.dumps({'error': 'No data points found for this shot'}, indent=2))
"
}

cmd_select_profile() {
  local id="${1:?Profile ID required}"
  if [[ ! "$id" =~ ^[0-9]+$ ]]; then echo '{"error": "Invalid profile ID"}'; exit 1; fi
  local raw
  raw=$(api_post "/api/profile-select/$id") || { echo '{"error": "Failed to select profile '$id'"}' ; exit 1; }
  echo '{"success": true, "profile_id": '$id'}'
}

cmd_get_settings() {
  local cat="${1:-}"
  local endpoint="/api/settings"
  if [[ -n "$cat" ]]; then endpoint="/api/settings/$cat"; fi
  local raw
  raw=$(api_get "$endpoint") || { echo '{"error": "Cannot fetch settings"}' ; exit 1; }
  echo "$raw" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=2))"
}

cmd_update_settings() {
  local cat="${1:?Category required (boiler|system|led|scales|display|theme)}"
  local payload="${2:?JSON payload required}"
  # Note: Gaggiuino requires all fields in the POST body.
  curl -sf --max-time "$TIMEOUT" -X POST -H "Content-Type: application/json" -d "$payload" "${BASE_URL}/api/settings/$cat" >/dev/null \
    || { echo '{"error": "Failed to update settings for '$cat'"}' ; exit 1; }
  echo '{"success": true, "category": "'$cat'"}'
}

# Main
case "${1:-help}" in
  status)          cmd_status ;;
  profiles)        cmd_profiles ;;
  latest-shot)     cmd_latest_shot ;;
  shot)            cmd_shot "${2:-}" ;;
  select-profile)  cmd_select_profile "${2:-}" ;;
  get-settings)    cmd_get_settings "${2:-}" ;;
  update-settings) cmd_update_settings "${2:-}" "${3:-}" ;;
  *)
    echo "Usage: $0 {status|profiles|latest-shot|shot <id>|select-profile <id>|get-settings [cat]|update-settings <cat> <json>}"
    exit 1
    ;;
esac
