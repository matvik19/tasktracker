from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

DEFAULT_ENCODING = "utf-8"
HMAC_DIGEST_MODE = "sha256"
JWT_SIGN_ALGORITHM = "HS256"
TOKEN_SECRET_KEY = os.getenv("TOKEN_SECRET_KEY", "mysecretkey")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 12 * 60))

MAIL_PASSWORD_APP = os.environ.get("MAIL_PASSWORD_APP")
