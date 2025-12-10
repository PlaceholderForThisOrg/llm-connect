from pathlib import Path

from dotenv import load_dotenv

from llm_connect.configs import app


def main():
    import uvicorn

    # load env variables in .env
    env_path = Path(".") / ".env.development"
    load_dotenv(env_path, verbose=True)

    app_loc = "llm_connect.app:app"
    uvicorn.run(app_loc, host=app.HOST, port=app.PORT, reload=True)


if __name__ == "__main__":
    main()
