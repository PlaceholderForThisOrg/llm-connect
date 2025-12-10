from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from llm_connect.errors import global_exception_handler, http_exception_handler
from llm_connect.routes import llm, private, public

# 🧠 The main FastAPI app
app = FastAPI(
    title="LLM connect service",
    description="Simple connector to the LLM service",
    version="1.0.0",
    docs_url="/docs",
    contact={"name": "Le Bui Trung Dung", "email": "trungdunglebui17112004@gmail.com"},
)

# 🛣️ Different API routes
app.include_router(router=public.router)
app.include_router(router=private.router)
app.include_router(router=llm.router)

# ⁉️ Exception handler

# HTTP handler
app.add_exception_handler(HTTPException, http_exception_handler)
# 🌍 Catch-all handler
app.add_exception_handler(Exception, global_exception_handler)
