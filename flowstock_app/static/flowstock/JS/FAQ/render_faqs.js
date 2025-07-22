const faqData = [
	{
		question: "Como faço para adicionar um item ao estoque?",
		answer: "Para fazer isso, selecione o estoque desejado e localize o botão com o ícone de ‘+’. Ao clicar nele, o item será adicionado automaticamente ao estoque."
	},
	{
		question: "Como faço para editar um item do estoque?",
		answer: "Para editar um item do estoque, primeiro localize o item desejado. Em seguida, clique no item para abrir o menu de edição. Nesse menu, você pode renomear o item, excluí-lo ou alterar sua quantidade."
	},
	{
		question: "Como faço para excluir um estoque?",
		answer: "Para excluir um estoque, localize-o na tela inicial. Na lateral, clique no botão com o ícone de lixeira . Ao confirmar a exclusão, o estoque será removido."
	},
	{
		question: "Como gerar uma lista?",
		answer: "Para gerar a lista pronta para sua compra, selecione o estoque desejado. Em seguida, localize o botão 'Imprimir' na parte inferior da tela. Ao clicar, um arquivo PDF será gerado automaticamente."
	},
	{
		question: "Como editar os dados da conta?",
		answer: "Para editar os dados da sua conta, vá até a tela inicial e localize o ícone de três tracinhos (☰) no canto superior direito. Clique nele para abrir o menu lateral e selecione a opção 'Conta'. Nessa seção, você poderá alterar seu nome, e-mail, senha ou até mesmo excluir sua conta."
	}
];

document.addEventListener("DOMContentLoaded", () => {
	const faqAccordion = document.getElementById('faqAccordion');

	faqData.forEach((item, index) => {
		const collapseId = `collapse${index}`;
		const headingId = `heading${index}`;

		faqAccordion.innerHTML += `
			<div class="accordion-item mb-3 border border-dark">
				<h2 class="accordion-header" id="${headingId}">
					<button class="accordion-button collapsed fw-bold text-dark bg-white" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
						${item.question}
					</button>
				</h2>
				<div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="${headingId}" data-bs-parent="#faqAccordion">
					<div class="accordion-body border-top border-dark bg-white text-dark">
						${item.answer}
					</div>
				</div>
			</div>
		`;
	});
});
