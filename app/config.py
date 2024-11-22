import os
from dotenv import load_dotenv

load_dotenv("../.env")

class Config:
    # Gitea 配置
    GITEA_SECRET = os.getenv("GITEA_SECRET") 
    GITEA_AUTHORIZATION = os.getenv("GITEA_AUTHORIZATION") 
    
    # Lark 配置
    LARK_APP_ID = os.getenv("LARK_APP_ID")
    LARK_APP_SECRET = os.getenv("LARK_APP_SECRET")

    LARK_ENCRYPT_KEY = os.getenv("LARK_ENCRYPT_KEY")
    LARK_VERIFICATION_TOKEN = os.getenv("LARK_VERIFICATION_TOKEN")

    LARK_CHAT_ID = os.getenv("LARK_CHAT_ID")

    # 发送的卡片配置
    LARK_CARD_ID = os.getenv("LARK_CARD_ID")
    LARK_CARD_VERSION = os.getenv("LARK_CARD_VERSION")

    # 回调更新的卡片配置
    LARK_CALLBACK_CARD_ID = os.getenv("LARK_CALLBACK_CARD_ID")
    LARK_CALLBACK_CARD_VERSION = os.getenv("LARK_CALLBACK_CARD_VERSION")

    # redis 数据库配置
    IS_SINGLE = bool(os.getenv("IS_SINGLE"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    
    # 单节点
    SINGLE_REDIS_HOST = os.getenv("SINGLE_REDIS_HOST")
    SINGLE_REDIS_PORT = os.getenv("SINGLE_REDIS_PORT")

    # 哨兵模式
    SENTINEL_NAME = os.getenv("SENTINEL_NAME")
    SENTINEL_HOSTS = os.getenv("SENTINEL_HOSTS")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE_PATH = os.path.abspath(os.getenv("LOG_FILE_PATH", "../log/app.log"))
    
missing_vars = []

for var_name in dir(Config):
    if not var_name.startswith("__"):  # 排除系统属性
        value = getattr(Config, var_name)
        if value is None:
            missing_vars.append(var_name)
if missing_vars:
    from log import logger
    logger.info("未设置的环境变量有:", missing_vars)
