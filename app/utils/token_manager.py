import os
import jwt
import time
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))
TOKEN_EXPIRY_MINUTES = int(os.getenv('TOKEN_EXPIRY_MINUTES')) * 60

async def encode(payload):  # Receive account_id, permissions list, dealer_id, and returns encoded_token for it
    payload['generated_at'] = time.time()
    payload['expiry'] = time.time() + TOKEN_EXPIRY_MINUTES   
    token = jwt.encode(payload, key=KEY, algorithm=ALGORITHM)
    return token
    
async def decode(token: str): # Receive a token and return a dictionary with decoded token or raise a exception for invalid tokens
    try:
        decoded_token = jwt.decode(token, key=KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid Token")
    if (decoded_token['expiry'] - time.time()) < 1:
        raise HTTPException(status_code=401, detail="Unauthorized - Token Expired")
    else:
        return decoded_token
    
async def validate(token: str):  # Raise exception with some message if the token is not valid or return True for valid tokens
    try:
        try:
            decoded_token = jwt.decode(token, key=KEY, algorithms=[ALGORITHM])
        except Exception as e:
            raise Exception("Unauthorized - Invalid Token")
        if (decoded_token['expiry'] - time.time()) < 1:
            raise Exception("Unauthorized - Token expired")
        else:
            return decoded_token
    except Exception as e:
        raise Exception(str(e))