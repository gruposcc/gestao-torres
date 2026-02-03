import { createIcons, icons } from 'lucide';
import 'htmx.org';
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
//mport { TriangleDashed } from 'lucide';
import focus from '@alpinejs/focus'

// Caution, this will import all the icons and bundle them.
createIcons({ icons });

document.body.addEventListener('htmx:afterSwap', function(event) {
    // Re-renderiza todos os ícones no DOM após o htmx trocar o conteúdo.
    // O htmx:afterSwap é disparado sempre que um swap de sucesso acontece.
    createIcons({ icons });
    //console.log("Lucide icons re-rendered after HTMX swap.");

    if (window.Alpine) {
      // Use Alpine's nextTick to ensure DOM/URL updates are finished
      Alpine.nextTick(() => { // <-- Use Alpine.nextTick()
      // Access and update the store property
      Alpine.store('sidebar').currentPath = window.location.pathname;
      //console.log('HTMX Swap Completo. Novo Caminho Ativo:', Alpine.store('sidebar').currentPath);
    });
    }

    // 2. Ouvir o popstate para botões Voltar/Avançar (boa prática)
    window.addEventListener('popstate', () => {
        currentPath = window.location.pathname;
    });
    
});


//listner para alterar o titulo da pagina 
document.addEventListener('updateTitle', (e) => {
    document.title = e.detail;
});


//LOG NOTIFY
document.addEventListener('DOMContentLoaded', function() {
  window.addEventListener('notify', function(event) {
      console.log('✅ EVENTO NOTIFY CAPTURADO!', event.detail);
  });
  console.log('Listener "notify" ativo.');
});


Alpine.plugin(persist)
Alpine.plugin(focus)
// Recommended way, to include only the icons you need.
/* import { createIcons, Menu, ArrowRight, Globe } from 'lucide';

createIcons({
  icons: {
    Menu,
    ArrowRight,
    Globe
  }
}); */

Alpine.store('messages', {
  initSSE:  (url = '/events') => {
    if (!window.EventSource) {
        console.warn("Seu navegador não suporta Server-Sent Events (SSE). As notificações em tempo real não funcionarão.");
        return;
    }

    // Cria a nova conexão EventSource com o endpoint do FastAPI
    const eventSource = new EventSource(url);

    // Manipulador de Eventos: Chamado quando o servidor envia um novo evento 'message'
    // Como você não especificou 'event:' na sua rota SSE, o evento padrão é 'message'.
    eventSource.onmessage = function(event) {
        console.log('Evento SSE recebido:', event.data);

        try {
            // Os dados do servidor são uma string JSON (devido ao json.dumps no Python)
            const notificationData = JSON.parse(event.data);
            
            // O payload do Python é: {"message": str, "level": str, "title": str}
            const { message, level, title } = notificationData;

            // Mapeia o 'level' do backend (success, info, etc.) para o 'variant' do frontend
            const variantMap = {
                'success': 'success',
                'error': 'error', // Assumindo que você pode enviar 'error'
                'warning': 'warning', // Assumindo 'warning'
                'info': 'info' // Assumindo 'info'
                // Adicione outros mapeamentos conforme necessário
            };

            const variant = variantMap[level] || 'info'; // 'info' como fallback

            // 📢 Dispara o evento 'notify.window' que o Alpine Store está ouvindo
            // Isso aciona a função addNotification() do seu componente Alpine.
            window.dispatchEvent(new CustomEvent('notify', {
                detail: {
                    variant: variant,
                    title: title,
                    message: message,
                }
            }));

        } catch (e) {
            console.error('Erro ao processar o evento SSE:', e, 'Dados:', event.data);
        }
    };

    // Manipulador de Erros
    eventSource.onerror = function(error) {
        console.error('Erro na conexão SSE:', error);
        // Lógica de reconexão (opcional):
        // Se a conexão cair, você pode tentar reabri-la após um pequeno atraso.
        // O navegador geralmente tenta reconectar sozinho, mas um tratamento explícito
        // pode ser útil.
    };

    // Opcional: Manipulador de Abertura da Conexão
    eventSource.onopen = function() {
        console.log("Conexão SSE aberta com sucesso.");
    };

    // Retorna a instância do EventSource para controle posterior, se necessário
    return eventSource;
}
})

Alpine.store('theme', {
  darkMode: Alpine.$persist(false).as("darkMode"),
  toggle() {
    this.darkMode = !this.darkMode;
  },
  init(){
    if (window.matchMedia('(prefers-color-scheme: dark)').matches && !localStorage.getItem("darkMode")) {
      this.darkMode = true;
    }
  }, 

})

Alpine.store('sidebar', {
  currentPath: window.location.pathname, 
  isSidebarOpen: Alpine.$persist(false).as("isSidebarOpen"),
  toggle() {
    this.isSidebarOpen = !this.isSidebarOpen
  }
})


window.Alpine = Alpine
window.htmx = require('htmx.org');

Alpine.start()