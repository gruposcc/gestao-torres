from fastapi import FastAPI

from routes.api.router import router as api_router

docs_url = "/docs"

app = FastAPI(docs_url=docs_url)
app.include_router(api_router)
