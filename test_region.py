"""Test script for region zoom."""
import json
import base64
import re
import urllib.request

def test_region(region):
    url = f"http://localhost:8000/game/start?difficulty=beginner&region={region}"
    req = urllib.request.Request(url, method='POST')
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))

    svg = base64.b64decode(data['map_image']).decode('utf-8')

    # Find path coordinates
    paths = re.findall(r'd="M ([\d\.\-]+) ([\d\.\-]+)', svg)

    print(f"\n=== {region.upper()} ===")
    print(f"Total paths: {len(paths)}")
    if paths:
        # Get first few x,y coordinates
        for i, (x, y) in enumerate(paths[:5]):
            print(f"  Path {i+1}: x={x}, y={y}")

        # Find coordinate ranges
        xs = [float(p[0]) for p in paths]
        ys = [float(p[1]) for p in paths]
        print(f"X range: {min(xs):.1f} - {max(xs):.1f}")
        print(f"Y range: {min(ys):.1f} - {max(ys):.1f}")

if __name__ == "__main__":
    test_region("world")
    test_region("europe")
