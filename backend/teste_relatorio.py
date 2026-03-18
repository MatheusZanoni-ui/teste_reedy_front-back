import pandas as pd
import re

COL_CPF_FILTRO  = "CPF (CIN)"
COL_NOME_FILTRO = "Nome"
COL_CONTRATO    = "Contratos"
COL_CPF_PAG     = "CPF (CIN)"
COL_NOME_PAG    = "Nome"
COL_DATA        = "Lançamento"
TEXTO_REEDY     = "Reedy 30"

def limpar_cpf(valor):
    return re.sub(r"\D", "", str(valor))

def gerar_relatorio(arquivo_filtro, arquivo_pagamento, id_filial, valor, produto, data_venda):
    #                                                   ↑ recebe os 4 valores do formulário

    df_filtro    = pd.read_excel(arquivo_filtro,    dtype={COL_CPF_FILTRO: str}, engine="openpyxl")
    df_pagamento = pd.read_excel(arquivo_pagamento, dtype={COL_CPF_PAG: str},    engine="openpyxl")

    df_filtro[COL_CPF_FILTRO] = df_filtro[COL_CPF_FILTRO].apply(limpar_cpf)
    df_pagamento[COL_CPF_PAG] = df_pagamento[COL_CPF_PAG].apply(limpar_cpf)

    df_anti = pd.merge(
        df_pagamento[[COL_CPF_PAG, COL_NOME_PAG, COL_DATA]],
        df_filtro[[COL_CPF_FILTRO]],
        left_on=COL_CPF_PAG,
        right_on=COL_CPF_FILTRO,
        how="left",
        indicator=True
    )
    df_nao_encontrados = df_anti[df_anti["_merge"] == "left_only"].copy()
    df_nao_encontrados = df_nao_encontrados.drop(columns=["_merge", COL_CPF_FILTRO])

    df_reedy = df_filtro[
        df_filtro[COL_CONTRATO].str.contains(TEXTO_REEDY, case=False, na=False)
    ].copy()

    df_merged = pd.merge(
        df_reedy[[COL_CPF_FILTRO, COL_NOME_FILTRO]],
        df_pagamento[[COL_CPF_PAG, COL_DATA]],
        left_on=COL_CPF_FILTRO,
        right_on=COL_CPF_PAG,
        how="inner"
    )

    df_saida = pd.DataFrame({
        "ID_FILIAL"        : id_filial,   # ← vem do formulário
        "NOME"             : df_merged[COL_NOME_FILTRO],
        "CPF (CIN)"        : df_merged[COL_CPF_FILTRO],
        "VALOR"            : valor,       # ← vem do formulário
        "SERVIÇO"          : "",
        "PRODUTO"          : produto,     # ← vem do formulário
        "DATA_VENDA"       : data_venda,  # ← vem do formulário
        "TIPO_RECEBIMENTO" : "12",
        "TID"              : "",
        "NSU"              : "",
        "AUTORIZAÇÃO"      : "",
    }).reset_index(drop=True)

    return df_saida, df_nao_encontrados