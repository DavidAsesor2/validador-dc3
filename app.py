from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)

# Función para crear la base de datos
def init_db():
    conn = sqlite3.connect('certificados.db')
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
    conn.close()

@app.route('/')
def home():
    return "El sistema de validación de DC-3 está activo."

# Ruta receptora de Power Automate
@app.route('/api/guardar', methods=['POST'])
def guardar_certificado():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"status": "error", "mensaje": "JSON no recibido correctamente"}), 400

    try:
        conn = sqlite3.connect('certificados.db')
        c = conn.cursor()
        
        # INSERT OR REPLACE evita que el flujo se rompa si el folio ya existe
        c.execute('''
            INSERT OR REPLACE INTO certificados (folio, nombre, curp, curso, fecha, calificacion, empresa, rfc_empresa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos.get('folio', ''),
            datos.get('nombre', ''),
            datos.get('curp', ''),
            datos.get('curso', ''),
            datos.get('fecha', ''),
            datos.get('calificacion', ''),
            datos.get('empresa', ''),
            datos.get('rfc_empresa', '')
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "éxito", "mensaje": "Datos guardados correctamente"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# Ruta visual del código QR
@app.route('/validar/<folio>')
def validar(folio):
    conn = sqlite3.connect('certificados.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM certificados WHERE folio = ?', (folio,))
    certificado = c.fetchone()
    conn.close()

    if certificado:
        return render_template('certificado.html', data=certificado)
    else:
        return "<h1 style='color:red; text-align:center; font-family:sans-serif; margin-top:50px;'>Documento NO válido o no encontrado</h1>", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
