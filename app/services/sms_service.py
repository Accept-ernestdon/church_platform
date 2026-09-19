import os
import requests


class SMSService:
    """
    ChurchConnect SMS service using Arkesel.
    """

    API_URL = "https://sms.arkesel.com/api/v2/sms/send"

    @staticmethod
    def send_sms(phone_number, message):
        """
        Send one SMS through Arkesel.
        """

        api_key = os.getenv("ARKESEL_API_KEY")
        sender_id = os.getenv("ARKESEL_SENDER_ID")

        if not api_key:
            print("ERROR: ARKESEL_API_KEY is not configured.")
            return False

        if not sender_id:
            print("ERROR: ARKESEL_SENDER_ID is not configured.")
            return False

        payload = {
            "sender": sender_id,
            "message": message,
            "recipients": [phone_number],
        }

        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                SMSService.API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )

            print("=" * 60)
            print("CHURCHCONNECT REAL SMS")
            print(f"To: {phone_number}")
            print(f"Sender: {sender_id}")
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text}")
            print("=" * 60)

            if response.ok:
                return True

            return False

        except requests.RequestException as error:
            print("=" * 60)
            print("CHURCHCONNECT SMS ERROR")
            print(error)
            print("=" * 60)

            return False