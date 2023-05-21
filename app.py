from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017')
db = client['boe-app']
collection = db['ox']

@app.route('/')
def index():
    # Consulta os documentos nos últimos 15 dias
    query = {"dataDiagnostico": {"$gte": "2023-05-05", "$lte": "2023-05-25"}}
    cursor = collection.find(query)

    # Converter os documentos em um DataFrame do pandas
    df = pd.DataFrame(list(cursor))

    # Converter a coluna "resultadoDiagnostico" para o tipo numérico
    df['resultadoDiagnostico'] = pd.to_numeric(df['resultadoDiagnostico'])

    # Filtrar os documentos com resultadoDiagnostico maior que 50
    df_positivos = df[df['resultadoDiagnostico'] > 50]

    # Filtrar os documentos com resultadoDiagnostico menor ou igual a 50
    df_negativos = df[df['resultadoDiagnostico'] <= 50]

    # Gerar dados do gráfico
    x_positivos = df_positivos['dataDiagnostico']
    y_positivos = df_positivos['resultadoDiagnostico']
    x_negativos = df_negativos['dataDiagnostico']
    y_negativos = df_negativos['resultadoDiagnostico']

    # Configurar o gráfico
    plt.style.use('classic')
    plt.rcParams['figure.facecolor'] = 'white'

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.set_title('Casos Positivos e Negativos', fontsize=16, fontweight='bold', fontstyle='italic')
    ax.plot(x_positivos, y_positivos, label='Positivos', color='green')
    ax.plot(x_negativos, y_negativos, label='Negativos', color='red')

    ax.set_xlim(min(df['dataDiagnostico']), max(df['dataDiagnostico']))
    ax.set_ylim(0, 100)

    ax.legend(fontsize=12, frameon=True, framealpha=0.5, facecolor='white')

    # Salvar o gráfico em um objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Codificar o gráfico em base64 para exibição na página
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return render_template('index.html', plot_data=plot_data)

if __name__ == '__main__':
    app.run()
