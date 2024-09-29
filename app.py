from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from tinydb import TinyDB, Query
from fuzzywuzzy import fuzz
import os
import random
from datetime import datetime
import json
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = '/archivos/'
app.secret_key = 'your_secret_key'
db = TinyDB('./database.json', encoding='utf-8')

# Ruta del archivo JSON
DATA_FILE_PATH = '/static/data/data.json'

# Función para cargar los datos desde el archivo JSON
def load_data():
    with open(DATA_FILE_PATH, 'r') as file:
        return json.load(file)

# Función para guardar los datos en el archivo JSON
def save_data(data):
    with open(DATA_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/posts', methods=['GET'])
def get_posts():
    data = load_data()
    return jsonify(data)

def obtener_recomendados():
    productos = db.all()
    return random.sample(productos, min(len(productos), 5)) if productos else []

def obtener_mas_nuevos():
    productos = db.all()
    productos_ordenados = sorted(productos, key=lambda x: x.get('id', 0), reverse=True)
    return productos_ordenados[:5]

def obtener_mas_vendidos():
    productos = db.all()
    productos_ordenados = sorted(productos, key=lambda x: sum([compra['cantidad'] for compra in x.get('compras', [])]), reverse=True)
    return productos_ordenados[:5]

def obtener_en_oferta():
    productos = db.all()
    productos_en_oferta = [producto for producto in productos if producto.get('en_promocion', False)]
    return productos_en_oferta[:5]  # Devuelve los primeros 5 productos en oferta

def generate_unique_id():
    while True:
        id = random.randint(1000000000, 9999999999)
        if not db.search(Query().id == id):
            return id

@app.route('/pqr')
def pqr():
    return render_template('/pages/pqr.html')

@app.route('/devolver')
def devolver():
    return render_template('/pages/devolver.html')

@app.route('/envios_gratis')
def envio_gratis():
    return render_template('/pages/envio_gratis.html')

@app.route('/envios_rapidos')
def envio_rapido():
    return render_template('/pages/envio_rapido.html')

@app.route('/servicios')
def servicios():
    return render_template('/pages/servicios.html')

@app.route('/ofertas')
def ofertas():
    en_oferta = obtener_en_oferta()
    return render_template('/pages/ofertas.html', en_oferta=en_oferta)

@app.route('/nuevos')
def nuevos():
    mas_nuevos = obtener_mas_nuevos()
    return render_template('/pages/nuevos.html', nuevos=mas_nuevos)

@app.route('/contacto')
def contacto():
    return render_template('/pages/contacto.html')

@app.route('/como_comprar')
def como_comprar():
    return render_template('/pages/como_comprar.html')

@app.route('/preguntas_frecuentes')
def preguntas_frecuentes():
    return render_template('/pages/preguntas_frecuentes.html')

@app.route('/grafico')
def grafico():
    return render_template('grafico.html')

@app.route('/')
def index():
    recomendados = obtener_recomendados()
    mas_nuevos = obtener_mas_nuevos()
    mas_vendidos = obtener_mas_vendidos()
    en_oferta = obtener_en_oferta()
    return render_template('/pages/index.html', recomendados=recomendados, mas_nuevos=mas_nuevos, mas_vendidos=mas_vendidos, en_oferta=en_oferta)

@app.route('/acceder', methods=['GET', 'POST'])
def acceder():
    if 'token' in session:
        return redirect(url_for('panel'))

    if request.method == 'POST':
        token = request.form['token']
        password = request.form['password']
        if token == '1234567890' and password == 'password':
            session['token'] = token
            return redirect(url_for('panel'))
        else:
            return render_template('/pages/acceder.html', error='Token o contraseña incorrectos')

    return render_template('/pages/acceder.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('token', None)
    return redirect(url_for('acceder'))

@app.route('/panel')
def panel():
    if 'token' not in session:
        return redirect(url_for('acceder'))

    productos = db.all()
    mas_vendidos = obtener_mas_vendidos()

    total_productos = len(productos)
    total_nina = sum(1 for p in productos if p.get('para_ninas'))
    total_nino = sum(1 for p in productos if p.get('para_ninos'))
    total_unisex = sum(1 for p in productos if p.get('unisex'))

    categorias_contador = {}
    for producto in productos:
        for categoria in producto.get('categorias', []):
            if categoria in categorias_contador:
                categorias_contador[categoria] += 1
            else:
                categorias_contador[categoria] = 1

    datos_panel = {
        'total_productos': total_productos,
        'total_nina': total_nina,
        'total_nino': total_nino,
        'total_unisex': total_unisex,
        'categorias_contador': categorias_contador
    }

    return render_template('/pages/panel.html', mas_vendidos=mas_vendidos, datos_panel=datos_panel)

@app.route('/editar')
def editar():
    if 'token' not in session:
        return redirect(url_for('acceder'))
    productos = db.all()
    return render_template('/pages/editar.html', productos=productos)

@app.route('/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    if 'token' not in session:
        return redirect(url_for('acceder'))

    Producto = Query()
    producto = db.get(Producto.id == producto_id)

    if not producto:
        return "Producto no encontrado", 404

    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto'].encode('utf-8').decode('utf-8')
        precio_producto = float(request.form['precio_producto'])
        en_promocion = 'en_promocion' in request.form
        porcentaje_promocion = int(request.form['porcentaje_promocion']) if en_promocion else 0
        para_ninos = 'para_ninos' in request.form
        para_ninas = 'para_ninas' in request.form
        unisex = 'unisex' in request.form
        categorias = request.form['categorias'].encode('utf-8').decode('utf-8')
        descripcion_producto = request.form['descripcion_producto'].encode('utf-8').decode('utf-8')
        envio_gratis = 'envio_gratis' in request.form
        envio_rapido = 'envio_rapido' in request.form
        marca = request.form['marca'].encode('utf-8').decode('utf-8')
        color = request.form['color'].encode('utf-8').decode('utf-8')

        categorias_list = [cat.strip().lower() for cat in categorias.split(',')]

        detalles = request.form.getlist('detalles[]')
        valores = request.form.getlist('valores[]')

        detalles_adicionales = [{'detalle': d.encode('utf-8').decode('utf-8'), 'valor': v.encode('utf-8').decode('utf-8')} for d, v in zip(detalles, valores)]

        if 'imagen_producto' in request.files:
            imagen_producto = request.files['imagen_producto']
            if imagen_producto.filename != '':
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_producto.filename)
                imagen_producto.save(imagen_path)
            else:
                imagen_path = producto.get('imagen_producto')
        else:
            imagen_path = producto.get('imagen_producto')

        db.update({
            'nombre_producto': nombre_producto,
            'precio_producto': precio_producto,
            'en_promocion': en_promocion,
            'porcentaje_promocion': porcentaje_promocion,
            'para_ninos': para_ninos,
            'para_ninas': para_ninas,
            'unisex': unisex,
            'categorias': categorias_list,
            'descripcion': descripcion_producto,
            'detalles_adicionales': detalles_adicionales,
            'imagen_producto': imagen_path,
            'envio_gratis': envio_gratis,
            'envio_rapido': envio_rapido,
            'marca': marca,
            'color': color
        }, Producto.id == producto_id)

        return redirect(url_for('editar'))

    return render_template('/pages/editar_producto.html', producto=producto)

@app.route('/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    if 'token' not in session:
        return redirect(url_for('acceder'))

    Producto = Query()
    db.remove(Producto.id == producto_id)

    return redirect(url_for('index'))

@app.route('/subir_producto', methods=['GET', 'POST'])
def subir_producto():
    if 'token' not in session:
        return redirect(url_for('acceder'))

    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto'].encode('utf-8').decode('utf-8')
        precio_producto = float(request.form['precio_producto'])
        en_promocion = 'en_promocion' in request.form
        porcentaje_promocion = int(request.form['porcentaje_promocion']) if en_promocion else 0
        para_ninos = 'para_ninos' in request.form
        para_ninas = 'para_ninas' in request.form
        unisex = 'unisex' in request.form
        categorias = request.form['categorias'].encode('utf-8').decode('utf-8')
        descripcion_producto = request.form['descripcion_producto'].encode('utf-8').decode('utf-8')
        envio_gratis = 'envio_gratis' in request.form
        envio_rapido = 'envio_rapido' in request.form
        marca = request.form['marca'].encode('utf-8').decode('utf-8')
        color = request.form['color'].encode('utf-8').decode('utf-8')

        categorias_list = [cat.strip().lower() for cat in categorias.split(',')]

        detalles = request.form.getlist('detalles[]')
        valores = request.form.getlist('valores[]')

        detalles_adicionales = [{'detalle': d.encode('utf-8').decode('utf-8'), 'valor': v.encode('utf-8').decode('utf-8')} for d, v in zip(detalles, valores)]

        if 'imagen_producto' in request.files:
            imagen_producto = request.files['imagen_producto']
            if imagen_producto.filename != '':
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_producto.filename)
                imagen_producto.save(imagen_path)
            else:
                imagen_path = None
        else:
            imagen_path = None

        producto_id = generate_unique_id()

        db.insert({
            'id': producto_id,
            'nombre_producto': nombre_producto,
            'precio_producto': precio_producto,
            'en_promocion': en_promocion,
            'porcentaje_promocion': porcentaje_promocion,
            'para_ninos': para_ninos,
            'para_ninas': para_ninas,
            'unisex': unisex,
            'categorias': categorias_list,
            'descripcion': descripcion_producto,
            'detalles_adicionales': detalles_adicionales,
            'imagen_producto': imagen_path,
            'envio_gratis': envio_gratis,
            'envio_rapido': envio_rapido,
            'marca': marca,
            'color': color,
            'compras': []  # Inicializar la lista de compras
        })

        return redirect(url_for('subir_producto'))

    return render_template('/pages/subir_producto.html')

@app.route('/producto/<int:producto_id>', methods=['GET'])
def mostrar_producto(producto_id):
    Producto = Query()
    producto = db.get(Producto.id == producto_id)
    if producto:
        mas_vendidos = obtener_mas_vendidos()
        recomendados = obtener_recomendados()
        return render_template('/pages/producto.html', producto=producto, mas_vendidos=mas_vendidos, recomendados=recomendados)
    else:
        return "Producto no encontrado", 404

@app.route('/comprar', methods=['POST'])
def comprar():
    producto_id = int(request.form['producto_id'])
    cantidad = int(request.form['cantidad'])
    fecha_compra = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    Producto = Query()
    producto = db.get(Producto.id == producto_id)
    if producto:
        compra = {
            'cantidad': cantidad,
            'fecha_compra': fecha_compra
        }
        producto['compras'].append(compra)
        db.update({'compras': producto['compras']}, Producto.id == producto_id)

        valor_producto = producto['precio_producto']

        # Crear el enlace de WhatsApp
        numero_whatsapp = '+573332547062'
        mensaje = f"Hola, acabo de visitar tu sitio web y encontré el producto con ID: {producto_id}. Estoy interesado en comprar {cantidad} unidades. ¿Podrías proporcionarme más información sobre el proceso de pago? Gracias."
        enlace_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensaje}"

        return redirect(enlace_whatsapp)
    else:
        return "Producto no encontrado", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    selected_brands = request.args.getlist('marca')
    selected_colors = request.args.getlist('color')
    precio_min = request.args.get('precio_min', 0, type=float)
    precio_max = request.args.get('precio_max', 3000000, type=float)
    envio_gratis = 'envio_gratis' in request.args
    envio_rapido = 'envio_rapido' in request.args
    sort_by = request.args.get('sort_by', 'relevancia')
    Producto = Query()
    results = []

    if query:
        # Separar la búsqueda en género y categoría
        es_nina = 'para niñas' in query
        es_nino = 'para niños' in query
        es_unisex = 'unisex' in query
        categorias_busqueda = query.replace('para niñas', '').replace('para niños', '').replace('unisex', '').strip().split()
        categorias_busqueda = [cat.strip() for cat in categorias_busqueda]

        # Filtrar productos por género
        for producto in db:
            if (es_nina and producto.get('para_ninas')) or \
               (es_nino and producto.get('para_ninos')) or \
               (es_unisex and producto.get('unisex')):

                # Filtrar productos por categorías
                categorias = producto.get('categorias', [])
                if all(cat in categorias for cat in categorias_busqueda) or not categorias_busqueda:
                    results.append(producto)

    # Aplicar filtros adicionales
    if selected_brands or selected_colors or envio_gratis or envio_rapido or precio_min or precio_max:
        results = [product for product in results if
                   (not selected_brands or product['marca'] in selected_brands) and
                   (not selected_colors or product['color'] in selected_colors) and
                   (product['precio_producto'] >= precio_min and product['precio_producto'] <= precio_max) and
                   (not envio_gratis or product['envio_gratis']) and
                   (not envio_rapido or product['envio_rapido'])]

    # Ordenar los resultados según el criterio seleccionado
    if sort_by == 'precio_asc':
        results = sorted(results, key=lambda x: x['precio_producto'])
    elif sort_by == 'precio_desc':
        results = sorted(results, key=lambda x: x['precio_producto'], reverse=True)
    else:
        results = sorted(results, key=lambda x: fuzz.partial_ratio(x.get('nombre_producto', '').lower(), query), reverse=True)

    return render_template('/pages/buscador.html', query=query, results=results, selected_brands=selected_brands, selected_colors=selected_colors, precio_min=precio_min, precio_max=precio_max, envio_gratis=envio_gratis, envio_rapido=envio_rapido, sort_by=sort_by)

@app.route('/get_filters')
def get_filters():
    brands = list(set([producto['marca'] for producto in db]))
    colors = list(set([producto['color'] for producto in db]))
    return jsonify({'marcas': brands, 'colores': colors})

@app.route('/prueba')
def prueba():
    return render_template('/pages/zapatos.html')

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
