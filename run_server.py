import uvicorn
from settings import config

if __name__ == "__main__":
    name = "app:app"
    uvicorn.run(
        name,
        host='0.0.0.0',
        port=config.SERVER_PORT,
        reload=True,
        log_level="debug"
    )