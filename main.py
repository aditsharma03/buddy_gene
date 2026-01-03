
import os
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI

from routes import jiraRoutes, poRoutes, authRoutes




app = FastAPI()



def main():
    load_dotenv()
    app.include_router(authRoutes.router) 
    app.include_router(jiraRoutes.router)
    app.include_router(poRoutes.router)


    PORT: int = int(os.getenv("PORT") or 8000)

    uvicorn.run(app, port=PORT)



if __name__ == "__main__":
    main()
