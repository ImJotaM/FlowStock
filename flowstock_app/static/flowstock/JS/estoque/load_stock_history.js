function carregarHistorico(stockId) {
    const lista = document.getElementById("listaHistorico");
    lista.innerHTML = "<li class='list-group-item'>Carregando histórico...</li>";

    fetch(`/estoque/${stockId}/historico/json/`)
        .then(response => response.json())
        .then(data => {
            lista.innerHTML = "";

            if (data.historico.length === 0) {
                lista.innerHTML = "<li class='list-group-item'>Nenhuma alteração registrada.</li>";
            } else {
                data.historico.forEach(item => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.innerHTML = `
                        <strong>${item.tipo}</strong> - ${item.item}<br>
                        <small>Quantidade: ${item.quantidade}, por ${item.usuario} em ${item.data}</small><br>
                        <em>${item.obs}</em>
                    `;
                    lista.appendChild(li);
                });
            }
        })
        .catch(error => {
            lista.innerHTML = "<li class='list-group-item text-danger'>Erro ao carregar histórico.</li>";
        });
}