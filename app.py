from flask import Flask, render_template, redirect, url_for, request, session, flash
import logging
import psycopg2
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

logging.basicConfig(level=logging.DEBUG)

DB_HOST = '192.168.100.100'
DB_NAME = 'sentinel'
DB_USER = 'andrino'
DB_PASS = 'Rebecca@2023'

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def get_hashed_password(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return bytes(result[0]) if result else None

def create_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def remove_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
    affected_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected_rows > 0

def change_password(username, new_password):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, username))
    affected_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected_rows > 0

def add_expense(username, date, description, amount, category, recurring, start_date=None, end_date=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO expenses (username, date, description, amount, category, recurring, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (username, date, description, amount, category, recurring, start_date, end_date)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao adicionar despesa: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_recent_expenses(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date, description, amount, category, recurring
        FROM expenses
        WHERE username = %s
        ORDER BY date DESC
        LIMIT 10
        """,
        (username,)
    )
    expenses = cur.fetchall()
    cur.close()
    conn.close()
    return expenses

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed = get_hashed_password(username)
        if hashed and bcrypt.checkpw(password, hashed):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('As senhas não coincidem', 'error')
        elif create_user(username, password):
            flash('Usuário registrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Nome de usuário já existe', 'error')
    return render_template('register.html')

@app.route('/remove_user', methods=['POST'])
def remove_user_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    hashed = get_hashed_password(username)
    if hashed and bcrypt.checkpw(password, hashed):
        if remove_user(username):
            if session['username'] == username:
                session.pop('username', None)
            flash('Usuário removido com sucesso', 'success')
        else:
            flash('Usuário não encontrado', 'error')
    else:
        flash('Credenciais inválidas', 'error')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
def change_password_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = request.form['username']
    current_password = request.form['current_password'].encode('utf-8')
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    hashed = get_hashed_password(username)
    if not hashed or not bcrypt.checkpw(current_password, hashed):
        flash('Credenciais inválidas', 'error')
    elif new_password != confirm_new_password:
        flash('As novas senhas não coincidem', 'error')
    elif change_password(username, new_password):
        flash('Senha alterada com sucesso', 'success')
    else:
        flash('Erro ao alterar a senha', 'error')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/despesas', methods=['GET', 'POST'])
def despesas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if request.method == 'POST':
        date = request.form['data']
        description = request.form['descricao']
        amount = float(request.form['valor'].replace('R$', '').replace('.', '').replace(',', '.').strip())
        category = request.form['tipo']
        recurring = 'recorrente' in request.form
        start_date = request.form.get('data_inicio') if recurring else None
        end_date = request.form.get('data_fim') if recurring else None
        
        if add_expense(username, date, description, amount, category, recurring, start_date, end_date):
            flash('Despesa adicionada com sucesso!', 'success')
        else:
            flash('Erro ao adicionar despesa.', 'error')
        return redirect(url_for('despesas'))
    
    expenses = get_recent_expenses(username)
    return render_template('despesas.html', expenses=expenses)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
