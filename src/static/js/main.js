import { createIcons, icons } from 'lucide';
import 'htmx.org';
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import { TriangleDashed } from 'lucide';
import focus from '@alpinejs/focus'

// Caution, this will import all the icons and bundle them.
createIcons({ icons });

document.body.addEventListener('htmx:afterSwap', function(event) {
    // Re-renderiza todos os ícones no DOM após o htmx trocar o conteúdo.
    // O htmx:afterSwap é disparado sempre que um swap de sucesso acontece.
    createIcons({ icons });
    console.log("Lucide icons re-rendered after HTMX swap.");

    // Use Alpine's nextTick to ensure DOM/URL updates are finished
    Alpine.nextTick(() => { // <-- Use Alpine.nextTick()
        // Access and update the store property
        Alpine.store('sidebar').currentPath = window.location.pathname;
        console.log('HTMX Swap Completo. Novo Caminho Ativo:', Alpine.store('sidebar').currentPath);
    });

    // 2. Ouvir o popstate para botões Voltar/Avançar (boa prática)
    window.addEventListener('popstate', () => {
        currentPath = window.location.pathname;
    });
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