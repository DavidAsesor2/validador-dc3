from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)

# 1. Función para crear nuestra base de datos de certificados
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

# 2. Esta es la "puerta" por donde Power Automate mandará los datos
@app.route('/api/guardar', methods=['POST'])
def guardar_certificado():
    datos = request.json
    try:
        conn = sqlite3.connect('certificados.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO certificados (folio, nombre, curp, curso, fecha, calificacion, empresa, rfc_empresa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['folio'], datos['nombre'], datos['curp'], 
            datos['curso'], datos['fecha'], datos['calificacion'], 
            datos['empresa'], datos['rfc_empresa']
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "éxito", "mensaje": "Datos guardados correctamente"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": "El folio ya existe o hubo un error"}), 400

# 3. Esta es la página que se abre cuando escanean el QR
@app.route('/validar/<folio>')
def validar(folio):
    conn = sqlite3.connect('certificados.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM certificados WHERE folio = ?', (folio,))
    certificado = c.fetchone()
    conn.close()

    if certificado:
        # Si encuentra el folio, muestra el diseño bonito
        return render_template('certificado.html', data=certificado)
    else:
        # Si escanean un QR falso
        return "<h1 style='color:red; text-align:center; font-family:sans-serif; margin-top:50px;'>Documento NO válido o no encontrado</h1>", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
