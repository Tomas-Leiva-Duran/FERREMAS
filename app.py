from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos')
def productos():
    lista_productos = [
        {'id': 1, 'nombre': 'Sierra Sable Inalámbrica 20V', 'precio': 104990},
        {'id': 2, 'nombre': 'Juego Dados de Impacto 10 Pzas', 'precio': 20990},
        {'id': 3, 'nombre': 'Llave Regulable 6"', 'precio': 3800},
        {'id': 4, 'nombre': 'Set de Llaves Allen 7 en 1', 'precio': 1990},
        {'id': 5, 'nombre': 'Juego de Destornilladores 4 piezas', 'precio': 2990},
        {'id': 6, 'nombre': 'Atornillador Inalámbrico Ronix 8530', 'precio': 32000},
    ]
    return render_template('productos.html', productos=lista_productos)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/api/productos', methods=['GET'])
def api_productos():
    data = [
        {'id': 1, 'nombre': 'Sierra Sable Inalámbrica 20V', 'precio': 104990},
        {'id': 2, 'nombre': 'Juego Dados de Impacto 10 Pzas', 'precio': 20990},
        {'id': 3, 'nombre': 'Llave Regulable 6"', 'precio': 3800},
        {'id': 4, 'nombre': 'Set de Llaves Allen 7 en 1', 'precio': 1990},
        {'id': 5, 'nombre': 'Juego de Destornilladores 4 piezas', 'precio': 2990},
        {'id': 6, 'nombre': 'Atornillador Inalámbrico Ronix 8530', 'precio': 32000},
    ]
    return jsonify(data)

@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    nuevo_producto = request.json
    return jsonify({'mensaje': 'Producto recibido', 'producto': nuevo_producto}), 201

if __name__ == '__main__':
    app.run(debug=True)