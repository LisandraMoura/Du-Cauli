# # processa_audios.py
# import openai
# from dotenv import load_dotenv
# import os

# # Carregar a chave de API do arquivo .env
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def transcrever_audio(caminho_audio):
#     """
#     Transcreve um arquivo de áudio utilizando a API da OpenAI.
#     """
#     print(f"[DEBUG] Transcrevendo áudio: {caminho_audio}")
#     try:
#         with open(caminho_audio, "rb") as audio_file:
#             transcricao = openai.Audio.transcribe(
#                 model="whisper-1",
#                 file=audio_file
#             )
#         print(f"[DEBUG] Transcrição concluída. Texto: {transcricao['text']}")
#         return transcricao["text"]
#     except Exception as e:
#         print(f"[ERROR] Erro ao transcrever áudio: {e}")
#         raise e

# if __name__ == "__main__":
#     caminho = "../data/IoT 2.m4a"
#     texto_transcrito = transcrever_audio(caminho)
#     print(texto_transcrito)

# funciona ##3


# processa_audios.py
import openai
from dotenv import load_dotenv
import os

# Carregar a chave de API do arquivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def transcrever_audio(caminho_audio):
    """
    Transcreve um arquivo de áudio utilizando a API da OpenAI.
    """
    print(f"[DEBUG] Transcrevendo áudio: {caminho_audio}")
    try:
        with open(caminho_audio, "rb") as audio_file:
            transcricao = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
            
        print(f"[DEBUG] Transcrição concluída. Texto: {transcricao['text']}")
        return transcricao["text"]
    except Exception as e:
        print(f"[ERROR] Erro ao transcrever áudio: {e}")
        raise e