import firebase_admin
from firebase_admin import credentials, messaging
import os


def init_firebase(cert_path='firebase_key.json'):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)


def send_notification_to_token(token, title, body, data=None):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )
    try:
        resp = messaging.send(message)
        return resp
    except Exception as e:
        print(f"Error sending message: {e}")
        return None


def send_multicast(tokens, title, body, data=None):
    # tokens: list of device registration tokens
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens,
        data=data or {}
    )
    try:
        resp = messaging.send_multicast(message)
        return resp
    except Exception as e:
        print(f"Error sending multicast: {e}")
        return None


def send_to_topic(topic, title, body, data=None):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            topic=topic,
            data=data or {}
        )
        resp = messaging.send(message)
        return resp
    except Exception as e:
        print(f"Error sending to topic {topic}: {e}")
        return None


if __name__ == '__main__':
    # Example usage
    if not os.path.exists('firebase_key.json'):
        print('firebase_key.json not found. Place your service account file in project root to use notifications.')
    else:
        init_firebase()
        print('Firebase messaging ready. Use send_notification_to_token() with device tokens.')
