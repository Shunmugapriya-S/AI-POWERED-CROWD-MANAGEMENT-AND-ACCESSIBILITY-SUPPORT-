from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from firebase_manager import FirebaseManager

app = Flask(__name__)
CORS(app)

# Initialize Firebase manager (will run in offline mode if no key present)
fb = FirebaseManager()


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'ok': True, 'service': 'smart-bus-api'})


@app.route('/api/gps_update', methods=['POST'])
def gps_update():
    """Accept GPS updates from a bus agent. JSON: {bus_id, lat, lon, speed?, route?}"""
    try:
        payload = request.get_json(force=True)
        bus_id = payload.get('bus_id')
        lat = payload.get('lat')
        lon = payload.get('lon')
        speed = payload.get('speed', 0.0)
        route = payload.get('route')

        if not bus_id or lat is None or lon is None:
            return jsonify({'ok': False, 'error': 'Missing required fields: bus_id, lat, lon'}), 400

        # If Firebase is available, write GPS to RTDB
        if fb.initialized:
            from firebase_admin import db
            ref = db.reference(f'buses/{bus_id}/location')
            ref.set({
                'lat': float(lat),
                'lon': float(lon),
                'speed': float(speed),
                'route': route,
                'timestamp': {'.sv': 'timestamp'}
            })
            return jsonify({'ok': True, 'stored': True})

        # Otherwise just accept
        return jsonify({'ok': True, 'stored': False, 'note': 'Firebase not initialized'}), 202
    except Exception:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': 'Internal error'}), 500


@app.route('/api/crowd_update', methods=['POST'])
def crowd_update():
    """Accept crowd counts from detector. JSON: {bus_id, count, level, timestamp?}"""
    try:
        payload = request.get_json(force=True)
        bus_id = payload.get('bus_id')
        count = payload.get('count')
        level = payload.get('level')

        if not bus_id or count is None or not level:
            return jsonify({'ok': False, 'error': 'Missing required fields: bus_id, count, level'}), 400

        # Use FirebaseManager helper when possible
        if fb.initialized:
            ok = fb.update_crowd_status(bus_id, int(count), str(level))
            return jsonify({'ok': bool(ok)})

        return jsonify({'ok': True, 'stored': False, 'note': 'Firebase not initialized'}), 202
    except Exception:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': 'Internal error'}), 500


if __name__ == '__main__':
    # Run on 0.0.0.0 for local network access (bus agents on same LAN)
    app.run(host='0.0.0.0', port=5000, debug=True)
