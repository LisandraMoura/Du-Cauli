# gera_excel.py
import os
from src.processa_audios import transcrever_audio  # Importa a função do outro arquivo
import openai

def formatar_transcricao_para_csv(transcricao, caminho_csv):
    """
    Usa um modelo de linguagem para formatar a transcrição em CSV e salva no caminho especificado.
    """
    print(f"[DEBUG] Formatando transcrição para CSV com LLM.")
    try:
        prompt = f"""
        A seguinte transcrição de áudio contém dados estruturados de medições. 
        Reformate o texto abaixo em uma tabela CSV com as seguintes colunas:
        - ID
        - L = Lote
        - altura
        - diâmetro
        Gere apenas a tabela com os dados, sem a parte da transcrição.
        Quero apenas os dados na tabela da mesma forma que a saida esperada.
        Aqui está o texto: {transcricao}
        
        Saída esperada (exemplo para dois registros):
        ID,Lote,altura,diâmetro
        1,L1,0.5,0.90
        2,L1,0.6,0.88
    
        """
        resposta = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente que transforma dados textuais em tabelas CSV."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        csv_conteudo = resposta['choices'][0]['message']['content']
        csv_conteudo = csv_conteudo.replace('```', '')
        
        # Salva o conteúdo CSV no arquivo especificado
        with open(caminho_csv, "w", encoding="utf-8") as file:
            file.write(csv_conteudo)
        
        print(f"[DEBUG] CSV salvo em: {caminho_csv}")
    except Exception as e:
        print(f"[ERROR] Erro ao formatar transcrição para CSV: {e}")
        raise e

if __name__ == "__main__":
    caminho_audio = "D:/Users/Carlo/Faculdade/IoT/Du-Cauli/data/Demo.m4a"
    caminho_csv = "D:/Users/Carlo/Faculdade/IoT/Du-Cauli/dados_transcritos/transcricao_formatada.csv"
    
    # Transcrição do áudio
    texto_transcrito = transcrever_audio(caminho_audio)
    
    # Formatação e salvamento em CSV
    formatar_transcricao_para_csv(texto_transcrito, caminho_csv)