from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    # Conectar ao banco de dados MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['database_name']
    collection = db['collection_name']

    # Obter a data atual
    current_date = datetime.now()

    # Calcular as datas de início e fim para cada período
    date_15dias_ago = current_date - timedelta(days=15)
    date_1mes_ago = current_date - timedelta(days=30)
    date_6meses_ago = current_date - timedelta(days=180)
    date_1ano_ago = current_date - timedelta(days=365)

    # Consultar os documentos do banco de dados dentro de cada período
    df_15dias = pd.DataFrame(list(collection.find({'dataDiagnostico': {'$gte': date_15dias_ago, '$lte': current_date}})))
    df_1mes = pd.DataFrame(list(collection.find({'dataDiagnostico': {'$gte': date_1mes_ago, '$lte': current_date}})))
    df_6meses = pd.DataFrame(list(collection.find({'dataDiagnostico': {'$gte': date_6meses_ago, '$lte': current_date}})))
    df_1ano = pd.DataFrame(list(collection.find({'dataDiagnostico': {'$gte': date_1ano_ago, '$lte': current_date}})))

    # Filtrar os documentos com resultadoDiagnostico maior que 50 para cada período
    df_positivos_15dias = df_15dias[df_15dias['resultadoDiagnostico'] > 50]
    df_positivos_1mes = df_1mes[df_1mes['resultadoDiagnostico'] > 50]
    df_positivos_6meses = df_6meses[df_6meses['resultadoDiagnostico'] > 50]
    df_positivos_1ano = df_1ano[df_1ano['resultadoDiagnostico'] > 50]

    # Criar os gráficos para cada período
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes[0, 0].plot(df_15dias['dataDiagnostico'], df_15dias['resultadoDiagnostico'])
    axes[0, 0].set_title('Últimos 15 dias')
    axes[0, 1].plot(df_1mes['dataDiagnostico'], df_1mes['resultadoDiagnostico'])
    axes[0, 1].set_title('Último mês')
    axes[1, 0].plot(df_6meses['dataDiagnostico'], df_6meses['resultadoDiagnostico'])
    axes[1, 0].set_title('Últimos 6 meses')
    axes[1, 1].plot(df_1ano['dataDiagnostico'], df_1ano['resultadoDiagnostico'])
    axes[1, 1].set_title('Último ano')

    # Converter o gráfico em uma imagem para exibição na página
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Converter a imagem em formato base64 para exibição na página
    graph = base64.b64encode(image_png).decode('utf-8')

    # Renderizar o template HTML e passar o gráfico codificado em base64 como argumento
    return render_template('index.html', graph=graph)

if __name__ == '__main__':
    app.run(debug=True)
