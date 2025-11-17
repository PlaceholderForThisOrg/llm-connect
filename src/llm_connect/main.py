from llm_connect.configs import app


def main():
    import uvicorn

    app_loc = "llm_connect.app:app"
    uvicorn.run(app_loc, host=app.HOST, port=app.PORT, reload=True)


if __name__ == "__main__":
    main()
