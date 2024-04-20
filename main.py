from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Latest Fastapi Crud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health route
app.add_api_route(
    "/health", lambda: {"status": "ok"}, methods=["GET"], tags=["Health Check"]
)

# Importing all routers
from app.routes import example_router

# Adding all routers
app.include_router(example_router.router, prefix="/example", tags=["Example"])
