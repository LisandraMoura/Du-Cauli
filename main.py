import os
import shutil
import uuid
import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pydub import AudioSegment
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaIoBaseDownload
from src.processa_audios import transcrever_audio
from src.gera_excel import formatar_transcricao_para_csv
import ssl
import certifi

# Configuração de SSL
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

google_credentials = st.secrets["GOOGLE_CREDENTIALS"]
# Transformar em dicionário, se necessário
google_credentials_dict = dict(google_credentials)

GOOGLE_DRIVE_FOLDER_ID = '14Qoy_hf7r6Qh2Rwng97pYMcFu7rf3eqY'


## LOCAL ##
# # Configurações do Google Drive
# CREDENTIALS_FILE = 'pdm-class-2024-ba9afd8b5e2d.json'
# SCOPES = ['https://www.googleapis.com/auth/drive']

# @st.cache_resource
# def create_drive_service():
#     """Cria o serviço para conectar ao Google Drive."""
#     try:
#         credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
#         service = build('drive', 'v3', credentials=credentials)
#         return service
#     except Exception as e:
#         st.error(f"Erro ao conectar ao Google Drive: {e}")
#         return None
    
@st.cache_resource
def create_drive_service():
    """Cria o serviço para conectar ao Google Drive."""
    try:
        # Usar as credenciais do dicionário
        credentials = Credentials.from_service_account_info(google_credentials_dict)
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Drive: {e}")
        return None

def list_files_in_folder(service, folder_id):
    """Lista os arquivos em uma pasta específica do Google Drive."""
    try:
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])
    except Exception as e:
        st.error(f"Erro ao listar arquivos na pasta: {e}")
        return []

