# Sparkly

Plataforma web gamificada de **Física** para alunos e professores. O aluno resolve questões e acompanha seu desempenho em trilhas; o professor gerencia turmas, lições e questões.

---

## Visão geral

O projeto é uma aplicação web em **Flask** (Python) com frontend em **HTML/CSS/JavaScript puro** (sem framework JS) e banco de dados **SQLite**. A comunicação entre front e back é feita por uma **API JSON** (fetch) e o estado da sessão fica em cookies assinados (Flask session).

O fluxo principal:

1. **Tela inicial** apresenta o produto e oferece cadastro/login.
2. **Aluno** faz login, vê seu dashboard com estatísticas, resolve questões em trilhas e recebe nota/correção imediata.
3. **Professor** faz login, acessa um painel com turmas, lições e CRUD de questões (o modelo de questão também gera instâncias automaticamente).

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Flask 3 (factory `create_app()` + Blueprints) |
| ORM | Flask-SQLAlchemy |
| Banco de dados | SQLite (`sqlite:///sparkly.db` em `instance/`) |
| Frontend | HTML, CSS puro (`sparkly.css` + CSS por página), JavaScript (fetch) |
| Configuração | `python-dotenv` (variáveis de ambiente) |
| Segurança | Hash de senha `scrypt` (`werkzeug.security`) |
| Testes | pytest |

---

## Estrutura do projeto

```
sparkly-ppa/
├── sparkly.py              # Entrypoint: cria a app e inicia o servidor (debug, porta 5000)
├── init_db.py              # Script fino: popula o banco com questões iniciais
├── test_app.py             # Script de verificação manual (importa a app e testa conexão)
├── requirements.txt        # Dependências de execução
├── requirements-dev.txt    # Dependências de desenvolvimento (pytest)
├── pytest.ini              # Configuração do pytest (pythonpath = ., testpaths = tests)
├── README.md               # Este documento
├── REFATORACAO.md          # Plano e registro da refatoração
├── instance/               # Pasta onde o SQLite cria o arquivo sparkly.db
├── app/
│   ├── __init__.py         # create_app(): fábrica que monta a app (banco, rotas, CLI seed)
│   ├── config.py           # Configurações centralizadas (SQLite, SECRET_KEY)
│   ├── gamificacao.py      # Constantes da gamificação (corações, pontos, missões)
│   ├── models/             # Pacote de modelos (tabelas), um arquivo por domínio
│   │   ├── __init__.py     # Define o `db` e importa todos os modelos
│   │   ├── aluno.py        # Aluno
│   │   ├── professor.py    # Professor
│   │   ├── materia.py      # Materia (turmas)
│   │   ├── licao.py        # Licao
│   │   ├── questao.py      # ModeloQuestao + QuestaoInstanciada
│   │   ├── desempenho.py   # Desempenho
│   │   └── mensagem.py     # Mensagem
│   ├── services/           # Camada de serviços: lógica de negócio
│   │   ├── auth_service.py     # Login de aluno e professor (hash de senha)
│   │   ├── aluno_service.py    # Dados do aluno, cadastro
│   │   ├── professor_service.py# Turmas, CRUD de questões, sincronizar instâncias
│   │   ├── questao_service.py  # Interpolação, avaliação de resposta, desempenho, gamificação
│   │   └── gamificacao_service.py # Missões (XP), ranking e loja (recarga de corações)
│   ├── routes/             # Blueprints: rotas "finas" (só chamam os serviços)
│   │   ├── __init__.py     # register_routes(): registra os blueprints
│   │   ├── paginas.py      # Páginas HTML (sem prefixo)
│   │   ├── aluno.py        # API do aluno (prefixo /api)
│   │   └── professor.py    # API do professor (prefixo /api/professor)
│   ├── seed.py             # Questões iniciais + função seed_questoes()
│   ├── static/
│   │   ├── sparkly.css     # Folha de estilo base do projeto
│   │   ├── css/            # CSS por página (extraído dos templates)
│   │   └── js/
│   │       ├── gamificacao.js  # Utilitário compartilhado (badges de corações/pontos na navbar)
│   │       └── ...             # Demais scripts, um por página
│   └── templates/          # Templates HTML (sem CSS/JS inline)
│       ├── tela-inicial.html
│       ├── cadastro.html
│       ├── login.html
│       ├── aluno-dashboard.html
│       ├── aluno-trilhas.html
│       ├── aluno-desafio.html
│       ├── aluno-missoes.html      # Missões (metas de XP)
│       ├── aluno-ranking.html      # Ranking geral por pontos
│       ├── aluno-loja.html         # Loja: recarregar corações com pontos
│       └── professor-dashboard.html
└── tests/                  # Suíte pytest dos services
    ├── conftest.py             # Fixtures (app de teste com banco temporário)
    ├── test_questao_service.py
    ├── test_auth_service.py
    ├── test_aluno_service.py
    ├── test_professor_service.py
    └── test_gamificacao_service.py
```

---

## Modelo de dados

As tabelas são definidas em `app/models/` via SQLAlchemy.

