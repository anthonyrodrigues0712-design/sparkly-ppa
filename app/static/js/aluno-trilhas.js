  const alunoStr = sessionStorage.getItem('aluno');
  if (!alunoStr) window.location.href = '/login';
  const aluno = JSON.parse(alunoStr);
  const alunoInfo = aluno.aluno || aluno;
  document.getElementById('nomeAluno').textContent = alunoInfo.nome || alunoInfo.usuario;

  async function carregar() {
    const trilha = document.getElementById('trilha');
    try {
      const [rm, ra] = await Promise.all([
        fetch('/api/aluno/modulos'),
        fetch('/api/aluno')
      ]);
      const data = await rm.json();
      const dadosAluno = await ra.json();
      if (!data.sucesso) throw new Error(data.erro);
      if (dadosAluno.sucesso) salvarGamificacaoNaSessao(dadosAluno.dados.aluno);
      renderizar(data.modulos);
    } catch (e) {
      trilha.innerHTML =
        `<div class="empty"><div class="em-icon"></div><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function renderizar(modulos) {
    const trilha = document.getElementById('trilha');
    if (!modulos.length) {
      trilha.innerHTML = `<div class="empty"><div class="em-icon"></div><div class="em-text">Nenhum módulo cadastrado ainda</div></div>`;
      return;
    }

    trilha.innerHTML = modulos.map(modulo => `
      <section class="modulo-bloco ${modulo.completo ? 'modulo-completo' : ''}">
        <div class="modulo-header">
          <div>
            <div class="modulo-nome">${modulo.nome}</div>
            ${modulo.descricao ? `<div class="modulo-desc">${modulo.descricao}</div>` : ''}
          </div>
          <span class="badge ${modulo.completo ? 'badge-green' : 'badge-blue'}">
            ${modulo.licoes_completas}/${modulo.total_licoes} lições
          </span>
        </div>
        <div class="licoes-caminho">
          ${modulo.licoes.map(licao => renderLicao(licao)).join('')}
        </div>
      </section>`).join('');
  }

  // ── Revisão pendente (questões erradas salvas para "revisar mais tarde") ──
  function chaveRevisao(licaoId) { return `sparkly_revisao_${licaoId}`; }

  function obterRevisaoPendente(licaoId) {
    try {
      const bruto = localStorage.getItem(chaveRevisao(licaoId));
      const lista = bruto ? JSON.parse(bruto) : [];
      return Array.isArray(lista) ? lista : [];
    } catch (e) { return []; }
  }

  function renderLicao(licao) {
    let estadoClasse = 'licao-bloqueada';
    let icone = '🔒';
    if (licao.completa) { estadoClasse = 'licao-completa'; icone = '✓'; }
    else if (licao.desbloqueada) { estadoClasse = 'licao-disponivel'; icone = '▶'; }

    const clickable = licao.desbloqueada ? `onclick="abrirLicao(${licao.id})"` : '';
    const revisaoPendente = licao.desbloqueada ? obterRevisaoPendente(licao.id) : [];

    return `
      <div class="licao-no ${estadoClasse}" ${clickable}>
        <div class="licao-icone">${icone}</div>
        <div class="licao-info">
          <div class="licao-nome">${licao.nome}</div>
          <div class="licao-progresso">${licao.questoes_concluidas}/${licao.total_questoes} questões</div>
        </div>
        <div class="licao-acoes-grupo">
          ${licao.desbloqueada
            ? `<button class="btn ${licao.completa ? 'btn-outline' : 'btn-primary'} btn-sm">${licao.completa ? 'Praticar' : 'Continuar →'}</button>`
            : `<span class="text-muted" style="font-size:.72rem;font-weight:700;">Bloqueada</span>`}
          ${revisaoPendente.length
            ? `<button class="btn btn-revisar btn-sm" onclick="event.stopPropagation(); revisarErros(${licao.id})">🔁 Revisar erros (${revisaoPendente.length})</button>`
            : ''}
        </div>
      </div>`;
  }

  async function abrirLicao(licaoId) {
    try {
      const r = await fetch(`/api/aluno/licoes/${licaoId}/questoes`);
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      if (!data.questoes.length) { alert('Esta lição ainda não tem questões.'); return; }

      // Guarda a fila de questões da lição para o desafio navegar em sequência.
      const pendentes = data.questoes.filter(q => !q.ja_concluida);
      const fila = (pendentes.length ? pendentes : data.questoes).map(q => q.id);
      sessionStorage.setItem('licaoAtual', JSON.stringify({
        licaoId, fila, original: [...fila], acertosOriginais: 0,
        contadas: [], erradas: [], modo: 'normal'
      }));
      window.location.href = `/aluno-desafio?questao=${fila[0]}&licao=${licaoId}`;
    } catch (e) {
      alert('Erro ao abrir lição: ' + e.message);
    }
  }

  function revisarErros(licaoId) {
    const fila = obterRevisaoPendente(licaoId);
    if (!fila.length) return;
    sessionStorage.setItem('licaoAtual', JSON.stringify({
      licaoId, fila, original: [], acertosOriginais: 0,
      contadas: [], erradas: [], modo: 'revisao'
    }));
    window.location.href = `/aluno-desafio?questao=${fila[0]}&licao=${licaoId}`;
  }

  function sair() { sessionStorage.clear(); window.location.href = '/login'; }
  carregar();
