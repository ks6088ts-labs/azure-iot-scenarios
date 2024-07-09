import fastapi

app = fastapi.FastAPI()


@app.get("/info")
async def info():
    return {
        "scenario": "iot-hub-messaging",
    }
