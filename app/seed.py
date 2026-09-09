"""Dados iniciais do banco: questões de Física (Eletricidade).

Uso (a tabela é criada automaticamente ao subir a app):
    python init_db.py          # script fino na raiz
    flask seed                 # ou via CLI do Flask
"""
from werkzeug.security import generate_password_hash

from app.models import db, ModeloQuestao, QuestaoInstanciada, Professor, Materia, Modulo, Licao, Aluno

# Nomes das lições, na ordem, com a quantidade de questões (consecutivas em
# QUESTOES_INICIAIS) que cada uma agrupa. Isso organiza o banco de questões
# no esquema Módulo → Lição → Questão (mesma ideia do Duolingo).
LICOES_TOPICOS = [
    ("Processos de Eletrização", 7),
    ("Força e Campo Elétrico", 5),
    ("Indução Magnética", 2),
    ("Potencial Elétrico", 4),
    ("Eletrodinâmica I", 5),
    ("Associação de Resistores", 5),
    ("Capacitores", 5),
    ("Medidores, Geradores e Leis de Kirchhoff", 8),
]

NOME_MODULO = "Eletricidade e Magnetismo"
NOME_MATERIA = "Física"
NOME_PROFESSOR_PADRAO = "Professor Sparkly"
USUARIO_PROFESSOR_PADRAO = "professor"
SENHA_PROFESSOR_PADRAO = "professor123"

# ──────────────────────────────────────────────
#  Usuários padrão de teste (alunos e professores)
#  Senha única por papel, apenas para ambiente de teste/demonstração.
# ──────────────────────────────────────────────
SENHA_ALUNO_PADRAO = "ALUNO123"
SENHA_PROFESSOR_TESTE = "PROFESSOR123"

ALUNOS_PADRAO = [
    {"usuario": "anthony_keyvson", "nome_completo": "Anthony Keyvson", "email": "anthony_keyvson@sparkly.local"},
    {"usuario": "joao_martins", "nome_completo": "João Martins", "email": "joao_martins@sparkly.local"},
    {"usuario": "igor_filho", "nome_completo": "Igor Filho", "email": "igor_filho@sparkly.local"},
    {"usuario": "daniel_abreu", "nome_completo": "Daniel Abreu", "email": "daniel_abreu@sparkly.local"},
    {"usuario": "giovane_arlindo", "nome_completo": "Giovane Arlindo", "email": "giovane_arlindo@sparkly.local"},
    {"usuario": "caike_luan", "nome_completo": "Caike Luan", "email": "caike_luan@sparkly.local"},
    {"usuario": "caio_cavalcante", "nome_completo": "Caio Cavalcante", "email": "caio_cavalcante@sparkly.local"},
]

PROFESSORES_PADRAO = [
    {"usuario": "villa_lp", "nome_completo": "Villa (Língua Portuguesa)", "email": "villa_lp@sparkly.local"},
    {"usuario": "lazaro_web", "nome_completo": "Lázaro (Web)", "email": "lazaro_web@sparkly.local"},
    {"usuario": "irlan_fisica", "nome_completo": "Irlan (Física)", "email": "irlan_fisica@sparkly.local"},
    {"usuario": "juliana_onq", "nome_completo": "Juliana (ONQ)", "email": "juliana_onq@sparkly.local"},
    {"usuario": "kenia_sociologia", "nome_completo": "Kênia (Sociologia)", "email": "kenia_sociologia@sparkly.local"},
    {"usuario": "william_portugues", "nome_completo": "William (Português)", "email": "william_portugues@sparkly.local"},
]

