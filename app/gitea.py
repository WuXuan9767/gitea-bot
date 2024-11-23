from security import verify_signature
from fastapi import APIRouter, Request, HTTPException
from schemas import GiteaPayload
from log import logger
from utils import send_message, build_content, build_deploy_url
from data import store_data
gitea_router = APIRouter()

@gitea_router.post("/gitea")
async def gitea_webhook(request: Request, payload: GiteaPayload):
    body = await request.body()
    
    # 安全检查
    Gitea_Signature = request.headers.get("X-Gitea-Signature")
    Authorization = request.headers.get("Authorization")
    if not verify_signature(Gitea_Signature, body.decode(), Authorization):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    uuid = request.headers.get("X-Gitea-Delivery")
    event = request.headers.get("X-Gitea-Event")

    if event != "pull_request":
        logger.info(f"ID: {uuid}, Event: {event}")
        return {"message": "Webhook received, but it`s not pr"}
    
    logger.info("收到 pr")
    action = payload.action
    repo_name = payload.repository.full_name
    username = payload.pull_request.user.full_name
    url = payload.pull_request.url
    title = payload.pull_request.title
    merged = payload.pull_request.merged
    state = payload.pull_request.state
    number = payload.number

    deploy_url = build_deploy_url(repo_name)
    repo_name =  f"{repo_name}/{number}"
    
    store_data(uuid, number, action, merged, state, repo_name, username, url, deploy_url, title)
    
    logger.debug(f"ID: {uuid}, Number: {number}, Action: {action}, Merged: {merged}, State: {state}, Repo: {repo_name}, Username: {username}, URL: {url}, Title: {title}")
    
    content = build_content(uuid, action, merged, state, repo_name, username, url, deploy_url, title)
    send_message(content)
    return {"message": "Webhook received"}
