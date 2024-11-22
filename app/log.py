import logging, os
from config import Config


# 将字符串日志级别转换为对应的数值
log_level_num = getattr(logging, Config.LOG_LEVEL, None)
if not isinstance(log_level_num, int):
    raise ValueError(f'Invalid log level: {Config.LOG_LEVEL}')

# 创建log文件所在目录，防止因目录不存在报错
os.makedirs(os.path.dirname(Config.LOG_FILE_PATH), exist_ok=True) 

# 配置日志
logging.basicConfig(
    level=log_level_num,  # 设置日志级别
    format="[%(asctime)s][%(levelname)s]%(message)s",  # 设置日志格式
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler(Config.LOG_FILE_PATH)  # 输出到文件
    ]
)

# 创建日志记录器
logger = logging.getLogger(__name__)

logger.info(f"Log_level: {Config.LOG_LEVEL}, Log_file_path: {Config.LOG_FILE_PATH}")
