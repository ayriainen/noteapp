"""
A secret key used by the app. I preferred a randomly generated one over specific.
"""
import secrets
secret_key = secrets.token_hex(32)
