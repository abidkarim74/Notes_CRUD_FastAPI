from fastapi import FastAPI, Depends
from database.db import SessionLocal
from sqlalchemy import text
from router.auth_routes import auth_router
from router.notes_routes import note_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        # print("Trying to connect...")    

        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))

        print("Database connected successfully.")

    except Exception as e:
        print(f"Database connection failed: {e}")
        

app.include_router(auth_router)
app.include_router(note_router)
