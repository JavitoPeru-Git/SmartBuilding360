from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2, os

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "172.31.X.X")

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port="5432", user="root", password="TuPasswordRoot", dbname="smartbuilding360_db"
    )

@app.route('/api/v1/receipts/<int:resident_id>', methods=['GET'])
def get_pending_receipts(resident_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, period, ordinary_fee, extraordinary_fee, reserve_fund, fine, total_amount, due_date, status 
        FROM receipts WHERE resident_id = %s AND status = 'Pendiente'
    """, (resident_id,))
    rows = cursor.fetchall()
    conn.close()
    
    receipts = [{
        "id": r[0], "period": r[1], "ordinary": float(r[2]), "extraordinary": float(r[3]),
        "reserve_fund": float(r[4]), "fine": float(r[5]), "total": float(r[6]), "due_date": str(r[7]), "status": r[8]
    } for r in rows]
    return jsonify(receipts)

@app.route('/api/v1/payments/checkout', methods=['POST'])
def process_payment():
    data = request.json
    receipt_ids = data.get('receipt_ids', [])
    card_number = data.get('card_number')
    cvv = data.get('cvv')

    conn = get_db()
    cursor = conn.cursor()

    # Validar pasarela simulada
    cursor.execute("SELECT balance FROM payment_methods WHERE card_number = %s AND cvv = %s", (card_number, cvv))
    card = cursor.fetchone()

    if not card:
        conn.close()
        return jsonify({"error": "Tarjeta o datos de pasarela no validos"}), 400

    # Marcar recibos como pagados
    for r_id in receipt_ids:
        cursor.execute("UPDATE receipts SET status = 'Pagado' WHERE id = %s", (r_id,))

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Pago procesado exitosamente mediante pasarela simulada."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)