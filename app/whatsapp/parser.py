from typing import Any

from app.models.domain import WhatsAppInboundMessage

SUPPORTED_MESSAGE_TYPES = {"text"}


def parse_inbound_messages(payload: dict[str, Any]) -> list[WhatsAppInboundMessage]:
    messages: list[WhatsAppInboundMessage] = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts_by_wa_id = {
                contact.get("wa_id"): contact.get("profile", {}).get("name")
                for contact in value.get("contacts", [])
            }
            phone_number_id = value.get("metadata", {}).get("phone_number_id")

            for message in value.get("messages", []):
                message_type = message.get("type")
                if message_type not in SUPPORTED_MESSAGE_TYPES:
                    continue

                from_phone = message.get("from")
                message_id = message.get("id")
                text = message.get("text", {}).get("body")
                if not from_phone or not message_id or text is None:
                    continue

                messages.append(
                    WhatsAppInboundMessage(
                        message_id=message_id,
                        from_phone=from_phone,
                        text=text,
                        timestamp=message.get("timestamp"),
                        profile_name=contacts_by_wa_id.get(from_phone),
                        phone_number_id=phone_number_id,
                        raw=message,
                    )
                )

    return messages
