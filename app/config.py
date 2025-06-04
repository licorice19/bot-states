from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN", "default_token")
ADMIN_ID = os.getenv("ADMIN_ID", "default_admin")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")



