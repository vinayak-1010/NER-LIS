"""
scripts/gps_sim.py — GPS simulation script.

Replays a vehicle moving along the pilot corridor (Guwahati → Shillong)
by POSTing position updates to the backend API every N seconds.

Usage:
    python scripts/gps_sim.py --vehicle-id <uuid> --api-url http://localhost:8000
"""

import argparse
import time
import json
import sys
import math
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# Pilot corridor waypoints (lat, lng) along Guwahati → Shillong
# ---------------------------------------------------------------------------
CORRIDOR_WAYPOINTS = [
    (26.1445, 91.7362),  # Guwahati start
    (26.1380, 91.7500),
    (26.1290, 91.7750),
    (26.1200, 91.7990),  # Jorabat Junction start
    (26.0950, 91.8200),
    (26.0700, 91.8400),  # Jorabat end / Barapani start
    (26.0400, 91.8620),
    (26.0100, 91.8890),
    (25.9800, 91.9050),  # Nongpoh
    (25.9600, 91.9200),
    (25.9350, 91.9380),  # Umiam Lake
    (25.9100, 91.9500),
    (25.8900, 91.9620),
    (25.8750, 91.9700),  # Shillong Bypass (blocked)
    (25.8620, 91.9780),
    (25.8500, 91.9820),
    (25.5780, 91.9880),  # Shillong city
]


def interpolate_points(waypoints: list, steps_between: int = 3) -> list:
    """Add intermediate points between waypoints for smoother movement."""
    result = []
    for i in range(len(waypoints) - 1):
        lat1, lng1 = waypoints[i]
        lat2, lng2 = waypoints[i + 1]
        for s in range(steps_between):
            t = s / steps_between
            result.append((
                lat1 + t * (lat2 - lat1),
                lng1 + t * (lng2 - lng1),
            ))
    result.append(waypoints[-1])
    return result


def post_position(api_url: str, vehicle_id: str, lat: float, lng: float, token: str = None):
    url = f"{api_url}/api/v1/vehicles/{vehicle_id}/position"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = {"latitude": lat, "longitude": lng}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        return r.status_code == 200
    except requests.RequestException as e:
        print(f"  ⚠️  POST failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="NER-LIS GPS Simulator")
    parser.add_argument("--vehicle-id", required=True, help="UUID of the vehicle to simulate")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Backend API base URL")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between updates")
    parser.add_argument("--token", default=None, help="JWT Bearer token (optional)")
    parser.add_argument("--loop", action="store_true", help="Loop the route continuously")
    args = parser.parse_args()

    points = interpolate_points(CORRIDOR_WAYPOINTS, steps_between=4)
    total = len(points)

    print(f"🚛 NER-LIS GPS Simulator")
    print(f"   Vehicle : {args.vehicle_id}")
    print(f"   Route   : Guwahati → Shillong ({total} waypoints)")
    print(f"   Interval: {args.interval}s")
    print(f"   API     : {args.api_url}")
    print()

    run = True
    while run:
        for i, (lat, lng) in enumerate(points):
            ok = post_position(args.api_url, args.vehicle_id, lat, lng, args.token)
            status = "✅" if ok else "❌"
            print(f"  {status} [{i+1:03d}/{total}] lat={lat:.5f}  lng={lng:.5f}  {datetime.utcnow().strftime('%H:%M:%S')}")
            time.sleep(args.interval)

        if not args.loop:
            run = False
        else:
            print("\n🔁 Route complete. Restarting...\n")

    print("\n✅ Simulation finished.")


if __name__ == "__main__":
    main()
