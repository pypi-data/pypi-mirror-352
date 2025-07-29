import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.db import connection
import os
import json
import secrets
import string
from core.settings.base import WORKFLOW_ENCRYPTION_KEY


class KeyAlgorithm:
    RSA = "rsa"


def generate_random_string(length=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_fernet():
    # Ensure WORKFLOW_ENCRYPTION_KEY is base64-encoded and 32 bytes
    key = WORKFLOW_ENCRYPTION_KEY
    if isinstance(key, str):
        key = key.encode()
    # If not already base64, encode it
    if len(key) != 44:  # 32 bytes base64-encoded = 44 chars
        key = base64.urlsafe_b64encode(key.ljust(32, b'0')[:32])
    return Fernet(key)


def write_encrypted_json(path, data):
    f = get_fernet()
    enc = f.encrypt(json.dumps(data).encode())
    with open(path, "wb") as out:
        out.write(enc)


def read_encrypted_json(path):
    f = get_fernet()
    with open(path, "rb") as inp:
        enc = inp.read()
    dec = f.decrypt(enc)
    return json.loads(dec.decode())


def get_external_project_id(user):
    return user.active_organization.id.__str__()


def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )

    return {
        "privateKey": private_pem.decode(),
        "publicKey": public_pem.decode(),
        "algorithm": KeyAlgorithm.RSA,
    }


def get_platform_id():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM platform LIMIT 1")
        row = cursor.fetchone()

    return row[0] if row else None


def get_key():
    cfg_path = "workflow.cfg"
    key_data = None

    if os.path.exists(cfg_path):
        try:
            key_data = read_encrypted_json(cfg_path)

            # Check if id exists in signing_key table
            with connection.cursor() as cursor:
                cursor.execute('SELECT id FROM signing_key WHERE id = %s', [key_data["id"]])
                row = cursor.fetchone()

            if row:
                return {
                    "id": key_data["id"],
                    "privateKey": key_data["privateKey"],
                    "publicKey": key_data["publicKey"],
                }
        except Exception as e:
            print(e)

    # If file does not exist or id not found, create new key
    key = create_key()
    write_encrypted_json(cfg_path, key)
    return key


def create_key():
    platform_id = get_platform_id()

    if platform_id is None:
        raise Exception("No workflow platform found")

    key = generate_key()
    key_id = generate_random_string(21)

    with connection.cursor() as cursor:
        cursor.execute(
            'INSERT INTO signing_key (id, "platformId", "publicKey", algorithm, "displayName") VALUES (%s, %s, %s, %s, %s)',
            [key_id, platform_id, key["publicKey"], key["algorithm"].upper(), "Auto-generated from platform"]
        )

    return {
        "id": key_id,
        "publicKey": key["publicKey"],
        "privateKey": key["privateKey"],
    }
