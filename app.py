from flask import Flask, render_template, request, flash, redirect, url_for
import json

app = Flask(__name__)
app.secret_key = 'colegio_secreto_2024'

def cargar_noticias():
    with open('noticias.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        noticias = sorted(data['noticias'], key=lambda x: x['fecha'], reverse=True)
        return noticias

@app.route('/')
@app.route('/inicio')
def inicio():
    noticias = cargar_noticias()[:3]
    return render_template('inicio.html', noticias=noticias)

@app.route('/niveles')
def niveles():
    return render_template('niveles.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/docentes')
def docentes():
    return render_template('docentes.html')

@app.route('/documentos')
def documentos():
    return render_template('documentos.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_padre = request.form.get('nombre_padre')
        nombre_alumno = request.form.get('nombre_alumno')
        flash(f'Gracias {nombre_padre}, hemos recibido tu solicitud para {nombre_alumno}.', 'success')
        return redirect(url_for('registro'))
    return render_template('registro.html')

@app.route('/noticias')
def noticias():
    todas_noticias = cargar_noticias()
    return render_template('noticias.html', noticias=todas_noticias)

if __name__ == '__main__':
    app.run(debug=True, port=8000)