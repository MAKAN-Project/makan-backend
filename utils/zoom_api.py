import requests
import base64
from django.conf import settings

def get_zoom_access_token():
    """Get a temporary access token from Zoom using Server-to-Server OAuth"""
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={settings.ZOOM_ACCOUNT_ID}"
    auth_header = base64.b64encode(f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}".encode()).decode()

    response = requests.post(url, headers={
        "Authorization": f"Basic {auth_header}"
    })

    if response.status_code != 200:
        print("❌ Zoom Token Error:", response.text)
        return None

    data = response.json()
    return data.get("access_token")


def create_zoom_meeting(topic, start_time, duration, agenda=None):
    """Create a Zoom meeting and return join/start links"""
    token = get_zoom_access_token()
    if not token:
        print("⚠️ Could not get Zoom token.")
        return None

    url = f"{settings.ZOOM_BASE_URL}/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "topic": topic,
        "type": 2,  # scheduled meeting
        "start_time": start_time.isoformat() if start_time else None,
        "duration": duration,
        "agenda": agenda,
        "timezone": "Asia/Gaza",
        "settings": {
            "join_before_host": False,
            "waiting_room": True,
            "approval_type": 0
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        meeting_data = response.json()
        print("✅ Zoom Meeting Created:", meeting_data.get("join_url"))
        return meeting_data
    else:
        print("❌ Zoom Meeting Error:", response.status_code, response.text)
        return None
