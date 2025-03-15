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

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        # Substitua essas linhas pelos dados reais do seu banco de dados
        total_earnings = 1000.00
        total_expenses = 500.00
        goals = [
            {"id": 1, "description": "Meta 1", "deadline": datetime.strptime("2025-12-31", "%Y-%m-%d"), "progress": 50, "current_amount": 500, "target_amount": 1000},
            {"id": 2, "description": "Meta 2", "deadline": datetime.strptime("2025-06-30", "%Y-%m-%d"), "progress": 30, "current_amount": 300, "target_amount": 1000},
        ]
        transactions = [
            {"description": "Compra 1", "category": "Alimentação", "date": datetime.strptime("2025-03-01", "%Y-%m-%d"), "amount": -50.00},
            {"description": "Salário", "category": "Renda", "date": datetime.strptime("2025-03-01", "%Y-%m-%d"), "amount": 1500.00},
        ]
        return render_template('dashboard.html', total_earnings=total_earnings, total_expenses=total_expenses, goals=goals, transactions=transactions)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_expense')
def add_expense():
    # Lógica para adicionar despesas
    return "Adicionar Despesas"

@app.route('/add_earning')
def add_earning():
    # Lógica para adicionar ganhos
    return "Adicionar Ganhos"

@app.route('/add_goal')
def add_goal():
    # Lógica para adicionar metas
    return "Adicionar Metas"

@app.route('/update_goal/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    # Lógica para atualizar metas
    return f"Meta {goal_id} atualizada"

@app.route('/earnings_vs_expenses')
def earnings_vs_expenses():
    # Lógica para o gráfico de Ganhos vs Despesas
    return "Gráfico de Ganhos vs Despesas"

@app.route('/expenses_distribution')
def expenses_distribution():
    # Lógica para o gráfico de Distribuição de Despesas
    return "Gráfico de Distribuição de Despesas"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
