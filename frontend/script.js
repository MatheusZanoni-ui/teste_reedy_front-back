// ── Atualiza o nome do arquivo selecionado na tela ──
function configurarUpload(inputId, labelId) {
  const input = document.getElementById(inputId);
  const label = document.getElementById(labelId);

  input.addEventListener("change", function () {
    if (this.files.length > 0) {
      label.textContent = this.files[0].name;
    } else {
      label.textContent = "Nenhum arquivo selecionado";
    }
  });
}

configurarUpload("filtro",    "label-filtro");
configurarUpload("pagamento", "label-pagamento");


// ── Helpers para mostrar/esconder mensagens ──
function mostrarErro(texto) {
  const el = document.getElementById("msg-erro");
  el.textContent = texto;
  el.hidden = false;
  document.getElementById("msg-sucesso").hidden = true;
}

function mostrarSucesso(texto) {
  const el = document.getElementById("msg-sucesso");
  el.textContent = texto;
  el.hidden = false;
  document.getElementById("msg-erro").hidden = true;
}

function limparMensagens() {
  document.getElementById("msg-erro").hidden    = true;
  document.getElementById("msg-sucesso").hidden = true;
}


// ── Envio do formulário ──
document.getElementById("form-relatorio").addEventListener("submit", async function (e) {
  e.preventDefault();  // impede o reload da página
  limparMensagens();

  // Pega os valores dos campos
  const id_filial  = document.getElementById("id_filial").value.trim();
  const valor      = document.getElementById("valor").value.trim();
  const produto    = document.getElementById("produto").value.trim();
  const data_venda = document.getElementById("data_venda").value;
  const filtro     = document.getElementById("filtro").files[0];
  const pagamento  = document.getElementById("pagamento").files[0];

  // Validação básica no frontend
  if (!id_filial || !valor || !produto || !data_venda) {
    mostrarErro("Preencha todos os campos antes de continuar.");
    return;
  }

  if (!filtro || !pagamento) {
    mostrarErro("Selecione as duas planilhas antes de continuar.");
    return;
  }

  // Monta o FormData para enviar para a API
  const formData = new FormData();
  formData.append("id_filial",  id_filial);
  formData.append("valor",      valor);
  formData.append("produto",    produto);
  formData.append("data_venda", data_venda);
  formData.append("filtro",     filtro);
  formData.append("pagamento",  pagamento);

  // Estado de carregamento
  const btn        = document.getElementById("btn-enviar");
  const btnTexto   = document.getElementById("btn-texto");
  const btnLoading = document.getElementById("btn-loading");

  btn.disabled       = true;
  btnTexto.hidden    = true;
  btnLoading.hidden  = false;

  try {
    const resposta = await fetch("http://localhost:8000/gerar-relatorio", {
      method: "POST",
      body: formData,
    });

    if (!resposta.ok) {
      const erro = await resposta.text();
      mostrarErro("Erro da API: " + erro);
      return;
    }

    // Faz o download automático do arquivo retornado
    const blob = await resposta.blob();
    const url  = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href     = url;
    link.download = "relatorio_final.xlsx";
    link.click();

    URL.revokeObjectURL(url);
    mostrarSucesso("Relatório gerado com sucesso! O download iniciou automaticamente.");

  } catch (err) {
    mostrarErro("Não foi possível conectar à API. Verifique se ela está rodando.");

  } finally {
    // Restaura o botão independente do resultado
    btn.disabled      = false;
    btnTexto.hidden   = false;
    btnLoading.hidden = true;
  }
});