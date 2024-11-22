from pydantic import BaseModel

class User(BaseModel):
    id: int
    full_name: str
    email: str
    username: str

class PullRequest(BaseModel):
    url: str
    title: str
    user: User
    merged: bool
    state: str

class Repository(BaseModel):
    full_name: str

class GiteaPayload(BaseModel):
    action: str
    number: int
    pull_request: PullRequest
    repository: Repository


