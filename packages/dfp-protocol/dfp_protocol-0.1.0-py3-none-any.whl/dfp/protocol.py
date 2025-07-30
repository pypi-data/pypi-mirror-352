def encode_message(flag: str, data: str) -> bytes:
    message = f"{flag}|{data}"
    return message.encode("utf-8")

def decode_message(data: bytes) -> tuple[str, str]:
    decoded = data.decode("utf-8")
    flag, payload = decoded.split("|", 1)
    return flag, payload