| Tabela | Classe | Campos principais |
|---|---|---|
| `aluno` | `Aluno` | `id_aluno`, `nome_completo`, `email` (unique), `usuario` (unique), `senha` (hash), `pontos`, `coracoes` |
| `professor` | `Professor` | `id_professor`, `nome_completo`, `email`, `usuario`, `senha` (hash) |
| `materia` | `Materia` | `id_materia`, `nome_materia`, `numero_sala`, `id_professor` (FK) |
| `licao` | `Licao` | `id_licao`, `tipo`, `descricao`, `nota`, `id_materia` (FK) |
| `modelo_questao` | `ModeloQuestao` | `id`, `nome`, `tipo`, `conteudo` (JSON) |
| `questao_instanciada` | `QuestaoInstanciada` | `id`, `modelo_id` (FK), `valores_variaveis` (JSON) |
| `desempenho` | `Desempenho` | `id_desempenho`, `id_aluno` (FK), `id_atividade` (FK), `nota`, `status` |
| `mensagem` | `Mensagem` | `id_mensagem`, `tipo_remetente`, `id_remetente`, `tipo_destinatario`, `id_destinatario`, `conteudo`, `data_envio` |

### Modelo de questão (questões dinâmicas)

O projeto separa **modelo** de **instância** de questão:

- `modelo_questao` guarda o conteúdo **mestre** (enunciado, alternativas, gabarito) em um campo JSON.
- `questao_instanciada` representa a questão "entregue" ao aluno e pode guardar `valores_variaveis` usados para **interpolar variáveis** no enunciado (ex.: `{{ valor }}` vira um número concreto).

Quando o professor cria uma questão, o sistema **automaticamente gera uma instância** (`professor_service.criar_questao`), e existe um endpoint para sincronizar instâncias em massa (`/api/professor/sincronizar-instancias`).

---

## Gamificação (corações, pontos e missões)

Inspirado no modelo de vidas/XP do Duolingo, o Sparkly usa um sistema de **corações** (vidas) e **pontos** (XP) para engajar o aluno. As constantes ficam centralizadas em `app/gamificacao.py`:

| Constante | Valor padrão | Descrição |
|---|---|---|
| `MAX_CORACOES` | 5 | Corações máximos que o aluno pode ter |
| `PONTOS_POR_QUESTAO` | 10 | XP ganho ao acertar uma questão |
| `PONTOS_PARA_RECARGA` | 10 | Custo em XP para recarregar os corações na loja |
| `MISSOES` | `[20, 50, 100, 250, 500, 1000]` | Metas de XP exibidas na tela de Missões |

### Regras de corações

A lógica vive em `questao_service.registrar_resposta` e segue o mesmo princípio do Duolingo: uma questão **já concluída** (acertada antes) pode ser **praticada de graça**.

- **Questão nova** (nunca concluída):
  - Acertar → ganha `PONTOS_POR_QUESTAO` XP.
  - Errar → perde 1 coração.
  - Se o aluno estiver com **0 corações**, a resposta é bloqueada (`403`) até recarregar.
- **Questão em prática** (já concluída antes):
  - Acertar → ganha XP novamente **e** devolve 1 coração (até o máximo).
  - Errar → nada acontece (sem perda de coração, sem alteração de nota).
  - Pode ser respondida mesmo com 0 corações.

`listar_questoes_do_aluno` expõe `ja_concluida` (acertou antes) e `bloqueada` (sem corações e ainda não concluída), usados pelo frontend para exibir o cadeado nas questões novas.

### Telas de gamificação

| Página | Rota | Descrição |
|---|---|---|
| Missões | `/aluno-missoes` | Progresso do aluno em relação às metas de XP (`MISSOES`) |
| Ranking | `/aluno-ranking` | Top alunos por pontos, com destaque para o usuário logado |
| Loja | `/aluno-loja` | Recarregar corações gastando `PONTOS_PARA_RECARGA` pontos |

Os corações (❤️) e pontos (⭐) do aluno aparecem na navbar de todas as páginas internas, sincronizados via `app/static/js/gamificacao.js`.

---

## Rotas

### Páginas (Blueprints: `paginas`)

| Rota | Descrição |
|---|---|
| `/` e `/tela-inicial` | Landing page |
| `/cadastro` | Formulário de cadastro |
| `/login` | Login de aluno/professor |
| `/aluno-dashboard` | Dashboard do aluno |
| `/aluno-trilhas` | Trilhas/questões do aluno |
| `/aluno-desafio` | Tela de resolução de questão |
| `/aluno-missoes` | Missões (metas de XP) |
| `/aluno-ranking` | Ranking geral por pontos |
| `/aluno-loja` | Loja (recarregar corações) |
| `/professor-dashboard` | Painel do professor |

