from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import pandas as pd
from datetime import datetime
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType


app = Flask(__name__)
app.secret_key = 'ferremas_secret_key'  # Necesario para las sesiones

# Configuración de credenciales (reemplaza por las reales de tu comercio)
Transaction.commerce_code = 'TU_CODIGO_COMERCIO'
Transaction.api_key = 'TU_API_KEY'
Transaction.integration_type = IntegrationType.TEST  # Cambia a LIVE en producción

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

@app.route('/api/buscar', methods=['GET'])
def buscar_productos():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Filtrar productos que coincidan con la búsqueda
    productos_filtrados = productos_df[
        productos_df['nombre'].str.lower().str.contains(query)
    ].to_dict(orient='records')
    
    return jsonify(productos_filtrados)

@app.route('/api/carrito', methods=['GET'])
def obtener_carrito():
    if 'carrito' not in session:
        session['carrito'] = []
    return jsonify(session['carrito'])

@app.route('/api/carrito/agregar', methods=['POST'])
def agregar_al_carrito():
    if 'carrito' not in session:
        session['carrito'] = []
    
    producto = request.json
    if not producto or 'id' not in producto:
        return jsonify({'error': 'Datos de producto inválidos'}), 400
    
    # Verificar si el producto ya está en el carrito
    for item in session['carrito']:
        if item['id'] == producto['id']:
            item['cantidad'] += producto.get('cantidad', 1)
            session.modified = True
            return jsonify(session['carrito'])
    
    # Si no está en el carrito, agregarlo
    producto['cantidad'] = producto.get('cantidad', 1)
    session['carrito'].append(producto)
    session.modified = True
    
    return jsonify(session['carrito'])

@app.route('/api/carrito/actualizar', methods=['PUT'])
def actualizar_carrito():
    if 'carrito' not in session:
        return jsonify({'error': 'Carrito no encontrado'}), 404
    
    producto = request.json
    if not producto or 'id' not in producto:
        return jsonify({'error': 'Datos de producto inválidos'}), 400
    
    # Actualizar cantidad del producto
    for item in session['carrito']:
        if item['id'] == producto['id']:
            item['cantidad'] = producto.get('cantidad', 1)
            session.modified = True
            return jsonify(session['carrito'])
    
    return jsonify({'error': 'Producto no encontrado en el carrito'}), 404

@app.route('/api/carrito/eliminar/<int:producto_id>', methods=['DELETE'])
def eliminar_del_carrito(producto_id):
    if 'carrito' not in session:
        return jsonify({'error': 'Carrito no encontrado'}), 404
    
    session['carrito'] = [item for item in session['carrito'] if item['id'] != producto_id]
    session.modified = True
    
    return jsonify(session['carrito'])

@app.route('/api/carrito/limpiar', methods=['DELETE'])
def limpiar_carrito():
    session['carrito'] = []
    session.modified = True
    return jsonify({'mensaje': 'Carrito limpiado exitosamente'})

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

@app.route('/producto/<int:id>')
def producto_detalle(id):
    producto = productos_df[productos_df['id'] == id].to_dict(orient='records')
    if not producto:
        return 'Producto no encontrado', 404
    return render_template('producto_detalle.html', producto=producto[0])

@app.route('/carrito')
def pagina_carrito():
    carrito = session.get('carrito', [])
    return render_template('carrito.html', carrito=carrito)

@app.route('/checkout/inicio', methods=['GET', 'POST'])
def checkout_inicio():
    if request.method == 'POST':
        # Guardar datos del usuario en sesión
        session['checkout_usuario'] = request.form.to_dict()
        return redirect(url_for('checkout_tipo_entrega'))
    carrito = session.get('carrito', [])
    return render_template('checkout_inicio.html', carrito=carrito)

@app.route('/checkout/tipo-entrega', methods=['GET', 'POST'])
def checkout_tipo_entrega():
    if request.method == 'POST':
        session['checkout_entrega'] = request.form.to_dict()
        return redirect(url_for('checkout_pago'))
    return render_template('checkout_tipo_entrega.html')

@app.route('/checkout/pago', methods=['GET', 'POST'])
def checkout_pago():
    if request.method == 'POST':
        carrito = session.get('carrito', [])
        usuario = session.get('checkout_usuario', {})
        entrega = session.get('checkout_entrega', {})
        amount = sum(item['precio'] * item['cantidad'] for item in carrito)
        buy_order = f"ORD-{usuario.get('email','anon')}-{session.sid}"
        session_id = session.sid
        return_url = url_for('checkout_confirmacion', _external=True)
        response = Transaction.create(buy_order, session_id, amount, return_url)
        token = response['token']
        url_tbk = response['url']
        return redirect(f"{url_tbk}?token_ws={token}")
    return render_template('checkout_pago.html')

@app.route('/checkout/confirmacion', methods=['POST'])
def checkout_confirmacion():
    token = request.form.get('token_ws')
    response = Transaction.commit(token)
    if response['status'] == 'AUTHORIZED':
        return render_template('checkout_exito.html', datos=response)
    else:
        return render_template('checkout_error.html', datos=response)

#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
