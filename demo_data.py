import time
from PIL import Image, ImageDraw, ImageFont


def _make_demo_image(name, size=(320,240), bgcolor=(30,144,255), text_color=(255,255,255)):
    img = Image.new('RGB', size, bgcolor)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except Exception:
        font = ImageFont.load_default()
    text = name
    w, h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill=text_color, font=font)
    return img


def get_demo_requests():
    """Return a list of demo pickup requests with in-memory images."""
    now = int(time.time())
    demo = [
        {
            'id': 'demo1',
            'user_name': 'Rajalakshmi',
            'location': 'Guindy Main Gate, Chennai',
            'disability_type': 'leg_disabled',
            'status': 'pending',
            'route': '570',
            'photo_url': _make_demo_image('Rajalakshmi'),
            'timestamp': now - 120
        },
        {
            'id': 'demo2',
            'user_name': 'Karthik',
            'location': 'Tambaram Gate 2',
            'disability_type': 'hand_disabled',
            'status': 'pending',
            'route': '21G',
            'photo_url': _make_demo_image('Karthik'),
            'timestamp': now - 600
        },
        {
            'id': 'demo3',
            'user_name': 'Meena',
            'location': 'Chromepet Bus Stop',
            'disability_type': 'blind',
            'status': 'resolved',
            'route': '45A',
            'photo_url': _make_demo_image('Meena'),
            'timestamp': now - 3600
        }
    ]
    return demo
