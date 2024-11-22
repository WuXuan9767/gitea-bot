from fastapi import FastAPI
from gitea import gitea_router
from lark import lark_router



app = FastAPI()

app.include_router(gitea_router)
app.include_router(lark_router)

