import asyncio
from app.core.db import engine


async def main() -> None:
    try:
        async with engine.begin() as conn:
            result = await conn.exec_driver_sql("SELECT 1")
            print("connected:", result.scalar())
    except Exception as e:
        import traceback
        print("ERROR:", type(e).__name__, str(e))
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

