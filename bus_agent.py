import time
import random
import argparse
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime


def init_firebase(cert_path='firebase_key.json', database_url=None):
    if not database_url:
        database_url = 'https://smart-bus-7bb33-default-rtdb.firebaseio.com/'
    cred = credentials.Certificate(cert_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})


def push_location(bus_id, lat, lon, speed=0.0, route=None):
    ref = db.reference(f'buses/{bus_id}/location')
    ref.set({
        'lat': lat,
        'lon': lon,
        'speed': speed,
        'route': route,
        'timestamp': {'.sv': 'timestamp'}
    })


def simulate_route(bus_id, route, start, end, steps=10, delay=5):
    lat1, lon1 = start
    lat2, lon2 = end
    for i in range(steps + 1):
        t = i / max(1, steps)
        lat = lat1 + (lat2 - lat1) * t + random.uniform(-0.0001, 0.0001)
        lon = lon1 + (lon2 - lon1) * t + random.uniform(-0.0001, 0.0001)
        speed = random.uniform(20, 40)
        push_location(bus_id, lat, lon, speed=speed, route=route)
        print(f"[{datetime.now().isoformat()}] Pushed {bus_id} -> ({lat:.6f},{lon:.6f}) speed={speed:.1f}")
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description='Simulate a bus sending GPS to Firebase RTDB')
    parser.add_argument('--bus-id', default='TN-01-AN-1234')
    parser.add_argument('--route', default='570')
    parser.add_argument('--start-lat', type=float, default=13.0168)
    parser.add_argument('--start-lon', type=float, default=80.2066)
    parser.add_argument('--end-lat', type=float, default=13.0827)
    parser.add_argument('--end-lon', type=float, default=80.2707)
    parser.add_argument('--steps', type=int, default=20)
    parser.add_argument('--delay', type=float, default=5.0)
    args = parser.parse_args()

    init_firebase()
    print('Starting bus agent simulator...')
    simulate_route(args.bus_id, args.route, (args.start_lat, args.start_lon), (args.end_lat, args.end_lon), steps=args.steps, delay=args.delay)


if __name__ == '__main__':
    main()