# ──────────────────────────────────────────────
#  Questões de Física no formato do banco atual
#  tipo deve ser um dos valores do ENUM:
#    'multipla-escolha' | 'multi-selecao' | 'entrada-texto'
#
#  conteudo JSON:
#    { enunciado, alternativas: [...], gabarito: <indice 0-based> }
#
#  Tópicos cobertos (conforme conteúdo programático):
#    - Processos de Eletrização / Conceitos Básicos de Eletromagnetismo
#    - Força e Campo Elétrico / Indução Magnética
#    - Potencial Elétrico
#    - Eletrodinâmica I (corrente, resistência, Lei de Ohm)
#    - Associação de Resistores
#    - Capacitores
#    - Eletrodinâmica II
#    - Medidores Elétricos, Geradores, Receptores e Leis de Kirchhoff
# ──────────────────────────────────────────────
QUESTOES_INICIAIS = [
    # ── Processos de Eletrização / Conceitos Básicos ──────────────
    {
        "nome": "Eletrização por Atrito — Carga do Bastão",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Quando atritamos um bastão de vidro com seda, o bastão fica com carga...",
            "alternativas": ["Negativa", "Positiva", "Neutra", "Depende da temperatura"],
            "gabarito": 1
        }
    },
    {
        "nome": "Eletrização por Atrito — Afinidade Eletrônica",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A eletrização por atrito ocorre pois corpos diferentes têm diferentes...",
            "alternativas": ["Massas atômicas", "Afinidades eletrônicas", "Cargas nucleares", "Pressões internas"],
            "gabarito": 1
        }
    },
    {
        "nome": "Eletrização por Contato — Carga Adquirida",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Na eletrização por contato, o corpo que toca o condutor eletrizado...",
            "alternativas": ["Perde toda a carga", "Adquire carga do mesmo sinal", "Adquire carga de sinal oposto", "Fica neutro"],
            "gabarito": 1
        }
    },
    {
        "nome": "Eletrização por Contato — Tipo de Material",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Para que a eletrização por contato ocorra de forma eficiente, os corpos devem ser preferencialmente...",
            "alternativas": ["Isolantes", "Condutores", "Magnéticos", "Radioativos"],
            "gabarito": 1
        }
    },
    {
        "nome": "Eletrização por Indução — Etapa do Aterramento",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Na eletrização por indução, ao aterrar o condutor neutro próximo a um bastão eletrizado (sem tocá-lo), o que ocorre?",
            "alternativas": [
                "O condutor perde os elétrons repelidos, ficando com carga oposta à do indutor",
                "O condutor fica com a mesma carga do bastão indutor",
                "Nenhuma carga é transferida",
                "O bastão perde toda a sua carga"
            ],
            "gabarito": 0
        }
    },
    {
        "nome": "Princípio da Conservação das Cargas",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O princípio da conservação das cargas elétricas afirma que, em um sistema isolado...",
            "alternativas": ["A carga total pode ser criada livremente", "A carga elétrica total permanece constante", "Toda carga positiva se transforma em negativa", "As cargas desaparecem com o tempo"],
            "gabarito": 1
        }
    },
    {
        "nome": "Condutores e Isolantes",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Materiais como o cobre e o alumínio são bons condutores de eletricidade porque possuem...",
            "alternativas": ["Elétrons livres em abundância", "Núcleos muito pesados", "Ausência total de elétrons", "Estrutura cristalina isolante"],
            "gabarito": 0
        }
    },
    # ── Força e Campo Elétrico ─────────────────────────────────────
    {
        "nome": "Lei de Coulomb — Força entre Cargas",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Segundo a Lei de Coulomb, a força elétrica entre duas cargas puntiformes é...",
            "alternativas": [
                "Diretamente proporcional ao produto das cargas e inversamente proporcional ao quadrado da distância",
                "Inversamente proporcional ao produto das cargas",
                "Independente da distância entre as cargas",
                "Diretamente proporcional ao cubo da distância"
            ],
            "gabarito": 0
        }
    },
    {
        "nome": "Campo Elétrico — Definição",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O campo elétrico em um ponto do espaço é definido como a força elétrica...",
            "alternativas": ["Multiplicada pela carga de prova", "Por unidade de carga de prova colocada nesse ponto", "Dividida pela distância ao quadrado", "Independente de qualquer carga de prova"],
            "gabarito": 1
        }
    },
    {
        "nome": "Linhas de Campo Elétrico",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "As linhas de campo elétrico ao redor de uma carga puntiforme positiva isolada são...",
            "alternativas": ["Radiais, apontando para dentro da carga", "Radiais, divergindo da carga", "Circulares ao redor da carga", "Paralelas entre si"],
            "gabarito": 1
        }
    },
    {
        "nome": "Campo Elétrico Uniforme",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Um campo elétrico é considerado uniforme quando suas linhas de campo são...",
            "alternativas": ["Curvas e convergentes", "Paralelas, igualmente espaçadas e de mesmo sentido", "Circulares e concêntricas", "Aleatórias em direção"],
            "gabarito": 1
        }
    },
    {
        "nome": "Unidade de Campo Elétrico",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "No Sistema Internacional, a unidade de medida do campo elétrico é...",
            "alternativas": ["N/C (newton por coulomb)", "J/C (joule por coulomb)", "C/N (coulomb por newton)", "W (watt)"],
            "gabarito": 0
        }
    },
    # ── Indução Magnética ──────────────────────────────────────────
    {
        "nome": "Indução Eletromagnética — Lei de Faraday",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Segundo a Lei de Faraday, uma força eletromotriz induzida surge em um circuito quando há...",
            "alternativas": ["Variação do fluxo magnético através do circuito", "Corrente elétrica constante no circuito", "Ausência total de campo magnético", "Resistência elétrica nula"],
            "gabarito": 0
        }
    },
    {
        "nome": "Lei de Lenz — Sentido da Corrente Induzida",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A Lei de Lenz estabelece que o sentido da corrente induzida é tal que...",
            "alternativas": ["Favorece a variação do fluxo magnético que a originou", "Se opõe à variação do fluxo magnético que a originou", "É sempre igual ao sentido do campo indutor", "Não depende do fluxo magnético"],
            "gabarito": 1
        }
    },
    # ── Potencial Elétrico ─────────────────────────────────────────
    {
        "nome": "Potencial Elétrico — Definição",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O potencial elétrico em um ponto é definido como a energia potencial elétrica por unidade de...",
            "alternativas": ["Massa", "Carga", "Distância", "Volume"],
            "gabarito": 1
        }
    },
    {
        "nome": "Diferença de Potencial (ddp)",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A diferença de potencial elétrico (ddp) entre dois pontos de um circuito é medida, no SI, em...",
            "alternativas": ["Ampère (A)", "Volt (V)", "Ohm (Ω)", "Watt (W)"],
            "gabarito": 1
        }
    },
    {
        "nome": "Superfícies Equipotenciais",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Sobre uma superfície equipotencial, o trabalho realizado para mover uma carga entre dois pontos quaisquer é...",
            "alternativas": ["Máximo", "Nulo", "Igual à energia cinética da carga", "Sempre negativo"],
            "gabarito": 1
        }
    },
    {
        "nome": "Relação entre Campo e Potencial Elétrico",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "As linhas de campo elétrico, em relação às superfícies equipotenciais, são sempre...",
            "alternativas": ["Paralelas a elas", "Perpendiculares a elas", "Coincidentes com elas", "Sem relação alguma"],
            "gabarito": 1
        }
    },
    # ── Eletrodinâmica I (corrente, Lei de Ohm) ─────────────────────
    {
        "nome": "Corrente Elétrica — Definição",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A corrente elétrica é definida como o fluxo ordenado de...",
            "alternativas": ["Prótons através de um isolante", "Cargas elétricas através de um condutor", "Nêutrons através do vácuo", "Fótons através de um circuito"],
            "gabarito": 1
        }
    },
    {
        "nome": "Primeira Lei de Ohm",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A Primeira Lei de Ohm relaciona a tensão (U), a resistência (R) e a corrente (i) elétrica pela equação...",
            "alternativas": ["U = R / i", "U = R . i", "U = i / R", "U = R + i"],
            "gabarito": 1
        }
    },
    {
        "nome": "Resistores Ôhmicos",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Um resistor é considerado ôhmico quando o gráfico da tensão em função da corrente elétrica é...",
            "alternativas": ["Uma reta passando pela origem", "Uma curva exponencial", "Uma parábola", "Uma reta paralela ao eixo da corrente"],
            "gabarito": 0
        }
    },
    {
        "nome": "Potência Elétrica Dissipada",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A potência elétrica dissipada em um resistor pode ser calculada por P = U . i, sendo também equivalente a...",
            "alternativas": ["P = R / i²", "P = R . i²", "P = U / R²", "P = R + i"],
            "gabarito": 1
        }
    },
    {
        "nome": "Efeito Joule",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O efeito Joule consiste na conversão de energia elétrica em energia...",
            "alternativas": ["Térmica, devido à resistência do condutor", "Química, devido a reações internas", "Magnética, devido ao campo induzido", "Nuclear, devido à fissão de átomos"],
            "gabarito": 0
        }
    },
    # ── Associação de Resistores ─────────────────────────────────────
    {
        "nome": "Associação em Série — Resistência Equivalente",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Em uma associação de resistores em série, a resistência equivalente é...",
            "alternativas": ["Menor que a menor das resistências", "A soma das resistências individuais", "O inverso da soma dos inversos", "Sempre igual à maior resistência"],
            "gabarito": 1
        }
    },
    {
        "nome": "Associação em Série — Corrente",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Em uma associação de resistores em série, a corrente elétrica que percorre cada resistor é...",
            "alternativas": ["Diferente em cada um, proporcional à resistência", "A mesma em todos os resistores", "Nula em pelo menos um deles", "Inversamente proporcional à tensão total"],
            "gabarito": 1
        }
    },
    {
        "nome": "Associação em Paralelo — Tensão",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Em uma associação de resistores em paralelo, a tensão elétrica sobre cada resistor é...",
            "alternativas": ["A mesma em todos os resistores", "Diferente, proporcional à resistência", "Sempre nula", "Igual à soma das correntes"],
            "gabarito": 0
        }
    },
    {
        "nome": "Associação em Paralelo — Resistência Equivalente",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Para dois resistores associados em paralelo, o inverso da resistência equivalente é igual a...",
            "alternativas": ["R1 + R2", "1/R1 + 1/R2", "R1 . R2", "R1 - R2"],
            "gabarito": 1
        }
    },
    {
        "nome": "Associação Mista de Resistores",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Para resolver uma associação mista de resistores, o procedimento correto é...",
            "alternativas": [
                "Somar diretamente todas as resistências, ignorando a topologia",
                "Reduzir primeiro os trechos em série ou paralelo isoladamente, depois combinar os resultados",
                "Ignorar os resistores em paralelo",
                "Aplicar apenas a fórmula da série a todo o circuito"
            ],
            "gabarito": 1
        }
    },
    # ── Capacitores ────────────────────────────────────────────────
    {
        "nome": "Capacitor — Função Básica",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A principal função de um capacitor em um circuito elétrico é...",
            "alternativas": ["Dissipar energia em forma de calor", "Armazenar energia em forma de campo elétrico", "Converter corrente contínua em alternada", "Aumentar a resistência do circuito"],
            "gabarito": 1
        }
    },
    {
        "nome": "Capacitância — Definição",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A capacitância de um capacitor é definida pela razão entre a carga armazenada e...",
            "alternativas": ["A corrente elétrica", "A diferença de potencial entre as placas", "A resistência do circuito", "O tempo de carregamento"],
            "gabarito": 1
        }
    },
    {
        "nome": "Capacitores em Paralelo — Capacitância Equivalente",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Em uma associação de capacitores em paralelo, a capacitância equivalente é igual a...",
            "alternativas": ["O inverso da soma dos inversos", "A soma das capacitâncias individuais", "A menor das capacitâncias", "Sempre zero"],
            "gabarito": 1
        }
    },
    {
        "nome": "Capacitores em Série — Carga Armazenada",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Em uma associação de capacitores em série, a carga elétrica armazenada em cada capacitor é...",
            "alternativas": ["A mesma em todos", "Diferente, proporcional à capacitância", "Sempre nula", "Igual à soma das tensões"],
            "gabarito": 0
        }
    },
    {
        "nome": "Energia Armazenada em um Capacitor",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A energia armazenada em um capacitor carregado pode ser calculada pela expressão...",
            "alternativas": ["E = Q . U", "E = Q . U / 2", "E = Q / U", "E = U / Q"],
            "gabarito": 1
        }
    },
    # ── Medidores, Geradores, Receptores e Leis de Kirchhoff ────────
    {
        "nome": "Amperímetro — Ligação no Circuito",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O amperímetro, usado para medir a corrente elétrica, deve ser ligado ao circuito...",
            "alternativas": [
                "Em série, e idealmente possui resistência interna nula",
                "Em paralelo, e idealmente possui resistência interna nula",
                "Em série, e idealmente possui resistência interna infinita",
                "Em paralelo, e idealmente possui resistência interna infinita"
            ],
            "gabarito": 0
        }
    },
    {
        "nome": "Voltímetro — Ligação no Circuito",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O voltímetro, usado para medir a diferença de potencial, deve ser ligado ao circuito...",
            "alternativas": [
                "Em série, e idealmente possui resistência interna infinita",
                "Em paralelo, e idealmente possui resistência interna infinita",
                "Em série, e idealmente possui resistência interna nula",
                "Em paralelo, e idealmente possui resistência interna nula"
            ],
            "gabarito": 1
        }
    },
    {
        "nome": "Gerador Elétrico — Força Eletromotriz",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A equação característica de um gerador real é U = ε - r . i, o que mostra que a tensão nos terminais...",
            "alternativas": ["É sempre igual à força eletromotriz", "Diminui conforme a corrente aumenta", "Aumenta conforme a corrente aumenta", "Independe da resistência interna"],
            "gabarito": 1
        }
    },
    {
        "nome": "Receptor Elétrico — Força Contraeletromotriz",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Um receptor elétrico (como um motor) converte parte da energia elétrica recebida em outras formas de energia úteis, sendo caracterizado por uma força...",
            "alternativas": ["Eletromotriz", "Contraeletromotriz", "Magnética induzida", "Gravitacional"],
            "gabarito": 1
        }
    },
    {
        "nome": "Primeira Lei de Kirchhoff (Lei dos Nós)",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A Primeira Lei de Kirchhoff (Lei dos Nós) afirma que, em qualquer nó de um circuito...",
            "alternativas": ["A soma das correntes que entram é igual à soma das correntes que saem", "A soma das tensões é sempre nula", "A corrente é sempre a mesma em todos os ramos", "A resistência total é a soma das resistências"],
            "gabarito": 0
        }
    },
    {
        "nome": "Segunda Lei de Kirchhoff (Lei das Malhas)",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A Segunda Lei de Kirchhoff (Lei das Malhas) afirma que, ao percorrer uma malha fechada de um circuito, a soma algébrica das diferenças de potencial é...",
            "alternativas": ["Sempre positiva", "Sempre negativa", "Igual a zero", "Igual à corrente total"],
            "gabarito": 2
        }
    },
    {
        "nome": "Rendimento de um Gerador",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "O rendimento de um gerador elétrico é dado pela razão entre a potência útil (fornecida ao circuito externo) e a potência...",
            "alternativas": ["Dissipada apenas na resistência interna", "Total gerada", "Nula", "Reativa"],
            "gabarito": 1
        }
    },
    {
        "nome": "Curto-Circuito em um Gerador",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Quando os terminais de um gerador são ligados diretamente entre si (curto-circuito), a tensão nos terminais é...",
            "alternativas": ["Máxima", "Igual à força eletromotriz", "Nula", "Igual à resistência interna"],
            "gabarito": 2
        }
    },
]


