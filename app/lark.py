from fastapi import APIRouter, Request
import json
from security import cipher
from log import logger
from utils import build_refresh_content

lark_router = APIRouter()

@lark_router.post("/")
async def lark(request: Request):

    data = await request.json()

    if data['encrypt']:   
      data = cipher.decrypt_string(data['encrypt'])

    data = json.loads(data)
    
    challenge = data.get("challenge")
    if challenge:
      logger.info(f"收到challenge:{challenge},立即返回")
      return {"challenge": challenge}

    uuid = data['event']['action']['value']
    approver_user_id = data['event']['operator']['user_id']

    logger.info(f"收到回调 uuid: {uuid}")
    logger.debug(f"回调内容: {data}")

    refresh_connect = build_refresh_content(uuid, approver_user_id)
    logger.info("发送响应")
    return refresh_connect
