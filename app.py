
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

    # Obter a data atual
    data_atual = datetime.now().date()

    # Função para converter a data em uma string formatada
    def formatar_data(data):
        return data.strftime('%Y-%m-%d')

    # Converter a data para string antes de criar o DataFrame
    documentos = []
    for document in cursor_15dias:
        item = {}
        for key, value in document.items():
            if key == "data" and isinstance(value, datetime.date):
                # Converter o objeto datetime.date para uma string formatada
                value = formatar_data(value)
            item[key] = value
        documentos.append(item)

    # Calcular as datas de início e fim para cada período
    periodo_15dias_inicio = data_atual - timedelta(days=15)
    periodo_15dias_fim = data_atual
    periodo_1mes_inicio = data_atual - timedelta(days=30)
    periodo_1mes_fim = data_atual
    periodo_6meses_inicio = data_atual - timedelta(days=180)
    periodo_6meses_fim = data_atual
    periodo_1ano_inicio = data_atual - timedelta(days=365)
    periodo_1ano_fim = data_atual

    # Consultar os documentos dentro de cada período
    query_15dias = {"dataDiagnostico": {"$gte": periodo_15dias_inicio, "$lte": periodo_15dias_fim}}
    query_1mes = {"dataDiagnostico": {"$gte": periodo_1mes_inicio, "$lte": periodo_1mes_fim}}
    query_6meses = {"dataDiagnostico": {"$gte": periodo_6meses_inicio, "$lte": periodo_6meses_fim}}
    query_1ano = {"dataDiagnostico": {"$gte": periodo_1ano_inicio, "$lte": periodo_1ano_fim}}

    cursor_15dias = collection.find(query_15dias)
    cursor_1mes = collection.find(query_1mes)
    cursor_6meses = collection.find(query_6meses)
    cursor_1ano = collection.find(query_1ano)

    # Converter os documentos em DataFrames do pandas
    df_15dias = pd.DataFrame(documentos)
    df_1mes = pd.DataFrame(list(cursor_1mes))
    df_6meses = pd.DataFrame(list(cursor_6meses))
    df_1ano = pd.DataFrame(list(cursor_1ano))

    # Converter a coluna "resultadoDiagnostico" para o tipo numérico
    df_15dias['resultadoDiagnostico'] = pd.to_numeric(df_15dias['resultadoDiagnostico'])
    df_1mes['resultadoDiagnostico'] = pd.to_numeric(df_1mes['resultadoDiagnostico'])
    df_6meses['resultadoDiagnostico'] = pd.to_numeric(df_6meses['resultadoDiagnostico'])
    df_1ano['resultadoDiagnostico'] = pd.to_numeric(df_1ano['resultadoDiagnostico'])

    # Filtrar os documentos com resultadoDiagnostico maior que 50 para cada período
    df_positivos_15dias = df_15dias[df_15dias['resultadoDiagnostico'] > 50]
    df_positivos_1mes = df_1mes[df_1mes['resultadoDiagnostico'] > 50]
    df_positivos_6meses = df_6meses[df_6meses['resultadoDiagnostico'] > 50]
    df_positivos_1ano = df_1ano[df_1ano['resultadoDiagnostico'] > 50]

    # Criar os gráficos para cada período
    fig, ax = plt.subplots(2, 2, figsize=(7, 5))
    ax[0, 0].plot(df_15dias['dataDiagnostico'], df_15dias['resultadoDiagnostico'])
    ax[0, 0].set_title('Últimos 15 dias')
    ax[0, 1].plot(df_1mes['dataDiagnostico'], df_1mes['resultadoDiagnostico'])
    ax[0, 1].set_title('Último mês')
    ax[1, 0].plot(df_6meses['dataDiagnostico'], df_6meses['resultadoDiagnostico'])
    ax[1, 0].set_title('Últimos 6 meses')
    ax[1, 1].plot(df_1ano['dataDiagnostico'], df_1ano['resultadoDiagnostico'])
    ax[1, 1].set_title('Último ano')

    # Configurar o gráfico
    plt.style.use('classic')
    plt.rcParams['figure.facecolor'] = 'white'

    # Salvar o gráfico em um objeto BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Codificar o gráfico em base64 para exibição na página
    plot_data = base64.b64encode(buffer.getvalue()).decode()

    return render_template('index.html', plot_data=plot_data)

if __name__ == '__main__':
    app.run()

