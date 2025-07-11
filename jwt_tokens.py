import jwt
import random
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Generate public key from private key
    public_key = private_key.public_key()

    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_key,public_key,private_pem,public_pem

def convert_pems_to_objects(private_pem,public_pem):
    print(private_pem,public_pem,flush=True)
    private_key = serialization.load_pem_private_key(bytes(private_pem,"utf-8"), password=None, backend=default_backend())
    public_key = serialization.load_pem_public_key(bytes(public_pem,"utf-8"), backend=default_backend())
    return private_key,public_key

def encode(payload,key):
    encoded = jwt.encode(payload,key, algorithm="RS256")
    return encoded

def decode(encoded,key):
    decoded = jwt.decode(encoded,key, algorithms=["RS256"])
    return decoded