const faqData = [
    {
        question: "Como adiciono um novo item ao estoque?",
        answer: "Selecione o estoque desejado e clique no botão com o ícone de <strong>+ (Adicionar)</strong>. O novo item será incluído imediatamente."
    },
    {
        question: "Como posso criar um grupo?",
        answer: "Na página inicial, acesse a seção <strong>Grupos</strong>. Em seguida, digite um nome para o seu novo grupo e clique em <strong>Criar Grupo</strong> para finalizar."
    },
    {
        question: "Como faço para compartilhar um estoque?",
        answer: "Abra o estoque que deseja compartilhar e clique no <strong>ícone de compartilhamento</strong>. Você terá a opção de compartilhar com um <strong>grupo</strong> já existente ou diretamente com outros <strong>usuários</strong>, utilizando o nome ou e-mail deles."
    },
    {
        question: "Como posso editar os dados da minha conta?",
        answer: "Na tela inicial, clique no <strong>ícone de usuário</strong> no canto superior direito e selecione a opção <strong>conta</strong>. Lá, você poderá atualizar seu nome, e-mail, alterar a senha ou excluir sua conta."
    },
    {
        question: "Como gero uma lista de compras a partir de um estoque?",
        answer: "Acesse o estoque que servirá de base para suas compras. Na parte inferior da tela, clique no botão <strong>Imprimir</strong>. Um arquivo PDF com a sua lista será gerado e baixado automaticamente."
    }
];

document.addEventListener("DOMContentLoaded", () => {
    const faqAccordion = document.getElementById('faqAccordion');

    if (faqAccordion) {
        faqAccordion.innerHTML = faqData.map((item, index) => {
            const collapseId = `collapse${index}`;
            const headingId = `heading${index}`;

            // Este é o HTML limpo que nosso CSS precisa para funcionar
            return `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="${headingId}">
                        <button class="accordion-button collapsed d-flex align-items-center" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                            <span>${item.question}</span>
                            <i class="bi bi-chevron-down faq-icon"></i>
                        </button>
                    </h2>
                    <div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="${headingId}" data-bs-parent="#faqAccordion">
                        <div class="accordion-body">
                            ${item.answer}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
});