def download_file(service, file_id, destination):
    """Baixa um arquivo do Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        with open(destination, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return destination
    except Exception as e:
        st.error(f"Erro ao baixar arquivo: {e}")
        return None

# Criar serviço do Google Drive
service = create_drive_service()

# Interface Streamlit
st.title("Du-CauLi Assistente de Voz")

st.write("Imagine substituir o caderninho amassado e as planilhas manuais por uma solução simples, rápida e escalável: um assistente de áudio para pesquisadores de campo. Com nosso dispositivo IoT, basta gravar suas observações em áudio, mesmo sem conexão. Assim que você estiver online, nossa tecnologia converte automaticamente esses áudios em planilhas digitais completas, com todas as variáveis já organizadas. É menos tempo perdido com transcrição manual e mais foco no que realmente importa: a pesquisa. Onde houver alguém coletando dados — na cidade, no cerrado ou no deserto — nossa solução se adapta e agiliza o trabalho.")
st.write("##### Bem-vindo a um futuro de coleta de dados em campo mais ágil, inteligente e sem complicações.")


# Menu de navegação
opcao = st.selectbox("Lista de ferramentas disponíveis: ", ["Processador de áudio", "Análise de dados"])

if opcao == "Processador de áudio":
    # Upload de arquivos locais
    st.write("### Arquivos Locais")
    arquivos_locais = st.file_uploader(
        "Selecione os arquivos de áudio locais", 
        type=["m4a", "mp3", "wav"], 
        accept_multiple_files=True
    )

    # Seleção de arquivos do Google Drive
    arquivos_drive = []
    if service:
        st.write("### Arquivos Remotos")
        arquivos_drive_disponiveis = list_files_in_folder(service, GOOGLE_DRIVE_FOLDER_ID)
        arquivos_drive = st.multiselect(
            "Selecione os arquivos de áudio do Google Drive:",
            arquivos_drive_disponiveis,
            format_func=lambda x: x['name']
        )
        baixar_todos = st.checkbox("Selecionar todos os arquivos da pasta")

    # Processar arquivos selecionados
    if st.button("Gerar Planilha"):
        if not arquivos_locais and not arquivos_drive and not baixar_todos:
            st.error("Por favor, envie arquivos locais ou selecione arquivos do Google Drive.")
        else:
            # Criar pasta temporária
            pasta_temporaria = "temp_audios"
            os.makedirs(pasta_temporaria, exist_ok=True)
            caminhos_audios = []

            # Salvar arquivos locais
            if arquivos_locais:
                count0 = 0
                st.write("### Processando arquivos locais...")
                for arquivo in arquivos_locais:
                    unique_name = f"{uuid.uuid4()}_{arquivo.name}"
                    caminho_arquivo = os.path.join(pasta_temporaria, unique_name)
                    with open(caminho_arquivo, "wb") as f:
                        f.write(arquivo.read())
                    caminhos_audios.append(caminho_arquivo)
                    count0 += 1
                    # st.write(f"✅ Arquivo local salvo: {unique_name}")
                st.write(f"✅ Total áudios salvos: {count0}")

            # Baixar todos os arquivos da pasta do Google Drive
            if baixar_todos:
                count = 0
                st.write("### Processando arquivos remotos...")
                for arquivo in arquivos_drive_disponiveis:
                    destino = os.path.join(pasta_temporaria, arquivo['name'])
                    caminho_arquivo = download_file(service, arquivo['id'], destino)
                    if caminho_arquivo:
                        caminhos_audios.append(caminho_arquivo)
                        count += 1
                        # st.write(f"✅ Arquivo baixado do Google Drive: {arquivo['name']}")
                st.write(f"✅ Total áudios salvos: {count}")


            # Baixar arquivos do Google Drive
            if arquivos_drive and not baixar_todos:
                count2 = 0
                st.write("### Processando arquivos remotos...")
                for arquivo in arquivos_drive:
                    destino = os.path.join(pasta_temporaria, arquivo['name'])
                    caminho_arquivo = download_file(service, arquivo['id'], destino)
                    if caminho_arquivo:
                        caminhos_audios.append(caminho_arquivo)
                        count2 += 1
                        # st.write(f"✅ Arquivo baixado do Google Drive: {arquivo['name']}")
                st.write(f"✅ Total áudios salvos: {count2}")

            # Concatenar todos os áudios
            if caminhos_audios:
                st.write("🔄 Gerando...")
                caminho_audio_concatenado = os.path.join("dados_transcritos", "audio_concatenado.mp3")
                os.makedirs("dados_transcritos", exist_ok=True)
                audio_final = AudioSegment.empty()
                for caminho in caminhos_audios:
                    audio = AudioSegment.from_file(caminho)
                    audio_final += audio
                audio_final.export(caminho_audio_concatenado, format="mp3")
                st.success(f"Áudio concatenado!")

                # Processar o áudio concatenado
                try:
                    st.write("🔄 Transcrevendo o áudio...")
                    transcricao = transcrever_audio(caminho_audio_concatenado)
                    st.text_area("📝 Transcrição:", transcricao, height=200)

                    # Salvar transcrição como CSV
                    caminho_csv = os.path.join("dados_transcritos", "transcricao_concatenado.csv")
                    formatar_transcricao_para_csv(transcricao, caminho_csv)
                    # st.success(f"Transcrição salva em CSV: {caminho_csv}")
                    st.success(f"CSV gerado com sucesso! Agora, basta baixar o csv ou visualizar os dados em 'Análise de dados'.")

                    # Botão para download do CSV
                    with open(caminho_csv, "rb") as f:
                        st.download_button(
                            label="Baixar CSV",
                            data=f,
                            file_name="transcricao_concatenado.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Erro ao processar o áudio: {e}")

            # Limpar pasta temporária
            shutil.rmtree(pasta_temporaria)
            st.write("🧹 Pasta temporária limpa.")

elif opcao == "Análise de dados":
    st.write("### Faça o upload do CSV gerado para análise dos dados ou use o arquivo gerado anteriormente")
    opcao_csv = st.radio("Como você deseja fornecer o CSV?", ["Upload de Arquivo", "CSV gerado"])

    if opcao_csv == "Upload de Arquivo":
        arquivo_csv = st.file_uploader("Envie o arquivo CSV", type=["csv"])
        if arquivo_csv is not None:
            df = pd.read_csv(arquivo_csv)
    elif opcao_csv == "CSV gerado":
        caminho_csv_existente = os.path.join("dados_transcritos", "transcricao_concatenado.csv")
        if os.path.exists(caminho_csv_existente):
            df = pd.read_csv(caminho_csv_existente)
            st.success(f"Usando o arquivo existente: {caminho_csv_existente}")
        else:
            st.error("Erro: Arquivo CSV não encontrado. Primeiro, processe o áudio para gerar o CSV.")
            df = None

    if 'df' in locals() and df is not None:
        st.write("### Dados Extraídos")
        st.dataframe(df)

        # Gráfico 1: Histograma das Alturas
        st.write("### Distribuição das Alturas")
        plt.figure()
        plt.hist(df['altura'].astype(float), bins=10, edgecolor='black')
        plt.xlabel('Altura')
        plt.ylabel('Frequência')
        plt.title('Histograma das Alturas')
        st.pyplot(plt)

        # Gráfico 2: Histograma dos Diâmetros
        st.write("### Distribuição dos Diâmetros")
        plt.figure()
        plt.hist(df['diâmetro'].astype(float), bins=10, edgecolor='black')
        plt.xlabel('Diâmetro')
        plt.ylabel('Frequência')
        plt.title('Histograma dos Diâmetros')
        st.pyplot(plt)

        # Gráfico 3: Gráfico de Dispersão entre Altura e Diâmetro
        st.write("### Relação entre Altura e Diâmetro")
        plt.figure()
        plt.scatter(df['altura'].astype(float), df['diâmetro'].astype(float))
        plt.xlabel('Altura')
        plt.ylabel('Diâmetro')
        plt.title('Gráfico de Dispersão entre Altura e Diâmetro')
        st.pyplot(plt)
