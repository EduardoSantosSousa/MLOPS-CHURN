from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Página inicial (com botão de login)
@app.route('/')
def index():
    return render_template('index.html')

# Página de login e acesso ao dashboard
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Validação simples
        if email == 'admin@teleconecta.com' and password == '1234':
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error='Credenciais inválidas')
    return redirect(url_for('index'))


# Página do dashboard após login
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    prediction = None

    if request.method == 'POST':
        client_id = request.form.get('client_id')
        months = int(request.form.get('months'))
        bill = float(request.form.get('bill'))

        # Lógica de predição fictícia
        if months < 6 or bill > 200:
            prediction = "🚨 Alta chance de cancelamento"
        else:
            prediction = "✅ Cliente estável"

    return render_template('dashboard.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)

