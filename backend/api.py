import shutil, os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from teste_relatorio import gerar_relatorio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/gerar-relatorio")
async def endpoint_gerar_relatorio(
    filtro:     UploadFile = File(...),
    pagamento:  UploadFile = File(...),
    id_filial:  str = Form(...),   # ← vem do site
    valor:      str = Form(...),   # ← vem do site
    produto:    str = Form(...),   # ← vem do site
    data_venda: str = Form(...),   # ← vem do site
):
    with open("temp_filtro.xlsx", "wb") as f:
        shutil.copyfileobj(filtro.file, f)
    with open("temp_pagamento.xlsx", "wb") as f:
        shutil.copyfileobj(pagamento.file, f)

    try:
        df_saida, df_nao_encontrados = gerar_relatorio(
            arquivo_filtro    = "temp_filtro.xlsx",
            arquivo_pagamento = "temp_pagamento.xlsx",
            id_filial  = id_filial,    # ← repassa para a função
            valor      = valor,        # ← repassa para a função
            produto    = produto,      # ← repassa para a função
            data_venda = data_venda,   # ← repassa para a função
        )

        df_saida.to_excel("relatorio_final.xlsx", index=False)

        if len(df_nao_encontrados) > 0:
            df_nao_encontrados.to_excel("nao_encontrados.xlsx", index=False)

    finally:
        os.remove("temp_filtro.xlsx")
        os.remove("temp_pagamento.xlsx")

    return FileResponse(
        path     = "relatorio_final.xlsx",
        filename = "relatorio_final.xlsx",
    )