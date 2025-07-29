from fastapi import FastAPI

app = FastAPI()


@app.route("/crud", methods=["GET", "POST", "PUT", "DELETE"])
async def crud():
    return {"message": "Hello, World!"}
