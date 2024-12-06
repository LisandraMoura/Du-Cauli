import os
import streamlit as st
from src.processa_audios import transcrever_audio
from src.gera_excel import formatar_transcricao_para_csv
import uuid
import shutil
from pydub import AudioSegment
import pandas as pd
import matplotlib.pyplot as plt

# Função para concatenar todos os áudios
def concatenar_audios(caminhos_audios, caminho_saida):
    print("[DEBUG] Concatenando áudios...")
    audio_final = AudioSegment.empty()
    
    for caminho in caminhos_audios:
        print(f"[DEBUG] Lendo áudio: {caminho}")
        audio = AudioSegment.from_file(caminho)
        audio_final += audio

    audio_final.export(caminho_saida, format="mp3")
    print(f"[DEBUG] Áudio concatenado salvo em: {caminho_saida}")

# Interface Streamlit
st.title("Processador de Áudios em Lote")

# Menu de navegação
opcao = st.selectbox("Escolha uma opção", ["Processar Áudio", "Analisar Dados"])

if opcao == "Processar Áudio":
    # Permitir upload de múltiplos arquivos
   
    arquivos = st.file_uploader(
        "Envie os arquivos de áudio (M4A, MP3 ou WAV)", 
        type=["m4a", "mp3", "wav"], 
        accept_multiple_files=True
    )
    st.write("Aceitamos áudios com os formatos M4A, MP3 e WAV.")

    if arquivos:
        # Criar pasta temporária para salvar os arquivos
        pasta_temporaria = "temp_audios"
        os.makedirs(pasta_temporaria, exist_ok=True)
        
        # Salvar arquivos localmente e exibir lista
        st.write("Arquivos carregados:")
        caminhos_audios = []
        for arquivo in arquivos:
            unique_name = f"{uuid.uuid4()}_{arquivo.name}"
            caminho_arquivo = os.path.join(pasta_temporaria, unique_name)
            with open(caminho_arquivo, "wb") as f:
                f.write(arquivo.read())
            caminhos_audios.append(caminho_arquivo)
            st.write(f"✅ {unique_name}")

        # Concatenar todos os áudios em um único arquivo automaticamente
        st.write("🔄 Concatenando os arquivos de áudio...")
        caminho_audio_concatenado = os.path.join("dados_transcritos", "audio_concatenado.mp3")
        os.makedirs("dados_transcritos", exist_ok=True)
        concatenar_audios(caminhos_audios, caminho_audio_concatenado)
        st.success(f"Áudio concatenado salvo em {caminho_audio_concatenado}.")
        
        # Botão para processar o áudio concatenado
        if st.button("Processar Áudio Concatenado"):
            st.write("🔄 Processando o áudio concatenado...")

            try:
                transcricao = transcrever_audio(caminho_audio_concatenado)
                st.write("📝 Transcrição do áudio concatenado:")
                st.text_area("", transcricao, height=200)
                
                # Formatar transcrição em CSV
                caminho_csv = os.path.join("dados_transcritos", "transcricao_concatenado.csv")
                formatar_transcricao_para_csv(transcricao, caminho_csv)
                st.success(f"Transcrição formatada e salva em CSV: {caminho_csv}")
                
                # Botão para download do CSV
                with open(caminho_csv, "rb") as f:
                    st.download_button(
                        label="Baixar CSV",
                        data=f,
                        file_name="transcricao_concatenado.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Erro ao processar o áudio concatenado: {e}")
                print(f"[ERROR] Erro ao processar o áudio concatenado: {e}")

            # Limpar pasta temporária
            if os.path.exists(pasta_temporaria):
                shutil.rmtree(pasta_temporaria)
                st.write("🧹 Pasta temporária limpa com sucesso.")

elif opcao == "Analisar Dados":
    st.write("### Faça o upload do CSV gerado para análise dos dados ou use o arquivo gerado anteriormente")
    opcao_csv = st.radio("Como você deseja fornecer o CSV?", ["Upload de Arquivo", "Usar Caminho Existente"])

    if opcao_csv == "Upload de Arquivo":
        arquivo_csv = st.file_uploader("Envie o arquivo CSV", type=["csv"])
        if arquivo_csv is not None:
            df = pd.read_csv(arquivo_csv)
    elif opcao_csv == "Usar Caminho Existente":
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
