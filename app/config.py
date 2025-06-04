from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN", "default")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv("ADMIN_IDS", 'default').split(",") if admin_id.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")