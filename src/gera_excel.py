# # gera_excel.py
# import pandas as pd
# import re

# def extrair_dados(transcricao_texto):
#     print("[DEBUG] Extraindo dados da transcrição...", transcricao_texto)
#     """
#     Extrai dados estruturados do texto transcrito utilizando expressões regulares.
#     """
#     print("[DEBUG] Extraindo dados da transcrição...")
#     padrao = (
#         r"ID(\d+)-[Ll](\d+),\s*[Aa]ltura\s*([\d,\.]+),\s*[Dd]iâmetro\s*([\d,\.]+)"  # Formato com ID-Lote
#         r"|"  # Ou
#         r"ID(\d+),\s*[Ll]ote\s*(\d+),\s*[Aa]ltura\s*([\d,\.]+),\s*[Dd]iâmetro\s*([\d,\.]+)"  # Formato com ID, lote
#         r"|"  # Ou
#         r"ID (\d+)-[Ll](\d+), altura ([\d,\.]+), diâmetro ([\d,\.]+)"  # Outro formato possível
#     )

#     dados = re.findall(padrao, transcricao_texto)
#     print(f"[DEBUG] Dados encontrados: {dados}")
#     dados_corrigidos = []
#     for match in dados:
#         if match[0] or match[4] or match[8]:  # Verifica qual padrão foi utilizado
#             if match[0]:  # Caso do primeiro padrão (ID-Lote)
#                 id_, lote, altura, diametro = match[0], match[1], match[2], match[3]
#             elif match[4]:  # Caso do segundo padrão (ID, Lote)
#                 id_, lote, altura, diametro = match[4], match[5], match[6], match[7]
#             else:  # Caso do terceiro padrão (ID-Lote com espaço)
#                 id_, lote, altura, diametro = match[8], match[9], match[10], match[11]
#             dados_corrigidos.append(
#                 (id_, lote, altura.replace(',', '.').rstrip('.'), diametro.replace(',', '.').rstrip('.'))
#             )
#     print(f"[DEBUG] Dados corrigidos: {dados_corrigidos}")
#     return dados_corrigidos

# def salvar_em_csv(dados, caminho_arquivo):
#     """
#     Salva os dados extraídos em um arquivo CSV.
#     """
#     df = pd.DataFrame(dados, columns=["ID", "LOTE", "ALTURA", "DIÂMETRO"])
#     df.to_csv(caminho_arquivo, index=False)
#     print(f"[DEBUG] Planilha salva como {caminho_arquivo}")

# if __name__ == "__main__":
#     texto_exemplo = "ID1, lote 1, altura 10, diâmetro 0,9. ID2, lote 1, altura 10,5, diâmetro 0,97"
#     dados_extraidos = extrair_dados(texto_exemplo)
#     salvar_em_csv(dados_extraidos, "../data/dados_transcritos.csv")



########## ate aui funciona



# # gera_excel.py
# import os
# from src.processa_audios import transcrever_audio  # Importa a função do outro arquivo
# import openai

# def formatar_transcricao_para_csv(transcricao, caminho_csv):
#     """ 
#     Usa um modelo de linguagem para formatar a transcrição em CSV e salva no caminho especificado.
#     """
#     print(f"[DEBUG] Formatando transcrição para CSV com LLM.")
#     try:
#         prompt = f"""
#         A seguinte transcrição de áudio contém dados estruturados de medições. 
#         Reformate o texto abaixo em uma tabela CSV com as seguintes colunas:
#         - ID
#         - lote
#         - altura
#         - diâmetro

#         Aqui está o texto: {transcricao}
        
#         Saída esperada (exemplo para dois registros):
#         ID,lote,altura,diâmetro
#         1,L1,0.5,0.90
#         2,L1,0.6,0.88
#         Não adicione nenhum comentário adicional, apenas a tabela CSV.
#         """
#         resposta = openai.ChatCompletion.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Você é um assistente que transforma dados textuais em tabelas CSV."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0
#         )
#         csv_conteudo = resposta['choices'][0]['message']['content']
        
#         # Salva o conteúdo CSV no arquivo especificado
#         with open(caminho_csv, "w", encoding="utf-8") as file:
#             file.write(csv_conteudo)
        
#         print(f"[DEBUG] CSV salvo em: {caminho_csv}")
#     except Exception as e:
#         print(f"[ERROR] Erro ao formatar transcrição para CSV: {e}")
#         raise e

# if __name__ == "__main__":
#     caminho_audio = "D:/Users/Carlo/Faculdade/IoT/Du-Cauli/data/Demo.m4a"
#     caminho_csv = "D:/Users/Carlo/Faculdade/IoT/Du-Cauli/dados_transcritos/transcricao_formatada.csv"
    
#     # Transcrição do áudio
#     texto_transcrito = transcrever_audio(caminho_audio)
    
#     # Formatação e salvamento em CSV
#     formatar_transcricao_para_csv(texto_transcrito, caminho_csv)


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