import os
from flask import Flask, request, render_template, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Conexión a tu base de datos en la nube
DB_URL = "postgresql://postgres.fvtibuitvbiuqygpallg:AsherEx3:14Asher@aws-0-us-west-2.pooler.supabase.com:5432/postgres"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# 1. Crear la base de datos
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS certificados (
            folio TEXT PRIMARY KEY,
            nombre TEXT,
            curp TEXT,
            curso TEXT,
            fecha TEXT,
            calificacion TEXT,
            empresa TEXT,
            rfc_empresa TEXT
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

# Forzar la creación de la tabla al arrancar
init_db()

@app.route('/')
def home():
    return "El sistema de validación de DC-3 está activo y en la nube."

@app.route('/api/guardar', methods=['POST'])
def guardar_certificado():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"status": "error", "mensaje": "JSON vacío"}), 400

    folio = datos.get('folio', '')
    if not folio:
        return jsonify({"status": "error", "mensaje": "Folio requerido"}), 400

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM certificados WHERE folio = %s', (folio,))
        c.execute('''
            INSERT INTO certificados (folio, nombre, curp, curso, fecha, calificacion, empresa, rfc_empresa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            folio, datos.get('nombre', ''), datos.get('curp', ''), 
            datos.get('curso', ''), datos.get('fecha', ''), 
            datos.get('calificacion', ''), datos.get('empresa', ''), 
            datos.get('rfc_empresa', '')
        ))
        conn.commit()
        c.close()
        conn.close()
        return jsonify({"status": "éxito", "mensaje": "Guardado"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/validar/<folio>')
def validar(folio):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('SELECT * FROM certificados WHERE folio = %s', (folio,))
    certificado = c.fetchone()
    c.close()
    conn.close()

    if certificado:
        return render_template('certificado.html', data=certificado)
    else:
        return "<h1 style='color:red; text-align:center; margin-top:50px;'>Documento NO válido</h1>", 404

if __name__ == '__main__':
    app.run(debug=True)