def _obter_ou_criar_estrutura_padrao():
    """Garante que exista um professor + turma + módulo de Física.

    Retorna o Modulo padrão, onde as lições/questões iniciais são criadas.
    É idempotente: se a estrutura já existir (mesmo nome), é reaproveitada.
    """
    professor = Professor.query.filter_by(usuario=USUARIO_PROFESSOR_PADRAO).first()
    if not professor:
        professor = Professor(
            nome_completo=NOME_PROFESSOR_PADRAO,
            genero="Prefiro não dizer",
            email="professor@sparkly.local",
            usuario=USUARIO_PROFESSOR_PADRAO,
            senha=generate_password_hash(SENHA_PROFESSOR_PADRAO),
        )
        db.session.add(professor)
        db.session.flush()

    materia = Materia.query.filter_by(nome_materia=NOME_MATERIA, id_professor=professor.id_professor).first()
    if not materia:
        from app.services.professor_service import _gerar_codigo_turma
        materia = Materia(nome_materia=NOME_MATERIA, numero_sala="101",
                           codigo_turma=_gerar_codigo_turma(), id_professor=professor.id_professor)
        db.session.add(materia)
        db.session.flush()
    elif not materia.codigo_turma:
        from app.services.professor_service import _gerar_codigo_turma
        materia.codigo_turma = _gerar_codigo_turma()

    modulo = Modulo.query.filter_by(nome=NOME_MODULO, id_materia=materia.id_materia).first()
    if not modulo:
        modulo = Modulo(nome=NOME_MODULO, descricao="Trilha inicial de Eletricidade e Magnetismo",
                         ordem=0, id_materia=materia.id_materia)
        db.session.add(modulo)
        db.session.flush()

    return modulo


