import { createIcons, icons } from 'lucide';

// 1. Função para criar os ícones
const renderLucideIcons = () => {
  // Limpar ícones existentes (opcional, dependendo do uso)
  // E recriar.
  createIcons({ icons });
};

// 2. Chamar no carregamento inicial da página
renderLucideIcons(); 

// 3. Chamar após o HTMX trocar o conteúdo do DOM
document.addEventListener('htmx:afterSwap', function (evt) {
    // Certifique-se de que o novo conteúdo tem a marcação Lucide Icons (e.g., <i data-lucide="home"></i>)
    renderLucideIcons();
});