from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import router

HOST = "localhost"
PORT = 8000

# Create FastAPI instance
app = FastAPI()


# Exception handlers
@app.exception_handler(FileNotFoundError)
async def not_found_exception_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})


# Include API routes
app.include_router(router)


# Define root endpoint.
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Object Store API",
        "documentation": {
            "Swagger UI": f"http://{HOST}:{PORT}/docs",
            "ReDoc": f"http://{HOST}:{PORT}/redoc",
        },
    }


# Set host to localhost and port to 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
