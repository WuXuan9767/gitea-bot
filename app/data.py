import redis
from redis.sentinel import Sentinel
from datetime import datetime
from config import Config
from log import logger

if Config.SENTINEL_HOSTS:
    sentinel_hosts = []
    for host in Config.SENTINEL_HOSTS.split(','):
        # 确保地址格式为 'host:port'
        parts = host.split(':')
        if len(parts) == 2:
            # 如果格式正确，添加到列表中
            sentinel_hosts.append((parts[0], int(parts[1])))
        else:
            # 如果格式不正确，输出警告或抛出错误
            logger.error(f"警告: 无效的地址格式 '{host}'，跳过该项")

if Config.IS_SINGLE:
    client = redis.StrictRedis(host=Config.SINGLE_REDIS_HOST, port=Config.SINGLE_REDIS_PORT, password=Config.REDIS_PASSWORD, db=15)
else:
    logger.info(f"SENTINEL_HOSTS:{sentinel_hosts}")
    sentinel = Sentinel(sentinel_hosts, socket_timeout=0.1)
    # 获取主节点连接
    master = sentinel.master_for(Config.SENTINEL_NAME, socket_timeout=0.1, db=15)
    # 获取从节点连接
    slave = sentinel.slave_for(Config.SENTINEL_NAME, socket_timeout=0.1)

def store_data(uuid: str, number: int, action: str, merged: bool, state: str, repo_name: str, username: str, url: str, title: str):
    timestamp = datetime.utcnow().isoformat()
    data = {
        'uuid': uuid,
        'number': number,
        'action': action,
        'merged': str(merged).lower(),
        'state': state,
        'repo_name': repo_name,
        'username': username,
        'url': url,
        'title': title,
        'time': timestamp
    }
    # 使用 uuid 作为 Redis 键

    key = data['uuid']
    
    # 将数据存储到 Redis 哈希中
    if Config.IS_SINGLE:
        client.hset(key, mapping=data)
        client.sadd(f"url:{url}", uuid)
    else:
        master.hset(key, mapping=data)
        master.sadd(f"url:{url}", uuid)

def get_data(uuid):
    key = str(uuid)
    if Config.IS_SINGLE:
        data = client.hgetall(key)
    else:
        data = slave.hgetall(key)
    return decode_data(data)
    
def decode_data(data):
    return {key.decode('utf-8'): value.decode('utf-8') for key, value in data.items()}

def get_latest_data_by_url(url: str):
    # 获取该 url 相关的所有 uuid
    if Config.IS_SINGLE:
        uuid_list = client.smembers(f"url:{url}")
    else:
        uuid_list = slave.smembers(f"url:{url}")
    if not uuid_list:
        logger.error(f"无{url}")
        return None  # 没有相关数据

    latest_data = None
    latest_timestamp = None

    # 遍历所有 uuid，获取对应的数据，并找出最大时间戳的记录
    for uuid in uuid_list:
        uuid = uuid.decode("utf-8")  # Redis 返回的是字节，需要解码成字符串
        if Config.IS_SINGLE:
            data = client.hgetall(uuid)  # 获取 uuid 对应的数据
        else:
            data = slave.hgetall(uuid)  # 获取 uuid 对应的数据
        if not data:
            continue  # 如果没有找到数据，跳过
        

        timestamp = data.get(b'time', None)

        if timestamp:
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_data = decode_data(data)
    return latest_data

def get_url_by_uuid(uuid: str):
    # 获取对应 uuid 的数据
  
    if Config.IS_SINGLE:
        data = client.hgetall(uuid) 
    else:
        data = slave.hgetall(uuid) 
    if not data:
        logger.error(f"无uuid: {uuid}")
        return None  # 如果没有数据，则返回 None

    # 提取 url 字段
    url = data.get(b'url', None)
    url = str(url.decode("utf-8")) 
    if url:
        logger.info(f"找到{url}")
        return url   # 解码为字符串并返回
    else:
        logger.error(f"uuid下无url:{url}")
        return None  # 如果没有 url 字段，返回 None

def get_latest_pr_by_uuid(uuid: str):
    url = get_url_by_uuid(uuid)
    latest_pr = get_latest_data_by_url(url)
    if latest_pr['uuid'] != uuid:
        return "outdate"
    return latest_pr['state']