def seed_questoes():
    """Insere as questões iniciais que ainda não existem, já organizadas em
    lições dentro do módulo "Eletricidade e Magnetismo", no esquema
    Módulo → Lição → Questão (mesma ideia do Duolingo).

    Retorna a quantidade de questões inseridas agora. É idempotente: se já
    existir, apenas garante que a instância (e a lição) correspondente
    também existam.
    """
    modulo = _obter_ou_criar_estrutura_padrao()

    # Monta a lista de lições (criando as que faltarem) na ordem definida.
    licoes = []
    for ordem, (nome_licao, _qtd) in enumerate(LICOES_TOPICOS):
        licao = Licao.query.filter_by(nome=nome_licao, id_modulo=modulo.id_modulo).first()
        if not licao:
            licao = Licao(nome=nome_licao, ordem=ordem, id_modulo=modulo.id_modulo)
            db.session.add(licao)
            db.session.flush()
        licoes.append(licao)

    # Mapa índice-da-questão → lição correspondente, seguindo LICOES_TOPICOS.
    licao_por_indice = {}
    indice = 0
    for licao, (_nome, qtd) in zip(licoes, LICOES_TOPICOS):
        for _ in range(qtd):
            licao_por_indice[indice] = licao
            indice += 1

    inseridas = 0
    for i, q_data in enumerate(QUESTOES_INICIAIS):
        licao_da_questao = licao_por_indice.get(i)

        existente = ModeloQuestao.query.filter_by(nome=q_data["nome"]).first()
        if existente:
            inst = QuestaoInstanciada.query.filter_by(modelo_id=existente.id).first()
            if not inst:
                db.session.add(QuestaoInstanciada(
                    modelo_id=existente.id, valores_variaveis={},
                    id_licao=licao_da_questao.id_licao if licao_da_questao else None
                ))
            elif inst.id_licao is None and licao_da_questao:
                inst.id_licao = licao_da_questao.id_licao
            continue

        modelo = ModeloQuestao(
            nome=q_data["nome"],
            tipo=q_data["tipo"],
            conteudo=q_data["conteudo"]
        )
        db.session.add(modelo)
        db.session.flush()

        db.session.add(QuestaoInstanciada(
            modelo_id=modelo.id,
            valores_variaveis={},
            id_licao=licao_da_questao.id_licao if licao_da_questao else None
        ))
        inseridas += 1

    db.session.commit()
    return inseridas


