from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2, os, pandas as pd, io

app = FastAPI(title="SmartBuilding360 - Residents Microservice")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

DB_HOST = os.getenv("DB_HOST", "172.31.X.X")

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port="5432", user="root", password="TuPasswordRoot", dbname="smartbuilding360_db"
    )

class ResidentCreate(BaseModel):
    full_name: str
    email: str
    document_number: str
    tower: str
    apartment: str
    phone: str

@app.get("/api/v1/residents")
def list_residents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, u.full_name, u.email, r.document_number, r.tower, r.apartment, r.phone 
        FROM residents r JOIN users u ON r.user_id = u.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "full_name": r[1], "email": r[2], "document": r[3], "tower": r[4], "apartment": r[5], "phone": r[6]} for r in rows]

@app.post("/api/v1/residents/excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Formato invalido de archivo Excel")
    
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Columnas esperadas: full_name, email, password, document_number, tower, apartment, phone
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, role_id) VALUES (%s,%s,%s,%s,2) RETURNING id",
            (row['email'], row['email'], row.get('password', '123456'), row['full_name'])
        )
        user_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO residents (user_id, document_number, tower, apartment, phone) VALUES (%s,%s,%s,%s,%s)",
            (user_id, str(row['document_number']), str(row['tower']), str(row['apartment']), str(row['phone']))
        )
    conn.commit()
    conn.close()
    return {"message": f"Se procesaron e importaron {len(df)} residentes con exito."}

@app.delete("/api/v1/residents/{resident_id}")
def delete_resident(resident_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE id = %s", (resident_id,))
    conn.commit()
    conn.close()
    return {"message": "Residente eliminado correctamente."}