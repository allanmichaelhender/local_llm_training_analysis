import os
from datetime import datetime, timedelta, timezone
from twilio.rest import Client


class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.to_number = os.getenv("USER_PHONE_NUMBER")
        self.client = None

    def _get_client(self):
        if not self.client:
            self.client = Client(self.account_sid, self.auth_token)
        return self.client

    def send_activity_prompt(self, activity: dict):
        message = (
            f"New workout detected!\n\n"
            f"Type: {activity['type']}\n"
            f"Duration: {activity['duration_minutes']:.1f} min\n"
            f"Avg HR: {activity['avg_hr']} bpm\n\n"
            f"Reply with: RPE (1-10) and any notes"
        )
        return self._send_message(message)

    def send_summary(self, summary: str):
        message = f"Workout Summary:\n\n{summary}"
        return self._send_message(message)

    def _send_message(self, body: str):
        try:
            client = self._get_client()
            message = client.messages.create(
                from_=self.from_number, body=body, to=self.to_number
            )
            print(f"WhatsApp sent: {message.sid}")
            return message.sid
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return None

    def get_unread_messages(self, after_sid: str = None):
        # For simplicity, we'll use a polling approach
        # In production, use Twilio webhooks
        try:
            client = self._get_client()
            messages = client.messages.list(to=self.from_number, limit=10)
            # Return all messages (both inbound and outbound)
            # Filtering is done in orchestrator based on SID tracking
            all_messages = [
                {
                    "sid": msg.sid,
                    "body": msg.body,
                    "from": msg.from_,
                    "date_sent": msg.date_sent,
                    "direction": msg.direction,
                }
                for msg in messages
            ]

            # If after_sid is provided, only return messages newer than that SID
            # Twilio message SIDs are roughly chronological
            if after_sid:
                try:
                    after_index = next(
                        i
                        for i, msg in enumerate(all_messages)
                        if msg["sid"] == after_sid
                    )
                    return all_messages[after_index + 1 :]
                except StopIteration:
                    # after_sid not found, return all
                    return all_messages

            return all_messages
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
