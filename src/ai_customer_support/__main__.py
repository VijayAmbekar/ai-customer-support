from dotenv import load_dotenv
import uvicorn

load_dotenv()


def main() -> None:
    uvicorn.run(
        "ai_customer_support.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
