// Tema claro/escuro compartilhado por todas as páginas.
// A leitura/aplicação inicial roda de forma síncrona (chamando aplicarTemaInicial
// no <head>, antes do CSS renderizar) para não haver "flash" do tema errado.
// Este arquivo cuida do resto: criar o switch na barra superior e alternar o tema.
(function () {
  const CHAVE_TEMA = 'sparkly_tema';

  function temaAtual() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function aplicarTema(tema) {
    document.documentElement.setAttribute('data-theme', tema);
    localStorage.setItem(CHAVE_TEMA, tema);
    document.querySelectorAll('.theme-switch').forEach(btn => {
      btn.setAttribute('aria-checked', tema === 'dark' ? 'true' : 'false');
      const icone = btn.querySelector('.theme-switch-thumb');
      if (icone) icone.textContent = tema === 'dark' ? '🌙' : '☀️';
    });
  }

  function alternarTema() {
    aplicarTema(temaAtual() === 'dark' ? 'light' : 'dark');
  }
  window.alternarTemaSparkly = alternarTema;

  // Cria o botão de switch dentro de cada elemento marcado com
  // [data-theme-switch-slot] (colocado ao lado do usuário na barra superior).
  function montarSwitches() {
    document.querySelectorAll('[data-theme-switch-slot]').forEach(slot => {
      if (slot.querySelector('.theme-switch')) return; // já montado
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'theme-switch';
      btn.setAttribute('role', 'switch');
      btn.setAttribute('aria-label', 'Alternar tema claro/escuro');
      btn.innerHTML = '<span class="theme-switch-thumb"></span>';
      btn.addEventListener('click', alternarTema);
      slot.appendChild(btn);
    });
    aplicarTema(temaAtual());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', montarSwitches);
  } else {
    montarSwitches();
  }
})();
