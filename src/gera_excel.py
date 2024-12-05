# gera_excel.py
import pandas as pd
import re

def extrair_dados(transcricao_texto):
    print("[DEBUG] Extraindo dados da transcrição...", transcricao_texto)
    """
    Extrai dados estruturados do texto transcrito utilizando expressões regulares.
    """
    print("[DEBUG] Extraindo dados da transcrição...")
    padrao = (
        r"ID(\d+)-[Ll](\d+),\s*[Aa]ltura\s*([\d,\.]+),\s*[Dd]iâmetro\s*([\d,\.]+)"  # Formato com ID-Lote
        r"|"  # Ou
        r"ID(\d+),\s*[Ll]ote\s*(\d+),\s*[Aa]ltura\s*([\d,\.]+),\s*[Dd]iâmetro\s*([\d,\.]+)"  # Formato com ID, lote
        r"|"  # Ou
        r"ID (\d+)-[Ll](\d+), altura ([\d,\.]+), diâmetro ([\d,\.]+)"  # Outro formato possível
    )

    dados = re.findall(padrao, transcricao_texto)
    print(f"[DEBUG] Dados encontrados: {dados}")
    dados_corrigidos = []
    for match in dados:
        if match[0] or match[4] or match[8]:  # Verifica qual padrão foi utilizado
            if match[0]:  # Caso do primeiro padrão (ID-Lote)
                id_, lote, altura, diametro = match[0], match[1], match[2], match[3]
            elif match[4]:  # Caso do segundo padrão (ID, Lote)
                id_, lote, altura, diametro = match[4], match[5], match[6], match[7]
            else:  # Caso do terceiro padrão (ID-Lote com espaço)
                id_, lote, altura, diametro = match[8], match[9], match[10], match[11]
            dados_corrigidos.append(
                (id_, lote, altura.replace(',', '.').rstrip('.'), diametro.replace(',', '.').rstrip('.'))
            )
    print(f"[DEBUG] Dados corrigidos: {dados_corrigidos}")
    return dados_corrigidos

def salvar_em_csv(dados, caminho_arquivo):
    """
    Salva os dados extraídos em um arquivo CSV.
    """
    df = pd.DataFrame(dados, columns=["ID", "LOTE", "ALTURA", "DIÂMETRO"])
    df.to_csv(caminho_arquivo, index=False)
    print(f"[DEBUG] Planilha salva como {caminho_arquivo}")

if __name__ == "__main__":
    texto_exemplo = "ID1, lote 1, altura 10, diâmetro 0,9. ID2, lote 1, altura 10,5, diâmetro 0,97"
    dados_extraidos = extrair_dados(texto_exemplo)
    salvar_em_csv(dados_extraidos, "../data/dados_transcritos.csv")


