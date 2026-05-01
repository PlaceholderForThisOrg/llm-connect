from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llm_connect.clients import lifespan

# from llm_connect.configs.app import ORIGINS
from llm_connect.errors import global_exception_handler, http_exception_handler
from llm_connect.routes import (
    ActivityRouter,
    AtomicPointRouter,
    ConversationRouter,
    LearnerRouter,
    MasteryRouter,
    ScenarioRouter,
    SessionRouter,
    TagRouter,
    cards,
    decks,
    dictionary,
    llm,
    private,
    public,
    reviews,
    scenario_template,
)

# import llm_connect.models

# 🧠 The main FastAPI app
app = FastAPI(
    title="my-companion",
    description="Core service for my-companion",
    version="1.0.1",
    docs_url="/docs",
    contact={
        "name": "Le Bui Trung Dung",
        "email": "trungdunglebui17112004@gmail.com",
    },
    lifespan=lifespan.lifespan,
)

# 🛣️ API routers, linked to app
app.include_router(router=public.router)
app.include_router(router=private.router)
app.include_router(router=llm.router)
app.include_router(router=dictionary.router)
app.include_router(router=LearnerRouter.router)
app.include_router(router=decks.router)
app.include_router(router=cards.router)
app.include_router(router=reviews.router)
app.include_router(router=ScenarioRouter.router)
app.include_router(router=scenario_template.router)
app.include_router(router=AtomicPointRouter.router)
app.include_router(router=SessionRouter.router)
app.include_router(router=ActivityRouter.router)
app.include_router(router=ConversationRouter.router)
app.include_router(router=MasteryRouter.router)
app.include_router(router=TagRouter.router)

# ⁉️ Exception handler

# HTTP handler
app.add_exception_handler(HTTPException, http_exception_handler)
# 🌍 Catch-all handler
app.add_exception_handler(Exception, global_exception_handler)

# 🖕 Middleware

# CORS to tell the browser to allow that script to read
# the response from the server (SOP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
