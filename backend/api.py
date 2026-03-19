import shutil, os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from zipfile import ZipFile
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
    id_filial:  str = Form(...),
    valor:      str = Form(...),
    produto:    str = Form(...),
    data_venda: str = Form(...),
):
    with open("temp_filtro.xlsx", "wb") as f:
        shutil.copyfileobj(filtro.file, f)
    with open("temp_pagamento.xlsx", "wb") as f:
        shutil.copyfileobj(pagamento.file, f)

    try:
        df_saida, df_nao_encontrados = gerar_relatorio(
            arquivo_filtro    = "temp_filtro.xlsx",
            arquivo_pagamento = "temp_pagamento.xlsx",
            id_filial  = id_filial,
            valor      = valor,
            produto    = produto,
            data_venda = data_venda,
        )

        df_saida.to_excel("relatorio_final.xlsx", index=False)

        # Verifica se tem não encontrados
        tem_nao_encontrados = len(df_nao_encontrados) > 0
        if tem_nao_encontrados:
            df_nao_encontrados.to_excel("nao_encontrados.xlsx", index=False) 

        # Junta os dois arquivos em um .zip para download
        with ZipFile("resultado.zip", "w") as zipf:
            zipf.write("relatorio_final.xlsx")
            if tem_nao_encontrados:
                zipf.write("nao_encontrados.xlsx")

    finally:
        os.remove("temp_filtro.xlsx")
        os.remove("temp_pagamento.xlsx")

    # Devolve o .zip para download
    return FileResponse(
        path        = "resultado.zip",
        filename    = "resultado.zip",
        media_type  = "application/zip"
    )