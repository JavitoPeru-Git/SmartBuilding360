from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="SmartBuilding360 - Auth Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "172.31.X.X") # IP Privada de la MV BD
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "TuPasswordRoot")
DB_NAME = os.getenv("DB_NAME", "smartbuilding360_db")

def get_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    return conn

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

@app.post("/api/v1/auth/login")
def login(credentials: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT u.id, u.full_name, u.email, r.name 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE (u.username = %s OR u.email = %s) AND u.password_hash = %s
    """
    cursor.execute(query, (credentials.username_or_email, credentials.username_or_email, credentials.password))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return {
        "status": "success",
        "user": {
            "id": user[0],
            "full_name": user[1],
            "email": user[2],
            "role": user[3]
        },
        "token": f"fake-jwt-token-for-{user[0]}"
    }