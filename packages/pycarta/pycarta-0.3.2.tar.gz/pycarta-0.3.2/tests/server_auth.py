import json
from fastapi import FastAPI
from flask import request
from pydantic import BaseModel


class Content(BaseModel):
    data: str


app = FastAPI()

@app.get("/auth")
def auth():
    return {
        "userPoolId": "<poolId>",
        "userPoolWebClientId": "<webClientId>",
        "region": "<region>",
    }

@app.post("/auth")
def auth(body: Content):
    return f"auth POST: {body.data}"

@app.put("/auth")
def auth(body: Content):
    return f"auth PUT: {body.data}"

@app.head("/auth")
def auth():
    return None

@app.patch("/auth")
def auth(body: Content):
    return f"auth PATCH: {body.data}"

@app.delete("/auth")
def auth(body: Content | None=None):
    if body:
        return f"auth DELETE: {body.data}"
    else:
        return "auth DELETE"
