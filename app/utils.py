import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.contact.v3 import *
from config import Config
import json
from data import get_data
from data import get_latest_pr_by_uuid
from log import logger

client = lark.Client.builder() \
    .app_id(Config.LARK_APP_ID) \
    .app_secret(Config.LARK_APP_SECRET) \
    .log_level(lark.LogLevel.INFO) \
    .build()


def build_content(uuid: str, action: str, merged: bool, state: str, repo_name: str, username: str, url: str, title: str):
# passed 为 True 表示不启用按钮，为 False 表示启用按钮
# state 有 open 和 closed 两种状态
    if action == "closed" and merged == False and state == "closed":
       action_message="变更已关闭"
       passed = True
    elif action == "closed" and merged == True and state == "closed":
       action_message="变更已合并"
       passed = True
    elif action == "edited" and merged == True and state == "closed":
        logger.info("此变更已关闭,不发送卡片")
        return 
    elif action == "edited" and merged == False and state == "open":
       action_message = "变更已重新编辑，待审核"
       passed = False
    elif action == "edited" and merged == False and state == "closed":
        logger.info("此变更已关闭,不发送卡片")
        return 
    elif action == "opened" and merged == False and state == "open":
       action_message="有代码合入，待审核"
       passed = False
    elif action == "reopened" and merged == False and state == "open":
       action_message="变更已重新开启，待审核"
       passed = False
    else:
       return False
    content = {
        "type": "template",
        "data": {
            "template_id": Config.LARK_CARD_ID,
            "template_version_name": Config.LARK_CARD_VERSION,
            "template_variable": {
                "uuid": uuid,  
                "action_message": action_message,  
                "repo_name": repo_name,  
                "username": username,
                "title":  title,
                "passed": passed  
            }
        }
    }
    return content


def build_refresh_content(uuid: str, approver_user_id: str):
    state=get_latest_pr_by_uuid(uuid)
    if state == "closed":
        logger.info("审批失败，变更已关闭")
        refresh_content = {
            "toast": {
                "content": "审批失败，变更已关闭",

                "type": "info"
            }
        }
    elif state == "outdate":
        logger.info("审批失败，变更已过期")
        refresh_content = {
            "toast": {
                "content": "审批失败，变更已过期",
                "type": "info"
            }
        }
    else:
        logger.info("审批成功")
        data=get_data(uuid)
        approver = get_username_by_userid(approver_user_id)
        refresh_content = {
            "card": {
                "type": "template",
                "data": {
                    "template_id": Config.LARK_CALLBACK_CARD_ID,
                    "template_version_name": Config.LARK_CALLBACK_CARD_VERSION,
                    "template_variable": {
                        "approver": approver,
                        "approver_user_id": approver_user_id,
                        "repo_name": data['repo_name'],  
                        "username": data['username'],  
                        "title":  data['title'] 
                    }
                }
            },
            "toast": {
                "content": "审核成功",
                "i18n": {
                "en_us": "card action success",
                "zh_cn": "审核成功"
                },
                "type": "info"
            }
        }
    return refresh_content


def get_username_by_userid(approver_user_id:str):
    request: GetUserRequest = GetUserRequest.builder() \
        .user_id(approver_user_id) \
        .user_id_type("user_id") \
        .department_id_type("open_department_id") \
        .build()

    logger.debug(f"发送请求查询user_id为{approver_user_id}的姓名")
    response: GetUserResponse = client.contact.v3.user.get(request)

    if not response.success():
        logger.error(
            f"获取姓名失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    logger.debug(response.data)
    return response.data.user.name


def send_message(content_data: dict[str]):


    if not content_data:
       return
    # 将content_data转换为JSON字符串
    content_str = json.dumps(content_data)

    # 创建消息请求
    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(Config.LARK_CHAT_ID)
            .msg_type("interactive")
            .content(content_str)
            .build()) \
        .build()
    logger.info(f"发送卡片")
    logger.debug(content_str)
    response: CreateMessageResponse = client.im.v1.message.create(request)
    
    # 处理失败返回
    if not response.success():
        logger.error(
            f"卡片发送失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    logger.debug(response.data)

    return True