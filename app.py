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

ventas_df = pd.read_excel('BBDD_ventas.xlsx', engine='openpyxl')
ventas_df['Fecha'] = pd.to_datetime(ventas_df['Fecha'], dayfirst=True)

prod_exc = 'bbdd_productos.xlsx'
productos_df = pd.read_excel(prod_exc, engine='openpyxl')

#Metodo para el reporte mensual del administrador
@app.route('/admin/reports/sales/<int:month>', methods=['GET'])
def reporte_ventas(month):
    
    datos_mes = ventas_df[ventas_df['Fecha'].dt.month == month]
    
    if datos_mes.empty:
        return jsonify({'error': f'No hay ventas registradas para el mes {month}'}), 404

    datos_mes['TotalVenta'] = datos_mes['Precio'] * datos_mes['Cantidad']
    total_ventas = int(datos_mes['TotalVenta'].sum())
    total_productos = int(datos_mes['Cantidad'].sum())

    return jsonify({
        'mes': month,
        'total_ventas': total_ventas,
        'productos_vendidos': total_productos
    })


#Metodo para obtener la cantidad de productos actuales
@app.route('/salesperson/products', methods=['GET'])
def productos_disponibles():
    productos = productos_df[['nombre', 'cantidad']].to_dict(orient='records')
    return jsonify(productos)

#Metodo para actualizar la cantidad de un producto
@app.route('/salesperson/products/<int:producto_id>', methods=['PATCH'])
def actualizar_cantidad(producto_id):
    datos = request.get_json()
    if 'cantidad' not in datos :
        return jsonify({
            'error':'Se requiere el campo cantidad'
        }), 400

    indice = productos_df[productos_df['id'] == producto_id].index

    if indice.empty:
        return(jsonify({
            'error':f'El producto con id {producto_id} no se ha encontrado'
        })), 400

    try:
        nueva_cantidad = int(datos['cantidad'])
        productos_df.loc[indice, 'cantidad'] = nueva_cantidad
        productos_df.to_excel(prod_exc, index=False, engine='openpyxl')
        return jsonify({'mensaje': f'Cantidad actualizada a {nueva_cantidad}'}), 200
    except Exception as e:  
        return jsonify({'error': str(e)}), 400
    
@app.route('/salesperson/orders', methods=['POST'])
def registrar_venta():
    datos = request.get_json()
    
    # Validar campos requeridos
    campos_requeridos = ['id_producto', 'fecha', 'cantidad']
    if not all(campo in datos for campo in campos_requeridos):
        return jsonify({'error': 'Faltan campos requeridos: id_producto, fecha, cantidad'}), 400

    try:
        id_producto = int(datos['id_producto'])
        fecha = pd.to_datetime(datos['fecha'], dayfirst=True)
        cantidad_vendida = int(datos['cantidad'])
    except Exception as e:
        return jsonify({'error': f'Datos inválidos: {str(e)}'}), 400

    # Buscar el producto
    producto = productos_df[productos_df['id'] == id_producto]
    if producto.empty:
        return jsonify({'error': 'Producto no encontrado'}), 404

    producto = producto.iloc[0]
    stock_disponible = int(producto['cantidad'])

    if cantidad_vendida > stock_disponible:
        return jsonify({'error': f'Stock insuficiente. Disponibles: {stock_disponible}'}), 400

    # Registrar venta
    nueva_venta = {
        'Fecha': fecha.strftime('%d-%m-%Y'),
        'PRODUCTO': producto['nombre'],
        'Precio': float(producto['PrecioUnidad']),
        'Cantidad': cantidad_vendida
    }

    # Cargar ventas desde Excel nuevamente por seguridad
    ventas_df = pd.read_excel('BBDD_ventas.xlsx', engine='openpyxl')
    ventas_df = pd.concat([ventas_df, pd.DataFrame([nueva_venta])], ignore_index=True)
    ventas_df.to_excel('BBDD_ventas.xlsx', index=False, engine='openpyxl')

    # Actualizar stock
    productos_df.loc[productos_df['id'] == id_producto, 'cantidad'] = stock_disponible - cantidad_vendida
    productos_df.to_excel('bbdd_productos.xlsx', index=False, engine='openpyxl')

    return jsonify({'mensaje': 'Venta registrada exitosamente'}), 201

# @app.route('/warehouse/inventory', methods=['GET'])


# @app.route('/warehouse/dispatch', methods=['POST'])


# @app.route('/accountant/sales-transactions/{date-range}', methods=['GET'])


#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
