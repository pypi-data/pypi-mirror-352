import datetime
from dateutil.parser import isoparse
import base64
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import logging

def verify_trivium_callback_request(
    signature_from_header: str,
    raw_webhook_request_body: str,
    timestamp_from_header: str,
    public_key_base64_encoded: str,
    validity_period_seconds: int = 10 * 60, # accept timestamps within ten minutes of server time by default
    now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
) -> bool:
    """Verify the signature of a webhook request from Trivium.

    :param signature_from_header (str): Comma-separated signatures to enable zero-downtime key rotation. Retrieve from HTTP header: "Trivium-Signature".
    :param raw_webhook_request_body (str): The raw body of the webhook request, decoded as a UTF-8 string.
    :param timestamp_from_header (str): Retrieve from HTTP header: "Trivium-Timestamp".
    :param public_key_base64_encoded (str): Retrieve upon event subscription from Trivium API, for e.g. UserApi.post_api_v1_user_events() or CashApi.post_api_v1_cash_events().
    :param validity_period_seconds (int, optional): Defines window in which timestamp is valid to prevent replay attacks. Recommended value: 600 seconds (10 minutes).
    :param now (datetime, optional): Current time (with timezone set).

    :return: True if the signature is valid, False otherwise.
    """

    public_key_stripped = public_key_base64_encoded.replace("\n", "")
    public_key_lines = [public_key_stripped[i:i + 64] for i in range(0, len(public_key_stripped), 64)]
    public_key_pem = "-----BEGIN PUBLIC KEY-----\n" + "\n".join(public_key_lines) + "\n-----END PUBLIC KEY-----"

    is_valid = False
    message = f"{timestamp_from_header}|{raw_webhook_request_body}"
    digest = hashlib.sha256(message.encode("utf-8")).digest()
    for signature in signature_from_header.strip().split(","):
        try:
            public_key = serialization.load_pem_public_key(
                data=public_key_pem.encode("utf-8"),
                backend=default_backend()
            )
            public_key.verify(
                signature=base64.b64decode(signature),
                data=digest,
                padding=PKCS1v15(),
                algorithm=hashes.SHA256()
            )
            is_valid = True
            break
        except InvalidSignature:
            logging.warning(f"Invalid signature: {signature[:10]}... for Trivium callback content: {message}")
            continue
        except Exception as e:
            logging.warning(f"An error occurred while verifying Trivium signature: {e}")
            continue

    if is_valid and now > isoparse(timestamp_from_header) + datetime.timedelta(seconds=validity_period_seconds):
        return False
    else:
        return is_valid