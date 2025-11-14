import uvicorn


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="localhost", port=22000, reload=True)

