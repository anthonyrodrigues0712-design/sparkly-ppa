  if (!sessionStorage.getItem('aluno')) window.location.href='/login';

  const LETRAS = ['A','B','C','D','E','F','G','H'];
  const TIPO_LABEL = {
    multipla_escolha:'Múltipla Escolha','multipla-escolha':'Múltipla Escolha',
    verdadeiro_falso:'Verdadeiro / Falso', dissertativa:'Dissertativa', calculo:'Cálculo'
  };
  const TIPO_BADGE = {
    multipla_escolha:'badge-blue','multipla-escolha':'badge-blue',
    verdadeiro_falso:'badge-purple', dissertativa:'badge-neutral', calculo:'badge-green'
  };

  const params = new URLSearchParams(window.location.search);
  const questaoId = parseInt(params.get('questao'));
  const licaoId = params.get('licao') ? parseInt(params.get('licao')) : null;
  if (!questaoId) window.location.href='/aluno-trilhas';

  let questaoAtual = null, respostaSelecionada = null, jaConfirmou = false;

  // ── Estado da fila da lição (persistido em sessionStorage) ──
  function chaveRevisao(id) { return `sparkly_revisao_${id}`; }

  function lerEstado() {
    if (!licaoId) return null;
    try {
      const estado = JSON.parse(sessionStorage.getItem('licaoAtual') || 'null');
      if (!estado || estado.licaoId !== licaoId) return null;
      estado.original = estado.original || [];
      estado.contadas = estado.contadas || [];
      estado.erradas = estado.erradas || [];
      estado.acertosOriginais = estado.acertosOriginais || 0;
      estado.modo = estado.modo || 'normal';
      return estado;
    } catch (e) { return null; }
  }

  function salvarEstado(estado) {
    sessionStorage.setItem('licaoAtual', JSON.stringify(estado));
  }

  function salvarRevisaoPendente(licaoIdAlvo, listaIds) {
    if (listaIds.length) localStorage.setItem(chaveRevisao(licaoIdAlvo), JSON.stringify(listaIds));
    else localStorage.removeItem(chaveRevisao(licaoIdAlvo));
  }

  // Registra o resultado da questão atual no estado da fila:
  // - conta a questão como "respondida original" na primeira vez que aparece
  // - se errou, marca para retornar ao fim da fila (e da lista de revisão)
  function registrarResultadoNaFila(correto) {
    const estado = lerEstado();
    if (!estado) return null;

    const eraOriginalNaoContada = estado.modo === 'normal'
      && estado.original.includes(questaoId)
      && !estado.contadas.includes(questaoId);

    if (eraOriginalNaoContada) {
      estado.contadas.push(questaoId);
      if (correto) estado.acertosOriginais += 1;
    }

    // Calcula a próxima questão da fila ANTES de mover a atual (se errada) para
    // o final — caso contrário, ao empurrá-la para o fim, ela passaria a ser o
    // último elemento e pareceria (erroneamente) que a fila acabou ali mesmo,
    // mostrando "Ver trilha" mesmo havendo questões restantes no módulo.
    const idxAtual = estado.fila.indexOf(questaoId);
    estado.proximaId = (idxAtual !== -1 && idxAtual < estado.fila.length - 1)
      ? estado.fila[idxAtual + 1]
      : null;

    if (!correto) {
      if (!estado.erradas.includes(questaoId)) estado.erradas.push(questaoId);
      // Remove ocorrência atual e reinsere a questão ao final da fila, para
      // que ela seja revisada novamente após as demais questões do módulo.
      estado.fila = estado.fila.filter(id => id !== questaoId);
      estado.fila.push(questaoId);
    } else {
      // Acertou: some da lista de erradas (caso estivesse revisando) e não repete.
      estado.erradas = estado.erradas.filter(id => id !== questaoId);
    }

    salvarEstado(estado);
    return estado;
  }

  function proximaQuestaoDaFila(estado) {
    if (!licaoId || !estado) return null;
    return estado.proximaId || null;
  }

  async function carregarQuestao() {
    try {
      const url = licaoId ? `/api/aluno/licoes/${licaoId}/questoes` : '/api/aluno/questoes';
      const r = await fetch(url);
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      const lista = licaoId ? data.questoes : data.questoes;
      questaoAtual = lista.find(q => q.id === questaoId);
      if (!questaoAtual) throw new Error('Questão não encontrada');

      if (questaoAtual.bloqueada) {
        document.getElementById('telaLoading').style.display = 'none';
        document.getElementById('telaBloqueada').style.display = 'flex';
        return;
      }
      renderQuestao();
    } catch(e) {
      document.getElementById('telaLoading').innerHTML =
        `<div style="text-align:center"><div style="font-size:2rem"></div><p style="font-weight:700;color:var(--red);margin:8px 0">${e.message}</p>
         <a href="/aluno-trilhas" class="btn btn-outline btn-sm mt-2">← Voltar</a></div>`;
    }
  }

  function renderQuestao() {
    document.getElementById('telaLoading').style.display = 'none';
    document.getElementById('telaQuestao').style.display = 'flex';
    const q = questaoAtual;
    const badge = document.getElementById('tipoBadge');
    badge.textContent = TIPO_LABEL[q.tipo] || q.tipo;
    badge.className = 'badge ' + (TIPO_BADGE[q.tipo] || 'badge-neutral');
    document.getElementById('qNome').textContent = q.nome;
    document.getElementById('qEnunciado').textContent = q.conteudo.enunciado || '';

    const tipo = q.tipo;
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      const wrap = document.getElementById('alternativasWrap');
      const alts = q.conteudo.alternativas || [];
      wrap.innerHTML = alts.map((alt,i) => `
        <button class="alt-btn" id="alt-${i}" onclick="selecionarAlt(${i})">
          <span class="letra">${LETRAS[i]}</span><span>${alt}</span>
        </button>`).join('');
      wrap.style.display = 'flex';
      document.getElementById('respostaLivre').style.display = 'none';
    } else {
      document.getElementById('alternativasWrap').style.display = 'none';
      document.getElementById('respostaLivre').style.display = 'block';
    }
  }

  function selecionarAlt(idx) {
    if (jaConfirmou) return;
    respostaSelecionada = idx;
    document.querySelectorAll('.alt-btn').forEach((btn,i) => btn.classList.toggle('selecionada', i===idx));
    document.getElementById('btnConfirmar').disabled = false;
  }

  const TEMPO_TRANSICAO_MS = 10000;
  let timeoutTransicao = null;

  async function confirmar() {
    if (jaConfirmou) return;
    const tipo = questaoAtual.tipo;
    let resposta;
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      if (respostaSelecionada===null) return;
      resposta = respostaSelecionada;
    } else {
      resposta = document.getElementById('respostaLivre').value.trim();
      if (!resposta) return;
    }

    jaConfirmou = true;
    document.getElementById('btnConfirmar').disabled = true;
    document.getElementById('respostaLivre').disabled = true;
    document.querySelectorAll('.alt-btn').forEach(b => b.disabled = true);

    try {
      const r = await fetch(`/api/aluno/questoes/${questaoId}/responder`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ resposta })
      });
      const data = await r.json();
      if (!data.sucesso) {
        if (r.status === 403) {
          document.getElementById('telaQuestao').style.display = 'none';
          document.getElementById('telaBloqueada').style.display = 'flex';
          return;
        }
        throw new Error(data.erro);
      }
      if (typeof data.pontos_totais === 'number' || typeof data.sparks_totais === 'number' || typeof data.coracoes === 'number') {
        const campos = {};
        if (typeof data.pontos_totais === 'number') campos.pontos = data.pontos_totais;
        if (typeof data.sparks_totais === 'number') campos.sparks = data.sparks_totais;
        if (typeof data.coracoes === 'number') campos.coracoes = data.coracoes;
        salvarGamificacaoNaSessao(campos);
      }
      mostrarFeedback(data);
      iniciarTransicaoParaResultado(data);
    } catch(e) {
      const box = document.getElementById('feedbackBox');
      box.className = 'feedback-box incorreto'; box.style.display = 'block';
      document.getElementById('feedbackTitulo').textContent = 'Erro';
      document.getElementById('feedbackDetalhe').textContent = e.message;
      jaConfirmou = false;
      document.getElementById('btnConfirmar').disabled = false;
    }
  }

  // Dá tempo para o aluno olhar o que acertou/errou antes de seguir em frente.
  // Uma barrinha mostra a contagem regressiva e o aluno pode adiantar clicando em "Continuar".
  function iniciarTransicaoParaResultado(data) {
    const btnContinuar = document.getElementById('btnContinuar');
    btnContinuar.style.display = 'inline-flex';
    btnContinuar.classList.add('surgir-suave');
    btnContinuar.onclick = () => continuarAgora(data);

    const fill = document.getElementById('feedbackTimerFill');
    fill.style.transition = 'none';
    fill.style.width = '100%';
    // força reflow para reiniciar a transição a partir de 100%
    void fill.offsetWidth;
    fill.style.transition = `width ${TEMPO_TRANSICAO_MS}ms linear`;
    requestAnimationFrame(() => { fill.style.width = '0%'; });

    timeoutTransicao = setTimeout(() => transicaoParaResultado(data), TEMPO_TRANSICAO_MS);
  }

  function continuarAgora(data) {
    if (timeoutTransicao) { clearTimeout(timeoutTransicao); timeoutTransicao = null; }
    transicaoParaResultado(data || ultimoResultado);
  }

  let ultimoResultado = null;

  // Transição suave: a tela de questão esmaece e desliza para fora, e só então
  // a tela de resultado aparece com um fade-in.
  function transicaoParaResultado(data) {
    ultimoResultado = data;
    const telaQuestao = document.getElementById('telaQuestao');
    telaQuestao.classList.add('tela-saindo');
    setTimeout(() => {
      telaQuestao.style.display = 'none';
      telaQuestao.classList.remove('tela-saindo');
      mostrarResultado(data);
    }, 420);
  }

  function mostrarFeedback(data) {
    document.getElementById('btnConfirmar').style.display = 'none';
    const box = document.getElementById('feedbackBox');
    const alts = questaoAtual.conteudo.alternativas || [];
    const tipo = questaoAtual.tipo;
    box.className = 'feedback-box ' + (data.correto ? 'correto' : 'incorreto');
    box.style.display = 'block';
    document.getElementById('feedbackTitulo').textContent = data.correto ? '✓ Correto!' : '✗ Resposta incorreta';
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      document.querySelectorAll('.alt-btn').forEach((btn,i) => {
        if (i===data.gabarito) btn.classList.add('correta');
        else if (i===respostaSelecionada && !data.correto) btn.classList.add('errada');
      });
      document.getElementById('feedbackDetalhe').textContent = data.correto
        ? 'Parabéns! Continue assim! '
        : `Resposta correta: ${LETRAS[data.gabarito]}) ${alts[data.gabarito]||''}`;
    } else {
      document.getElementById('feedbackDetalhe').textContent = data.correto
        ? 'Resposta certa! ' : `Gabarito: "${data.gabarito}"`;
    }
  }

  function mostrarResultado(data) {
    const estado = registrarResultadoNaFila(data.correto);

    document.getElementById('telaResultado').style.display = 'flex';
    document.getElementById('telaResultado').classList.remove('tela-entrando');
    void document.getElementById('telaResultado').offsetWidth;
    document.getElementById('telaResultado').classList.add('tela-entrando');
    document.getElementById('resEmoji').textContent = data.correto ? '' : '';
    document.getElementById('resTitulo').textContent = data.correto ? 'Incrível!' : 'Quase lá!';
    document.getElementById('resTitulo').className = 'resultado-titulo ' + (data.correto?'correto':'incorreto');
    document.getElementById('resSub').textContent = data.correto
      ? 'Nota 10! Você está arrasando! Continue assim!'
      : 'Não desanime! Refaça a questão para melhorar.';
    const fill = document.getElementById('resBarraFill');
    fill.style.background = data.correto ? 'var(--green)' : 'var(--red)';
    setTimeout(() => fill.style.width = (data.correto?'100%':'30%'), 100);
    document.getElementById('resBarraLabel').textContent = data.correto ? 'Nota: 10.0' : 'Nota: 0.0';

    const gami = document.getElementById('resGamificacao');
    const partes = [];
    if (data.pontos_ganhos) partes.push(`<span class="ganho-pontos">⭐ +${data.pontos_ganhos} XP</span>`);
    if (data.sparks_ganhos) partes.push(`<span class="ganho-sparks">⚡ +${data.sparks_ganhos} Sparks</span>`);
    if (data.correto && data.em_pratica) partes.push(`<span class="ganho-coracao">❤️ +1 coração</span>`);
    else if (!data.correto && !data.em_pratica) partes.push(`<span class="perda-coracao">💔 -1 coração</span>`);
    if (data.pet_subiu_nivel && data.pet_nivel) {
      partes.push(`<span class="ganho-nivel-pet">🐾 Seu pet subiu para o nível ${data.pet_nivel.nivel}!</span>`);
    }
    gami.innerHTML = partes.join('');

    // Chegou ao fim das questões ORIGINAIS do módulo (antes de emendar as erradas)?
    const fimDasOriginais = estado && estado.modo === 'normal'
      && estado.contadas.length >= estado.original.length
      && estado.original.length > 0;

    if (fimDasOriginais && estado.erradas.length > 0) {
      const rendimento = Math.round((estado.acertosOriginais / estado.original.length) * 100);
      estado.modo = 'revisaoAtiva';
      salvarEstado(estado);
      mostrarTelaRevisao(estado, rendimento);
      return;
    }

    renderAcoesResultado(estado);
  }

  function renderAcoesResultado(estado) {
    const proximaId = proximaQuestaoDaFila(estado);
    const acoes = document.querySelector('#telaResultado .resultado-acoes');
    if (proximaId) {
      acoes.innerHTML = `
        <button class="btn btn-primary btn-full btn-lg" onclick="irParaProximaQuestao(${proximaId})">Próxima questão →</button>
        <a href="/aluno-trilhas" class="btn btn-outline btn-full">Sair da lição</a>`;
    } else if (licaoId) {
      if (estado) salvarRevisaoPendente(licaoId, estado.erradas);
      acoes.innerHTML = `
        <a href="/aluno-trilhas" class="btn btn-primary btn-full btn-lg">🎉 Lição concluída! Ver trilha</a>
        <a href="/aluno-dashboard" class="btn btn-outline btn-full">Dashboard</a>`;
    }
  }

  // Tela exibida ao final das questões originais do módulo quando há erros pendentes.
  // Abaixo de 70% de rendimento: revisão sugerida com destaque forte.
  // 70% ou mais: revisão totalmente opcional.
  function mostrarTelaRevisao(estado, rendimento) {
    document.getElementById('telaResultado').style.display = 'none';
    let tela = document.getElementById('telaRevisao');
    if (!tela) {
      tela = document.createElement('div');
      tela.id = 'telaRevisao';
      document.body.appendChild(tela);
    }
    tela.style.display = 'flex';
    tela.classList.remove('tela-entrando');
    void tela.offsetWidth;
    tela.classList.add('tela-entrando');

    const abaixoDaMeta = rendimento < 70;
    const titulo = abaixoDaMeta
      ? 'Vamos revisar! Sua trilha para o conhecimento só está começando'
      : 'Mandou bem! Que tal revisar o que errou?';
    const sub = abaixoDaMeta
      ? `Você acertou ${rendimento}% das questões originais. Revisar agora ajuda a fixar o conteúdo.`
      : `Você atingiu ${rendimento}% de rendimento — ótimo! A revisão das questões erradas é opcional.`;

    tela.innerHTML = `
      <div class="revisao-wrap">
        <div class="revisao-icone">${abaixoDaMeta ? '📚' : '✨'}</div>
        <div class="revisao-titulo">${titulo}</div>
        <p class="revisao-sub">${sub}</p>
        <div class="revisao-acoes">
          <button class="btn btn-outline btn-full" onclick="revisarMaisTarde()">Revisar mais tarde</button>
          <button class="btn btn-comecar btn-full btn-lg" onclick="comecarRevisaoAgora()">✨ Vamos começar! ✨</button>
        </div>
      </div>`;
  }

  function revisarMaisTarde() {
    const estado = lerEstado();
    if (estado) salvarRevisaoPendente(licaoId, estado.erradas);
    sessionStorage.removeItem('licaoAtual');
    window.location.href = '/aluno-trilhas';
  }

  function comecarRevisaoAgora() {
    const estado = lerEstado();
    const telaRevisao = document.getElementById('telaRevisao');
    telaRevisao.classList.add('tela-saindo');
    setTimeout(() => {
      telaRevisao.style.display = 'none';
      telaRevisao.classList.remove('tela-saindo');
      const telaResultado = document.getElementById('telaResultado');
      telaResultado.style.display = 'flex';
      telaResultado.classList.remove('tela-entrando');
      void telaResultado.offsetWidth;
      telaResultado.classList.add('tela-entrando');
      renderAcoesResultado(estado);
    }, 420);
  }

  function irParaProximaQuestao(id) {
    window.location.href = `/aluno-desafio?questao=${id}&licao=${licaoId}`;
  }

  document.getElementById('respostaLivre').addEventListener('input', function() {
    document.getElementById('btnConfirmar').disabled = this.value.trim()==='';
  });

  carregarQuestao();
