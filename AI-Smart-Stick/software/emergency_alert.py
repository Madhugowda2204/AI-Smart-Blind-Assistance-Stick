
import os
from dotenv import load_dotenv
from twilio.rest import Client
from gps_module import get_current_location

load_dotenv()

def send_sms(location=None):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Twilio credentials are not configured.")
        return

    try:
        client = Client(account_sid, auth_token)

        if location is None:
            location = get_current_location()

        location_text = (
            f"{location[0]}, {location[1]}"
            if location else "Unavailable"
        )

        message = client.messages.create(
            body=f"🚨 Emergency! Location: {location_text}",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=os.getenv("EMERGENCY_PHONE_NUMBER")
        )

        print("✅ Alert Sent:", message.sid)

    except Exception as e:
        print("⚠️ Failed to send emergency SMS:", e)


if __name__ == "__main__":
    send_sms()
