from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llm_connect.clients import lifespan
from llm_connect.configs.app import ORIGINS
from llm_connect.errors import global_exception_handler, http_exception_handler
from llm_connect.routes import cards, decks, dictionary, learner, llm, private, public

# 🧠 The main FastAPI app
app = FastAPI(
    title="LLM connect service",
    description="Simple connector to the LLM service",
    version="1.0.0",
    docs_url="/docs",
    contact={"name": "Le Bui Trung Dung", "email": "trungdunglebui17112004@gmail.com"},
    lifespan=lifespan.lifespan,
)

# 🛣️ API routes
app.include_router(router=public.router)
app.include_router(router=private.router)
app.include_router(router=llm.router)
app.include_router(router=dictionary.router)
app.include_router(router=learner.router)
app.include_router(router=decks.router)
app.include_router(router=cards.router)

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
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
