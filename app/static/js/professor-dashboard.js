  const LETRAS = ['A','B','C','D','E','F','G','H'];
  let questoesCache = [];
  let licoesCache = [];
  let turmaAtualId = null;

  async function carregarLicoesParaSelects() {
    try {
      const r = await fetch('/api/professor/licoes');
      const data = await r.json();
      if (!data.sucesso) return;
      licoesCache = data.licoes;
      const opts = '<option value="">Sem lição</option>' +
        licoesCache.map(l => `<option value="${l.id}">${l.turma} · ${l.modulo} · ${l.nome}</option>`).join('');
      document.getElementById('q-licao').innerHTML = opts;
      document.getElementById('edit-licao').innerHTML = opts;
    } catch (e) { /* select fica só com "Sem lição" */ }
  }

  const profSS = JSON.parse(sessionStorage.getItem('professor')||'null');
  if (!profSS) {
    fetch('/api/professor/turmas').then(r=>{if(r.status===401)window.location.href='/login';}).catch(()=>window.location.href='/login');
  } else {
    const nome = profSS.nome||profSS.nome_completo||'Professor';
    document.getElementById('professorNome').textContent = nome;
    document.getElementById('professorAvatar').textContent = nome.charAt(0).toUpperCase();
  }

  function showSection(id) {
    document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
    document.getElementById('sec-'+id).classList.add('active');
    document.getElementById('nav-'+id).classList.add('active');
    if(id==='turmas')  carregarTurmas();
    if(id==='questoes') carregarQuestoes();
  }

  function toast(msg, tipo='success') {
    const t = document.getElementById('toast');
    t.textContent = msg; t.className = 'show '+tipo;
    setTimeout(()=>{t.className='';},3500);
  }

  async function carregarTurmas() {
    const grid = document.getElementById('turmasGrid');
    grid.innerHTML = '<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando...</div>';
    try {
      const r = await fetch('/api/professor/turmas');
      if(r.status===401){window.location.href='/login';return;}
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      renderTurmas(data.turmas);
    } catch(e) {
      grid.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function renderTurmas(turmas) {
    const grid = document.getElementById('turmasGrid');
    document.getElementById('stat-turmas').textContent = turmas.length;
    document.getElementById('stat-licoes').textContent = turmas.reduce((s,t)=>s+t.total_licoes,0);
    document.getElementById('stat-alunos').textContent = turmas.reduce((s,t)=>s+t.total_alunos,0);
    if(!turmas.length){
      grid.innerHTML=`<div class="empty-state" style="grid-column:1/-1"><div class="em-icon">📭</div><div class="em-text">Nenhuma turma encontrada.</div></div>`;
      return;
    }
    grid.innerHTML = turmas.map(t=>`
      <div class="turma-card" onclick="verTurma(${t.id})">
        <div class="t-header">
          <div class="t-nome">${t.nome}</div>
          <div class="t-sala">Sala ${t.numero_sala||'—'}</div>
        </div>
        <div class="t-codigo" onclick="copiarCodigoTurma(event,'${t.codigo_turma||''}')" title="Copiar código da turma">
          <span class="t-codigo-label">Código</span>
          <span class="t-codigo-valor">${t.codigo_turma||'—'}</span>
          <span class="t-codigo-icon">📋</span>
        </div>
        <div class="t-stats">
          <div class="t-stat"><div class="ts-num">${t.total_licoes}</div><div class="ts-label">Lições</div></div>
          <div class="t-stat"><div class="ts-num">${t.total_alunos}</div><div class="ts-label">Alunos</div></div>
        </div>
        <button class="btn btn-outline btn-sm btn-full mt-2">Ver turma →</button>
      </div>`).join('');
  }

  function copiarCodigoTurma(ev, codigo) {
    ev.stopPropagation();
    if(!codigo) return;
    navigator.clipboard?.writeText(codigo).then(()=>{
      toast('Código copiado! ✓');
    }).catch(()=>{ toast('Não foi possível copiar o código','error'); });
  }

  async function verTurma(id) {
    turmaAtualId = id;
    document.getElementById('turmasGrid').style.display='none';
    document.getElementById('statsRow').style.display='none';
    document.getElementById('turmasToolbar').style.display='none';
    const det = document.getElementById('turmaDetalhe');
    det.innerHTML='<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando detalhes...</div>';
    det.style.display='block';
    try {
      const r = await fetch(`/api/professor/turmas/${id}`);
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      renderDetalhe(data);
    } catch(e) {
      det.innerHTML=`<button class="back-btn" onclick="fecharDetalhe()">← Voltar</button>
        <div class="empty-state"><div class="em-icon"></div><div class="em-text">${e.message}</div></div>`;
    }
  }

  function renderDetalhe(data) {
    const det = document.getElementById('turmaDetalhe');
    const {turma,modulos,alunos} = data;
    const notaClass  = v => v>=7?'nota-alta':v>=5?'nota-media':'nota-baixa';
    det.innerHTML = `
      <button class="back-btn" onclick="fecharDetalhe()">← Voltar às turmas</button>
      <div class="page-title mb-1">${turma.nome}</div>
      <div class="page-sub mb-3">Sala ${turma.numero_sala||'—'} · ID ${turma.id}</div>
      <div class="codigo-turma-box" onclick="copiarCodigoTurma(event,'${turma.codigo_turma||''}')" title="Copiar código da turma">
        <div>
          <div class="ctb-label">Código da turma <span class="ctb-hint">(visível só para você — compartilhe com seus alunos)</span></div>
          <div class="ctb-valor">${turma.codigo_turma||'—'}</div>
        </div>
        <span class="btn btn-outline btn-sm">📋 Copiar</span>
      </div>
      <div class="detalhe-grid">
        <div class="panel">
          <div class="panel-title">
            <span> Módulos e Lições</span>
            <button class="btn btn-outline btn-sm" onclick="abrirModalNovoModulo(${turma.id})">+ Módulo</button>
          </div>
          ${modulos.length===0
            ? '<div class="empty-state" style="padding:20px"><div class="em-icon"></div><div class="em-text">Nenhum módulo cadastrado</div></div>'
            : modulos.map(mo=>`
                <div class="modulo-bloco">
                  <div class="modulo-header">
                    <div class="modulo-nome">${mo.nome}</div>
                    <div class="modulo-actions">
                      <button class="btn-icon edit" onclick="abrirModalEditarModulo(${mo.id},'${(mo.nome||'').replace(/'/g,"\\'")}',${JSON.stringify(mo.descricao||'')})" title="Editar módulo">✏️</button>
                      <button class="btn-icon danger" onclick="deletarModulo(${mo.id},'${(mo.nome||'').replace(/'/g,"\\'")}')" title="Excluir módulo">🗑</button>
                      <button class="btn btn-outline btn-sm" onclick="abrirModalNovaLicao(${mo.id})">+ Lição</button>
                    </div>
                  </div>
                  ${mo.descricao ? `<div class="modulo-descricao">${mo.descricao}</div>` : ''}
                  ${mo.licoes.length===0
                    ? '<div class="empty-state" style="padding:14px"><div class="em-text">Nenhuma lição neste módulo</div></div>'
                    : `<table class="table">
                        <thead><tr><th>Lição</th><th>Descrição</th><th>Questões</th><th></th></tr></thead>
                        <tbody>${mo.licoes.map(li=>`
                          <tr>
                            <td>${li.nome}</td>
                            <td>${li.descricao||'—'}</td>
                            <td>${li.total_questoes}</td>
                            <td>
                              <div class="questao-actions">
                                <button class="btn-icon edit" onclick="abrirModalEditarLicao(${li.id},'${(li.nome||'').replace(/'/g,"\\'")}',${JSON.stringify(li.descricao||'')})" title="Editar lição">✏️</button>
                                <button class="btn-icon danger" onclick="deletarLicao(${li.id},'${(li.nome||'').replace(/'/g,"\\'")}')" title="Excluir lição">🗑</button>
                              </div>
                            </td>
                          </tr>`).join('')}
                        </tbody></table>`}
                </div>`).join('')}
        </div>
        <div class="panel">
          <div class="panel-title"><span>👥 Alunos</span><span class="badge badge-green">${alunos.length}</span></div>
          ${alunos.length===0
            ? '<div class="empty-state" style="padding:20px"><div class="em-icon">👥</div><div class="em-text">Nenhum aluno nesta turma</div></div>'
            : `<table class="table">
                <thead><tr><th>Nome</th><th>Usuário</th><th>Média</th></tr></thead>
                <tbody>${alunos.map(a=>`
                  <tr>
                    <td>${a.nome}</td>
                    <td class="text-muted">@${a.usuario}</td>
                    <td class="${notaClass(a.media)}">${a.media}</td>
                  </tr>`).join('')}
                </tbody></table>`}
        </div>
      </div>`;
  }

  function fecharDetalhe() {
    turmaAtualId = null;
    document.getElementById('turmaDetalhe').style.display='none';
    document.getElementById('turmasGrid').style.display='grid';
    document.getElementById('statsRow').style.display='grid';
    document.getElementById('turmasToolbar').style.display='flex';
    carregarTurmas();
  }

  // ── Turmas ─────────────────────────────────────────────────────────

  function abrirModalNovaTurma() {
    document.getElementById('turma-nome').value='';
    document.getElementById('turma-sala').value='';
    document.getElementById('modalTurma').classList.add('active');
  }
  function fecharModalTurma() { document.getElementById('modalTurma').classList.remove('active'); }

  async function salvarTurma() {
    const nome = document.getElementById('turma-nome').value.trim();
    const numero_sala = document.getElementById('turma-sala').value.trim();
    if(!nome){toast('Informe o nome da turma','error');return;}
    try {
      const r = await fetch('/api/professor/turmas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,numero_sala})});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast('Turma criada! ✓'); fecharModalTurma(); carregarTurmas();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  // ── Módulos ────────────────────────────────────────────────────────

  function abrirModalNovoModulo(materiaId) {
    document.getElementById('modulo-modal-titulo').textContent='Novo Módulo';
    document.getElementById('modulo-id').value='';
    document.getElementById('modulo-materia-id').value=materiaId;
    document.getElementById('modulo-nome').value='';
    document.getElementById('modulo-descricao').value='';
    document.getElementById('modalModulo').classList.add('active');
  }
  function abrirModalEditarModulo(id, nome, descricao) {
    document.getElementById('modulo-modal-titulo').textContent='Editar Módulo';
    document.getElementById('modulo-id').value=id;
    document.getElementById('modulo-materia-id').value='';
    document.getElementById('modulo-nome').value=nome;
    document.getElementById('modulo-descricao').value=descricao||'';
    document.getElementById('modalModulo').classList.add('active');
  }
  function fecharModalModulo() { document.getElementById('modalModulo').classList.remove('active'); }

  async function salvarModulo() {
    const id = document.getElementById('modulo-id').value;
    const materiaId = document.getElementById('modulo-materia-id').value;
    const nome = document.getElementById('modulo-nome').value.trim();
    const descricao = document.getElementById('modulo-descricao').value.trim();
    if(!nome){toast('Informe o nome do módulo','error');return;}
    try {
      const url = id ? `/api/professor/modulos/${id}` : `/api/professor/turmas/${materiaId}/modulos`;
      const r = await fetch(url,{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,descricao})});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast(id?'Módulo atualizado! ✓':'Módulo criado! ✓'); fecharModalModulo();
      if(turmaAtualId) verTurma(turmaAtualId);
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  async function deletarModulo(id, nome) {
    if(!confirm(`Excluir o módulo "${nome}"? As lições dentro dele também serão excluídas.`)) return;
    try {
      const r = await fetch(`/api/professor/modulos/${id}`,{method:'DELETE'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast('Módulo excluído! ✓');
      if(turmaAtualId) verTurma(turmaAtualId);
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  // ── Lições ─────────────────────────────────────────────────────────

  function abrirModalNovaLicao(moduloId) {
    document.getElementById('licao-modal-titulo').textContent='Nova Lição';
    document.getElementById('licao-id').value='';
    document.getElementById('licao-modulo-id').value=moduloId;
    document.getElementById('licao-nome').value='';
    document.getElementById('licao-descricao').value='';
    document.getElementById('modalLicao').classList.add('active');
  }
  function abrirModalEditarLicao(id, nome, descricao) {
    document.getElementById('licao-modal-titulo').textContent='Editar Lição';
    document.getElementById('licao-id').value=id;
    document.getElementById('licao-modulo-id').value='';
    document.getElementById('licao-nome').value=nome;
    document.getElementById('licao-descricao').value=descricao||'';
    document.getElementById('modalLicao').classList.add('active');
  }
  function fecharModalLicao() { document.getElementById('modalLicao').classList.remove('active'); }

  async function salvarLicao() {
    const id = document.getElementById('licao-id').value;
    const moduloId = document.getElementById('licao-modulo-id').value;
    const nome = document.getElementById('licao-nome').value.trim();
    const descricao = document.getElementById('licao-descricao').value.trim();
    if(!nome){toast('Informe o nome da lição','error');return;}
    try {
      const url = id ? `/api/professor/licoes/${id}` : `/api/professor/modulos/${moduloId}/licoes`;
      const r = await fetch(url,{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,descricao})});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast(id?'Lição atualizada! ✓':'Lição criada! ✓'); fecharModalLicao();
      if(turmaAtualId) verTurma(turmaAtualId);
      carregarLicoesParaSelects();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  async function deletarLicao(id, nome) {
    if(!confirm(`Excluir a lição "${nome}"?`)) return;
    try {
      const r = await fetch(`/api/professor/licoes/${id}`,{method:'DELETE'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast('Lição excluída! ✓');
      if(turmaAtualId) verTurma(turmaAtualId);
      carregarLicoesParaSelects();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  async function carregarQuestoes() {
    const list = document.getElementById('questoesList');
    list.innerHTML='<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando...</div>';
    try {
      const r = await fetch('/api/professor/questoes');
      if(r.status===401){window.location.href='/login';return;}
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      questoesCache = data.questoes;
      renderQuestoes(data.questoes);
    } catch(e) {
      list.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">${e.message}</div></div>`;
    }
  }

  const TIPO_LABEL = {'multipla-escolha':'Múltipla Escolha','multi-selecao':'Múltipla Seleção','entrada-texto':'Dissertativa'};

  function renderQuestoes(questoes) {
    const list = document.getElementById('questoesList');
    if(!questoes.length){
      list.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">Nenhuma questão. Crie a primeira!</div></div>`;
      return;
    }
    list.innerHTML = questoes.map(q=>`
      <div class="questao-item">
        <div class="questao-info">
          <div class="q-nome">${q.nome}</div>
          <div class="q-tipo">${TIPO_LABEL[q.tipo]||q.tipo}</div>
        </div>
        <div class="questao-actions">
          <button class="btn-icon info" onclick="verQuestao(${q.id})" title="Ver">👁</button>
          <button class="btn-icon edit" onclick="editarQuestao(${q.id})" title="Editar">✏️</button>
          <button class="btn-icon danger" onclick="deletarQuestao(${q.id},'${q.nome.replace(/'/g,"\\'")}')">🗑</button>
        </div>
      </div>`).join('');
  }

  function verQuestao(id) {
    const q = questoesCache.find(x=>x.id===id); if(!q) return;
    document.getElementById('verQ-nome').textContent = q.nome;
    document.getElementById('verQ-tipo').textContent = TIPO_LABEL[q.tipo]||q.tipo;
    const c = q.conteudo||{};
    let html = `<div style="font-weight:700;margin-bottom:10px;">${c.enunciado||c.texto_base||'—'}</div>`;
    if(c.alternativas?.length) {
      html += c.alternativas.map((alt,i)=>
        `<div class="alt ${i===c.gabarito?'correta':''}">${LETRAS[i]}) ${alt} ${i===c.gabarito?'✓':''}</div>`).join('');
    } else if(c.gabarito!==undefined&&c.gabarito!==null&&c.gabarito!=='') {
      html+=`<div style="margin-top:10px;font-weight:700;">Gabarito: ${c.gabarito}</div>`;
    }
    document.getElementById('verQ-conteudo').innerHTML = html;
    document.getElementById('modalVerQuestao').classList.add('active');
  }
  function fecharVerQuestao() { document.getElementById('modalVerQuestao').classList.remove('active'); }

  async function deletarQuestao(id, nome) {
    if(!confirm(`Excluir "${nome}"?`)) return;
    try {
      const r = await fetch(`/api/professor/questoes/${id}`,{method:'DELETE'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast('Questão excluída! ✓'); carregarQuestoes();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  function abrirModalNovaQuestao() {
    carregarLicoesParaSelects();
    document.getElementById('q-nome').value='';
    document.getElementById('q-enunciado').value='';
    document.getElementById('q-gabarito').value='';
    document.getElementById('q-tipo').value='multipla-escolha';
    resetAlternativas(); tipoChanged();
    document.getElementById('modalQuestao').classList.add('active');
  }
  function fecharModal() { document.getElementById('modalQuestao').classList.remove('active'); }

  function tipoChanged() {
    const tipo = document.getElementById('q-tipo').value;
    document.getElementById('bloco-alternativas').style.display = tipo==='entrada-texto'?'none':'block';
    document.getElementById('bloco-gabarito').style.display    = tipo==='entrada-texto'?'block':'none';
    if(tipo!=='entrada-texto') resetAlternativas();
  }

  function resetAlternativas() {
    const c = document.getElementById('alternativas-container');
    c.innerHTML = ['A','B','C','D'].map((l,i)=>`
      <div class="alternativa-row">
        <input type="radio" name="gabarito" value="${i}">
        <label>${l}</label>
        <input type="text" placeholder="Texto da alternativa ${l}">
      </div>`).join('');
  }

  function adicionarAlternativa() {
    const c = document.getElementById('alternativas-container');
    const idx = c.children.length; if(idx>=8){toast('Máximo 8 alternativas','error');return;}
    const l = LETRAS[idx];
    const div = document.createElement('div'); div.className='alternativa-row';
    div.innerHTML=`<input type="radio" name="gabarito" value="${idx}"> <label>${l}</label><input type="text" placeholder="Alternativa ${l}">`;
    c.appendChild(div);
  }

  async function salvarQuestao() {
    const nome = document.getElementById('q-nome').value.trim();
    const tipo = document.getElementById('q-tipo').value;
    const enunciado = document.getElementById('q-enunciado').value.trim();
    if(!nome){toast('Informe o nome','error');return;}
    if(!enunciado){toast('Informe o enunciado','error');return;}
    let conteudo = {enunciado};
    if(tipo!=='entrada-texto') {
      const rows = document.querySelectorAll('#alternativas-container .alternativa-row');
      const alternativas=[]; let gabarito=null;
      rows.forEach((row,i)=>{
        const radio=row.querySelector('input[type=radio]');
        const txt=row.querySelector('input[type=text]').value.trim();
        alternativas.push(txt||`Alternativa ${LETRAS[i]}`);
        if(radio?.checked) gabarito=i;
      });
      if(gabarito===null){toast('Marque a alternativa correta','error');return;}
      conteudo.alternativas=alternativas; conteudo.gabarito=gabarito;
    } else {
      conteudo.gabarito=document.getElementById('q-gabarito').value.trim();
    }
    const id_licao = document.getElementById('q-licao').value || null;
    try {
      const r = await fetch('/api/professor/questoes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,tipo,conteudo,id_licao})});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast('Questão criada! ✓'); fecharModal(); carregarQuestoes();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  async function sincronizarInstancias() {
    try {
      const r = await fetch('/api/professor/sincronizar-instancias',{method:'POST'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast(data.instancias_criadas===0 ? 'Tudo já sincronizado ✓' : `${data.instancias_criadas} questão(ões) sincronizadas! ✓`);
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  function editarQuestao(id) {
    carregarLicoesParaSelects();
    const q = questoesCache.find(x=>x.id===id); if(!q) return;
    document.getElementById('edit-id').value=q.id;
    document.getElementById('edit-nome').value=q.nome;
    document.getElementById('edit-enunciado').value=q.conteudo?.enunciado||q.conteudo?.texto_base||'';
    document.getElementById('edit-tipo').value=q.tipo;
    editTipoChanged();
    const c = q.conteudo||{};
    if(q.tipo!=='entrada-texto') {
      const alts=c.alternativas||[];
      const container=document.getElementById('edit-alternativas-container');
      container.innerHTML='';
      const lista=alts.length?alts:['','','',''];
      lista.forEach((texto,i)=>{
        const div=document.createElement('div'); div.className='alternativa-row';
        div.innerHTML=`<input type="radio" name="edit-gabarito" value="${i}" ${i===c.gabarito?'checked':''}> <label>${LETRAS[i]}</label><input type="text" value="${texto}" placeholder="Alternativa ${LETRAS[i]}">`;
        container.appendChild(div);
      });
    } else {
      document.getElementById('edit-gabarito').value=c.gabarito||'';
    }
    document.getElementById('modalEditarQuestao').classList.add('active');
  }
  function fecharEditarQuestao() { document.getElementById('modalEditarQuestao').classList.remove('active'); }
  function editTipoChanged() {
    const tipo=document.getElementById('edit-tipo').value;
    document.getElementById('edit-bloco-alternativas').style.display=tipo==='entrada-texto'?'none':'block';
    document.getElementById('edit-bloco-gabarito').style.display=tipo==='entrada-texto'?'block':'none';
  }
  function editAdicionarAlternativa() {
    const c=document.getElementById('edit-alternativas-container');
    const idx=c.children.length; if(idx>=8){toast('Máximo 8','error');return;}
    const div=document.createElement('div'); div.className='alternativa-row';
    div.innerHTML=`<input type="radio" name="edit-gabarito" value="${idx}"> <label>${LETRAS[idx]}</label><input type="text" placeholder="${LETRAS[idx]}">`;
    c.appendChild(div);
  }
  async function salvarEdicao() {
    const id=parseInt(document.getElementById('edit-id').value);
    const nome=document.getElementById('edit-nome').value.trim();
    const tipo=document.getElementById('edit-tipo').value;
    const enunciado=document.getElementById('edit-enunciado').value.trim();
    if(!nome){toast('Informe o nome','error');return;}
    if(!enunciado){toast('Informe o enunciado','error');return;}
    let conteudo={enunciado};
    if(tipo!=='entrada-texto') {
      const rows=document.querySelectorAll('#edit-alternativas-container .alternativa-row');
      const alternativas=[]; let gabarito=null;
      rows.forEach((row,i)=>{
        const radio=row.querySelector('input[type=radio]');
        const txt=row.querySelector('input[type=text]').value.trim();
        alternativas.push(txt||`Alternativa ${LETRAS[i]}`);
        if(radio.checked) gabarito=i;
      });
      if(gabarito===null){toast('Marque a alternativa correta','error');return;}
      conteudo.alternativas=alternativas; conteudo.gabarito=gabarito;
    } else {
      conteudo.gabarito=document.getElementById('edit-gabarito').value.trim();
    }
    const id_licao = document.getElementById('edit-licao').value || null;
    try {
      const r=await fetch(`/api/professor/questoes/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,tipo,conteudo,id_licao})});
      const data=await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast('Questão atualizada! ✓'); fecharEditarQuestao(); carregarQuestoes();
    } catch(e){ toast('Erro: '+e.message,'error'); }
  }

  async function sair() {
    await fetch('/api/professor/logout',{method:'POST'}).catch(()=>{});
    sessionStorage.removeItem('professor'); sessionStorage.removeItem('professor_id');
    window.location.href='/login';
  }

  carregarTurmas();
  carregarLicoesParaSelects();