def seed_usuarios_padrao():
    """Cria alunos e professores padrão de teste, se ainda não existirem.

    Todas as senhas usam o mesmo valor por papel (ALUNO123 / PROFESSOR123),
    apenas para ambiente de teste/demonstração — não use em produção.

    Retorna (alunos_criados, professores_criados).
    """
    alunos_criados = 0
    for dados in ALUNOS_PADRAO:
        if Aluno.query.filter_by(usuario=dados["usuario"]).first():
            continue
        aluno = Aluno(
            nome_completo=dados["nome_completo"],
            genero="Prefiro não dizer",
            email=dados["email"],
            usuario=dados["usuario"],
            senha=generate_password_hash(SENHA_ALUNO_PADRAO),
        )
        db.session.add(aluno)
        alunos_criados += 1

    professores_criados = 0
    for dados in PROFESSORES_PADRAO:
        if Professor.query.filter_by(usuario=dados["usuario"]).first():
            continue
        professor = Professor(
            nome_completo=dados["nome_completo"],
            genero="Prefiro não dizer",
            email=dados["email"],
            usuario=dados["usuario"],
            senha=generate_password_hash(SENHA_PROFESSOR_TESTE),
        )
        db.session.add(professor)
        professores_criados += 1

    db.session.commit()
    return alunos_criados, professores_criados
