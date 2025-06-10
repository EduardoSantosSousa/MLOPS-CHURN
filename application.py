from flask import Flask, render_template, request, redirect, url_for
import os
import joblib
import pandas as pd

# Caminhos do modelo e encoder
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENCODER_PATH = os.path.join(PROJECT_ROOT, 'artifacts', 'encoders', 'label_encoders.pkl')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'artifacts', 'model', 'best_random_forest.pkl')

# Carrega modelo e encoders
model = joblib.load(MODEL_PATH)
encoders = joblib.load(ENCODER_PATH)

FEATURES_PATH = os.path.join(PROJECT_ROOT, 'artifacts', 'model', 'feature_columns.pkl')

# Carrega colunas usadas no treinamento
with open(FEATURES_PATH, 'rb') as f:
    trained_feature_columns = joblib.load(f)


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


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    prediction = None
    calculated_fields = {}

    if request.method == 'POST':
        input_data = {}
        # Separe campos numéricos e categóricos
        numeric_fields = ['tenure', 'MonthlyCharges', 'TotalCharges', 'AvgMonthlySpend']
        categorical_fields = [
            'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
            'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
            'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
            'PaperlessBilling', 'PaymentMethod'
        ]

        # Processa campos numéricos
        for feature in numeric_fields:
            value = request.form.get(feature)
            if value:
                input_data[feature] = float(value) if '.' in value else int(value)
            else:
                input_data[feature] = 0.0  # Valor padrão

        # Processa campos categóricos (mantém como string)
        for feature in categorical_fields:
            input_data[feature] = request.form.get(feature)

        # Mapeamentos diretos (agora usando strings do formulário)
        map_internet_service = {
            'DSL': 'DSL',
            'Fiber Optic': 'Fiber optic',
            'No': 'No internet service'
        }
        
        map_yes_no = {
            'No': 'No',
            'Yes': 'Yes',
            'No internet service': 'No internet service',
            'Sem serviço de telefone': 'No internet service',
            'Sem serviço de internet': 'No internet service'
        }

        # Dados convertidos para lógica de cálculos
        logic_data = {
            'OnlineSecurity': map_yes_no.get(input_data['OnlineSecurity'], 'No'),
            'OnlineBackup': map_yes_no.get(input_data['OnlineBackup'], 'No'),
            'DeviceProtection': map_yes_no.get(input_data['DeviceProtection'], 'No'),
            'TechSupport': map_yes_no.get(input_data['TechSupport'], 'No'),
            'StreamingTV': map_yes_no.get(input_data['StreamingTV'], 'No'),
            'StreamingMovies': map_yes_no.get(input_data['StreamingMovies'], 'No'),
            'PhoneService': map_yes_no.get(input_data['PhoneService'], 'No'),
            'MultipleLines': map_yes_no.get(input_data['MultipleLines'], 'No'),
            'InternetService': map_internet_service.get(input_data['InternetService'], 'No'),
            'Contract': input_data['Contract'],
            'PaymentMethod': input_data['PaymentMethod'],
            'tenure': input_data['tenure']
        }

        # Cálculo dos campos derivados
        no_online_services = sum([
            logic_data['OnlineSecurity'] == 'No',
            logic_data['OnlineBackup'] == 'No',
            logic_data['DeviceProtection'] == 'No',
            logic_data['TechSupport'] == 'No'
        ])

        no_streaming = sum([
            logic_data['StreamingTV'] == 'No',
            logic_data['StreamingMovies'] == 'No'
        ])

        total_services = 0
        for col in ['PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
                    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
            value = logic_data[col]
            if value in ['Yes', 'Fiber optic', 'DSL']:
                total_services += 1

        risk_score = sum([
            logic_data['Contract'] == 'Month-to-month',
            logic_data['OnlineSecurity'] == 'No',
            logic_data['TechSupport'] == 'No',
            logic_data['PaymentMethod'] == 'Electronic check',
            logic_data['tenure'] < 6
        ])

        # Salvar campos calculados
        calculated_fields = {
            'NoOnlineServices': no_online_services,
            'NoStreaming': no_streaming,
            'TotalServices': total_services,
            'RiskScore': risk_score
        }

        # Adiciona campos calculados
        input_data.update(calculated_fields)

        # Converte para DataFrame
        df = pd.DataFrame([input_data])

        # Codificação
        for col, encoder in encoders.items():
            if col in df.columns and col != 'Churn':
                # Converte valores desconhecidos para o mais frequente
                unknown_values = ~df[col].isin(encoder.classes_)
                if unknown_values.any():
                    most_frequent = encoder.classes_[0]
                    df.loc[unknown_values, col] = most_frequent
                df[col] = encoder.transform(df[col])

        # Predição
        # Garante que o DataFrame tenha todas as colunas do treinamento
        missing_cols = set(trained_feature_columns) - set(df.columns)
        for col in missing_cols:
            df[col] = 0  # Valor padrão para colunas ausentes
        # Remove colunas que não foram usadas no treinamento
        extra_cols = set(df.columns) - set(trained_feature_columns)
        df.drop(columns=extra_cols, inplace=True)

        # Reordena colunas na mesma ordem do treinamento
        df = df[trained_feature_columns]

        #Predição:
        result = model.predict(df)[0]
        prediction = "🚨 Alta chance de cancelamento" if result == 1 else "✅ Cliente estável"

    return render_template('dashboard.html', prediction=prediction, calculated=calculated_fields)

if __name__ == '__main__':
    app.run(debug=True)

