import pandas as pd
import re

# ─────────────────────────────────────────────
# 1. CONFIGURAÇÕES — ajuste os nomes dos arquivos
#    e das colunas conforme suas planilhas reais
# ─────────────────────────────────────────────

ARQUIVO_FILTRO    = "FiltroClientes (16).xlsx"   # Planilha Filtro de Cliente
ARQUIVO_PAGAMENTO = "Contas_receber (2).xlsx"        # Planilha de Pagamento
ARQUIVO_SAIDA     = "relatorio_final.xlsx"  # Planilha gerada

# Nomes exatos das colunas em cada planilha (ajuste se necessário)
COL_CPF_FILTRO    = "CPF (CIN)"
COL_NOME_FILTRO   = "Nome"
COL_CONTRATO      = "Contratos"

COL_CPF_PAG       = "CPF (CIN)"
COL_NOME_PAG      = "Nome"
COL_DATA          = "Lançamento"

TEXTO_REEDY       = "Reedy 30"   # Trecho que identifica o contrato adicional


# ─────────────────────────────────────────────
# 2. FUNÇÃO AUXILIAR — limpa CPF (só dígitos)
# ─────────────────────────────────────────────

def limpar_cpf(valor):
    """Remove tudo que não for dígito do CPF."""
    return re.sub(r"\D", "", str(valor))


# ─────────────────────────────────────────────
# 3. LEITURA DAS PLANILHAS
# ─────────────────────────────────────────────

df_filtro    = pd.read_excel(ARQUIVO_FILTRO,    dtype={COL_CPF_FILTRO: str}, engine="openpyxl")
df_pagamento = pd.read_excel(ARQUIVO_PAGAMENTO, dtype={COL_CPF_PAG: str}, engine="openpyxl")


# ─────────────────────────────────────────────
# 4. LIMPEZA DOS CPFs NAS DUAS PLANILHAS
# ─────────────────────────────────────────────

df_filtro[COL_CPF_FILTRO]    = df_filtro[COL_CPF_FILTRO].apply(limpar_cpf)
df_pagamento[COL_CPF_PAG]    = df_pagamento[COL_CPF_PAG].apply(limpar_cpf)


# ─────────────────────────────────────────────
# 5. FILTRO: apenas clientes com contrato Reedy 30
# ─────────────────────────────────────────────

df_reedy = df_filtro[
    df_filtro[COL_CONTRATO].str.contains(TEXTO_REEDY, case=False, na=False)
].copy()


# ─────────────────────────────────────────────
# 6. MERGE (junção) pela coluna CPF
# ─────────────────────────────────────────────

df_merged = pd.merge(
    df_reedy[[COL_CPF_FILTRO, COL_NOME_FILTRO]],   # colunas que nos interessam do filtro
    df_pagamento[[COL_CPF_PAG, COL_DATA]], # colunas de pagamento
    left_on  = COL_CPF_FILTRO,
    right_on = COL_CPF_PAG,
    how      = "inner"   # só quem aparecer nas duas planilhas
)


# ─────────────────────────────────────────────
# 7. MONTAGEM DA PLANILHA FINAL
# ─────────────────────────────────────────────

df_saida = pd.DataFrame({
    "ID_FILIAL" : "22",
    "NOME"          : df_merged[COL_NOME_FILTRO],
    "CPF (CIN)"           : df_merged[COL_CPF_FILTRO],
    "VALOR"         : "30",
    "SERVIÇO" : "",
    "PRODUTO" : "REEDY 30 - LIVRO DIGITAL - EBOOK PREMIUM",
    "DATA_VENDA" : pd.to_datetime(df_merged[COL_DATA], dayfirst = True).dt.strftime("%d/%m/%Y"),
    "TIPO_RECEBIMENTO" : "12",
    "TID" : "",
    "NSU" : "",
    "AUTORIZAÇÃO" : "",
})

df_saida = df_saida.reset_index(drop=True)


# ─────────────────────────────────────────────
# 8. EXPORTAÇÃO PARA EXCEL COM FORMATAÇÃO BÁSICA
# ─────────────────────────────────────────────

with pd.ExcelWriter(ARQUIVO_SAIDA, engine="openpyxl") as writer:
    df_saida.to_excel(writer, index=False, sheet_name="Relatório")

    # Ajusta largura das colunas automaticamente
    ws = writer.sheets["Relatório"]
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_len + 4

print(f"✅ Planilha '{ARQUIVO_SAIDA}' gerada com {len(df_saida)} registros.")