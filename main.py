from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.LambdaRouter import LambdaRouter
from routers.SlackRouter import SlackRouter
from routers.ReactRouter import ReactRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(LambdaRouter)
app.include_router(SlackRouter)
app.include_router(ReactRouter)

# @app.get("/")
# def post_ban():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}