### API — Aluno (Blueprint `aluno`, prefixo `/api`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/login` | Autentica aluno e grava `aluno_id` na sessão |
| GET | `/api/aluno` | Dados completos do aluno autenticado (desempenho + lições + gamificação) |
| POST | `/api/cadastro` | Cria conta de aluno (valida duplicidade e gera hash de senha) |
| GET | `/api/aluno/questoes` | Lista questões instanciadas com enunciado interpolado, gabarito oculto e estado de bloqueio |
| POST | `/api/aluno/questoes/<id>/responder` | Recebe a resposta, avalia, atualiza pontos/corações e grava no `desempenho` |
| GET | `/api/aluno/missoes` | Lista as missões (metas de XP) com o progresso do aluno |
| GET | `/api/aluno/ranking` | Top 10 alunos por pontos |
| POST | `/api/aluno/loja/recarregar` | Gasta pontos para recarregar os corações ao máximo |

### API — Professor (Blueprint `professor`, prefixo `/api/professor`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/professor/login` | Autentica professor e grava `professor_id` na sessão |
| POST | `/api/professor/logout` | Encerra a sessão do professor |
| GET | `/api/professor/turmas` | Lista turmas (matérias) com total de lições e alunos |
| GET | `/api/professor/turmas/<materia_id>` | Detalhe da turma (lições + alunos com média) |
| GET | `/api/professor/questoes` | Lista todas as questões-modelo |
| POST | `/api/professor/questoes` | Cria questão-modelo e sua instância |
| PUT | `/api/professor/questoes/<id>` | Edita questão-modelo |
| DELETE | `/api/professor/questoes/<id>` | Exclui questão-modelo |
| POST | `/api/professor/sincronizar-instancias` | Gera instâncias para modelos que ainda não têm nenhuma |

---

## Fluxo de autenticação

- A lógica fica em `app/services/auth_service.py` (`validar_login`, `validar_login_professor`).
- As senhas são armazenadas com **hash `scrypt`** (Werkzeug). Se o banco tiver senha legada em texto puro, o **primeiro login converte automaticamente** para hash.
- A sessão guarda o ID (`aluno_id` / `professor_id`) e um dicionário do usuário.
- As rotas de API exigem autenticação; retornam `401` quando a sessão está ausente.

### Avaliação de questões (`/api/aluno/questoes/<id>/responder`)

- `multipla-escolha`, `multi-selecao`, `multipla_escolha`, `verdadeiro_falso` → compara a resposta (índice) com o `gabarito`.
- Outros tipos (`entrada-texto`/dissertativa) → comparação textual normalizada (`lower`/`strip`).
- Nota: `10.0` se correto, `0.0` caso contrário. Status: `Concluida` ou `Pendente`.
- Se já existe um `desempenho` para aquele aluno+atividade, ele é atualizado; senão, é criado.

---

## Como rodar

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux/macOS (no Windows: .venv\Scripts\activate)
   pip install -r requirements.txt
   ```

2. (Opcional) Defina uma chave secreta no `.env` (na raiz):

   ```env
   SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria
   ```

   Sem `.env` o projeto roda com valores de desenvolvimento. O banco SQLite é criado automaticamente em `instance/sparkly.db` ao subir a app (tabelas são criadas via `db.create_all()`).

3. (Opcional) Popule o banco com as questões iniciais de Física e os usuários padrão de teste:

   ```bash
   python init_db.py          # ou: flask seed (Se um arquivo chamado "sparkly.db" já estiver criado, apague-o e rode o comando novamente, isso evita que ocorra erros de popularização)
   ```

   Isso cria, além do banco de questões, os seguintes usuários de teste (todas as senhas são fixas e servem só para desenvolvimento — **não usar em produção**):

   | Papel | Usuários | Senha |
   |---|---|---|
   | Aluno | `anthony_keyvson`, `joao_martins`, `igor_filho`, `daniel_abreu`, `giovane_arlindo`, `caike_luan`, `caio_cavalcante` | `ALUNO123` |
   | Professor | `villa_lp`, `lazaro_web`, `irlan_fisica`, `juliana_onq`, `kenia_sociologia`, `william_portugues` | `PROFESSOR123` |

   Os e-mails são gerados automaticamente no formato `<usuario>@sparkly.local`.

4. Inicie o servidor:

   ```bash
   python sparkly.py
   ```

   A aplicação sobe em `http://localhost:5000` (modo debug).

---

## Testes

Suíte `pytest` para os services (avaliação de resposta, interpolação, hash/login, cadastro, CRUD de questões):

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam um banco SQLite temporário isolado (`tests/conftest.py`).

Há também `test_app.py`, um script manual de verificação (importa a app, testa a conexão e sobe o servidor):

```bash
python test_app.py
```

---

## Observações e melhorias futuras

- **`SECRET_KEY`** tem fallback para um valor de desenvolvimento — obrigatório definir via `.env` em produção.
- **Validação de sessão** — as APIs dependem apenas da sessão Flask; falta proteção CSRF e expiração de sessão.
- **`db.create_all()`** cria as tabelas ao subir, mas não versiona mudanças de schema — se o schema evoluir, considere adotar migrações (Alembic/Flask-Migrate).
- **Avaliação de questões** é binária (certo/errado) — dá para evoluir para notas parciais por tipo de questão.
