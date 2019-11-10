#!/usr/bin/env python
import csv
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, session,request
from flask_bootstrap import Bootstrap
from forms import LoginForm, SaludarForm, RegistrarForm


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'un string que funcione como llave'
#bloque de difincion de abrir el archivo csv que lo lee lo guarde en una lista y lo retone
def listaCSV():
    with open('clientes.csv','r', encoding="utf-8") as cliente: 
        leearh = csv.reader(cliente)
        archlist = list(leearh)
    return archlist

@app.route('/')
def index():
    
    return render_template('index.html', fecha_actual=datetime.utcnow())


@app.route('/saludar', methods=['GET', 'POST'])
def saludar():
    formulario = SaludarForm()
    if formulario.validate_on_submit():  # Acá hice el POST si es True
        print(formulario.usuario.name)
        return redirect(url_for('saludar_persona', usuario=formulario.usuario.data))
    return render_template('saludar.html', form=formulario)


@app.route('/saludar/<usuario>')
def saludar_persona(usuario):
    return render_template('usuarios.html', nombre=usuario)


@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404

@app.route('/about',methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    session['username'] = formulario.usuario.data
                    return render_template('ingresado.html', username=session['username'])
                registro = next(archivo_csv, None)
            else: #se agrego un else de qe si no esta conectado lo redireccione a ingresar
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)
#Bloque de Clientes cree una ruta para el nuevo html que se muestra si estas logiado si no te redirecciona a sin permiso
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'username' in session:
        Cli= listaCSV()
        username = session['username']
        return render_template('clientes.html',username=session['username'],misventas=Cli)
    else:
        return render_template('sin_permiso.html')


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        #Comienzo a tocar
        Existe= False
        with open('usuarios') as archivo:
            archivo_csv2 = csv.reader(archivo)
            registro2 = next(archivo_csv2)
            while registro2 and Existe==False:
                if formulario.usuario.data == registro2[0]:
                    flash('El usuario ya esta en uso.')
                    Existe=True
                registro2 = next(archivo_csv2, None)
        #Termine de tocar
        if Existe ==False:
            if formulario.password.data == formulario.password_check.data:

                with open('usuarios', 'a+', newline='') as archivo:
                    archivo_csv = csv.writer(archivo)
                    registro = [formulario.usuario.data, formulario.password.data]
                    archivo_csv.writerow(registro)
                flash('Usuario creado correctamente')
                return redirect(url_for('ingresar'))
            else:
                flash('Las passwords no matchean')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
