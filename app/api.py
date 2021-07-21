import time
from fastapi import FastAPI, Body, Depends, Request
from fastapi.responses import RedirectResponse
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.auth_handler import signJWT
from app.auth.auth_bearer import JWTBearer
from starlette.middleware.cors import CORSMiddleware


posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "Lorem Ipsum ..."
    }
]

users = [
    UserSchema(fullname="Rick", email="rickyang2910@gmail.com", password="1234")
]


app = FastAPI();

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["DELETE", "GET", "POST", "PUT"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print('response', response.status_code )
    print('response', response.headers )
    if response.status_code == 403:
        return RedirectResponse("https://typer.tiangolo.com")
    return response

@app.get("/token", tags=["root"])
def read_token():
    return {"access_token": "12345"}

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!."}

@app.get("/hello", tags=["root"])
async def read_root() -> dict:
    return {"message": "Hellow World"}

@app.get("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def get_posts() -> dict:
    return { "data": posts }


@app.get("/posts/{id}", tags=["posts"])
async def get_single_post(id: int) -> dict:
    if id > len(posts):
        return {
            "error": "No such post with the supplied ID."
        }

    for post in posts:
        if post["id"] == id:
            return {
                "data": post
            }

@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def add_post(post: PostSchema) -> dict:
    post.id = len(posts) + 1
    posts.append(post.dict())
    return {
        "data": "post added."
    }            

@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user) # replace with db call, making sure to hash the password first
    return signJWT(user.email)

@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False
