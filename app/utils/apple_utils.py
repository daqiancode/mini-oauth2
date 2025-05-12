
import jwt
import time
from dotenv import load_dotenv
import os
from argparse import ArgumentParser
args = ArgumentParser(prog="apple_utils", description="Generate Apple Client Secret.",epilog="python app/utils/apple_utils.py -t team_id -c client_id -k key_id -p ./AuthKey_key_id.p8")
args.add_argument('-t', "--team_id", type=str, required=True)
args.add_argument('-c', "--client_id", type=str, required=True)
args.add_argument('-k', "--key_id", type=str, required=True)
args.add_argument('-p', "--private_key_path", type=str, required=True)
# add help

load_dotenv()

def generate_apple_client_secret(args):
    team_id = args.team_id
    client_id = args.client_id
    key_id = args.key_id
    private_key_path = args.private_key_path

    with open(private_key_path, "r") as f:
        private_key = f.read()

    headers = {
        "alg": "ES256",
        "kid": key_id,
    }

    payload = {
        "iss": team_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 180,
        "aud": "https://appleid.apple.com",
        "sub": client_id,
    }

    client_secret = jwt.encode(
        payload, private_key, algorithm="ES256", headers=headers
    )

    return client_secret

if __name__ == "__main__":
    args = args.parse_args()
    if args.help:
        print("python app/utils/apple_utils.py -t team_id -c client_id -k key_id -p ./AuthKey_key_id.p8")
    else:
        print(generate_apple_client_secret(args))
