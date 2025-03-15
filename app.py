from flask import Flask, render_template, redirect, url_for, request, session, flash
import logging
import psycopg2
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG)

# Configuração do banco de dados
DB_HOST = '192.168.100.100'
DB_NAME = 'sentinel'
DB_USER = 'andrino'
DB_PASS = 'Rebecca@2023'

# Função para obter a senha hasheada do banco de dados
def get_hashed_password(username):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Retorna a senha hasheada
        return None
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_user(username, password):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = connection.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
    except Exception as e:
        logging.error(f"Erro ao criar usuário no banco de dados: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def remove_user(username):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        connection.commit()
    except Exception as e:
        logging.error(f"Erro ao remover usuário no banco de dados: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def change_password(username, new_password):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = connection.cursor()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
        connection.commit()
    except Exception as e:
        logging.error(f"Erro ao alterar a senha no banco de dados: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        logging.debug(f"Tentativa de login com username: {username}")
        hashed_password = get_hashed_password(username)
        logging.debug(f"Senha hasheada recuperada: {hashed_password}")
        if hashed_password:
            try:
                if bcrypt.checkpw(password, hashed_password.encode('utf-8')):
                    session['username'] = username
                    logging.debug(f"Login bem-sucedido para usuário: {username}")
                    return redirect(url_for('dashboard'))
                else:
                    logging.warning(f"Senha incorreta para usuário: {username}")
                    flash('Login Failed. Please check your username and password.', 'error')
            except ValueError as ve:
                logging.error(f"Erro ao verificar a senha: {ve}")
                flash('Internal error. Please try again later.', 'error')
        else:
            logging.warning(f"Usuário {username} não encontrado.")
            flash('Login Failed. Please check your username and password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user(username, password)
        flash('User registered successfully.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/remove_user', methods=['POST'])
def remove_user_route():
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    hashed_password = get_hashed_password(username)
    if hashed_password and bcrypt.checkpw(password, hashed_password.encode('utf-8')):
        remove_user(username)
        flash('User removed successfully.', 'success')
    else:
        flash('Failed to remove user. Please check your username and password.', 'error')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
def change_password_route():
    username = request.form['username']
    current_password = request.form['current_password'].encode('utf-8')
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    hashed_password = get_hashed_password(username)
    if hashed_password and bcrypt.checkpw(current_password, hashed_password.encode('utf-8')):
        if new_password == confirm_new_password:
            change_password(username, new_password)
            flash('Password changed successfully.', 'success')
        else:
            flash('New passwords do not match.', 'error')
    else:
        flash('Failed to change password. Please check your username and current password.', 'error')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
