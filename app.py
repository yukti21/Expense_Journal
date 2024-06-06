from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('transactions.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()

# Initialize the database if not exists
init_db()

# Route to display all transactions (expenses and income)
@app.route('/')
def index():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions').fetchall()
    total_expense = sum(transaction['amount'] for transaction in transactions if transaction['type'] == 'expense')
    total_income = sum(transaction['amount'] for transaction in transactions if transaction['type'] == 'income')
    balance = total_income - total_expense

    return render_template('index.html', transactions=transactions, total_expense=total_expense,
                           total_income=total_income, balance=balance)


# Route to add a new transaction (expense or income)
@app.route('/add', methods=['POST'])
def add():
    description = request.form['description']
    amount = request.form['amount']
    type = request.form['type']

    conn = get_db_connection()
    conn.execute('INSERT INTO transactions (description, amount, type) VALUES (?, ?, ?)', (description, amount, type))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Route to delete a transaction
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route to edit a transaction
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        type = request.form['type']
        conn.execute('UPDATE transactions SET description = ?, amount = ?, type = ? WHERE id = ?', (description, amount, type, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        transaction = conn.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
        conn.close()
        return render_template('edit.html', transaction=transaction)

if __name__ == '__main__':
    app.run(debug=True)
