import asyncio
import sys

import uvicorn
from fastapi import FastAPI

from api.main import router as api_router
from db import ping_database
from migrations.migrate import migrate_database_tables
from settings import settings

# move app object outside of __main__ so auto reload can be set
app = FastAPI(title="BTJ Academy")
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        match sys.argv[1]:
            case "api":
                asyncio.run(ping_database())  # ping database before server start, exit when failed

                uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

            case "migrate":
                migrate_database_tables()
