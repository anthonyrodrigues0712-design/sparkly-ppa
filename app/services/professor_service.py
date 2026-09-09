import random
import string

from app.models import db, Aluno, Materia, Modulo, Licao, ModeloQuestao, QuestaoInstanciada, Desempenho

# Caracteres usados no código da turma: letras maiúsculas e números,
# excluindo os que costumam ser confundidos entre si (0/O, 1/I).
_ALFABETO_CODIGO = ''.join(c for c in (string.ascii_uppercase + string.digits) if c not in 'O0I1')
_TAMANHO_CODIGO = 6


def _gerar_codigo_turma():
    """Gera um código alfanumérico único (estilo Google Classroom) para a turma."""
    while True:
        codigo = ''.join(random.choices(_ALFABETO_CODIGO, k=_TAMANHO_CODIGO))
        if not Materia.query.filter_by(codigo_turma=codigo).first():
            return codigo


def _instancia_ids_da_materia(materia):
    """IDs de todas as questões instanciadas que pertencem a alguma lição da turma."""
    ids = []
    for modulo in materia.modulos:
        for licao in modulo.licoes:
            ids.extend(q.id for q in licao.questoes)
    return ids


def _total_licoes(materia):
    return sum(len(m.licoes) for m in materia.modulos)


def listar_turmas(professor_id):
    """Lista as turmas (matérias) do professor com totais de lições e alunos."""
    turmas = []
    for m in Materia.query.filter_by(id_professor=professor_id).all():
        instancia_ids = _instancia_ids_da_materia(m)
        total_alunos = 0
        if instancia_ids:
            total_alunos = db.session.query(Desempenho.id_aluno)\
                .filter(Desempenho.id_atividade.in_(instancia_ids))\
                .distinct().count()

        turmas.append({
            'id': m.id_materia,
            'nome': m.nome_materia,
            'numero_sala': m.numero_sala,
            'codigo_turma': m.codigo_turma,
            'total_modulos': len(m.modulos),
            'total_licoes': _total_licoes(m),
            'total_alunos': total_alunos
        })
    return turmas


def criar_turma(professor_id, nome, numero_sala=None):
    """Cria uma turma (matéria) vinculada ao professor logado. Retorna (materia, erro, codigo)."""
    if not nome or not nome.strip():
        return None, 'Informe o nome da turma', 400

    try:
        materia = Materia(nome_materia=nome.strip(),
                           numero_sala=(numero_sala or '').strip() or None,
                           codigo_turma=_gerar_codigo_turma(),
                           id_professor=professor_id)
        db.session.add(materia)
        db.session.commit()
        return materia, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def obter_turma(materia_id, professor_id):
    """Detalhe da turma (módulos + lições + alunos com média). Retorna dict ou None."""
    materia = Materia.query.filter_by(id_materia=materia_id, id_professor=professor_id).first()
    if not materia:
        return None

    modulos = []
    for modulo in sorted(materia.modulos, key=lambda mo: (mo.ordem, mo.id_modulo)):
        licoes = [dict(l.to_dict(), total_questoes=len(l.questoes))
                  for l in sorted(modulo.licoes, key=lambda li: (li.ordem, li.id_licao))]
        modulos.append(dict(modulo.to_dict(), licoes=licoes))

    instancia_ids = _instancia_ids_da_materia(materia)
    alunos_data = []

    if instancia_ids:
        desempenhos = Desempenho.query.filter(Desempenho.id_atividade.in_(instancia_ids)).all()
        for aid in sorted({d.id_aluno for d in desempenhos}):
            aluno = db.session.get(Aluno, aid)
            if not aluno:
                continue
            notas = [float(d.nota) for d in desempenhos if d.id_aluno == aid and d.nota]
            alunos_data.append({
                'id': aluno.id_aluno,
                'nome': aluno.nome_completo,
                'usuario': aluno.usuario,
                'media': round(sum(notas) / len(notas), 2) if notas else 0,
                'atividades': len([d for d in desempenhos if d.id_aluno == aid])
            })

    return {
        'turma': materia.to_dict(),
        'modulos': modulos,
        'alunos': alunos_data
    }


# ── Módulos ──────────────────────────────────────────────────────────

def criar_modulo(materia_id, professor_id, nome, descricao=None):
    """Cria um módulo dentro de uma turma do professor. Retorna (modulo, erro, codigo)."""
    materia = Materia.query.filter_by(id_materia=materia_id, id_professor=professor_id).first()
    if not materia:
        return None, 'Turma não encontrada', 404

    if not nome or not nome.strip():
        return None, 'Informe o nome do módulo', 400

    try:
        ordem = len(materia.modulos)
        modulo = Modulo(nome=nome.strip(), descricao=(descricao or '').strip() or None,
                         ordem=ordem, id_materia=materia_id)
        db.session.add(modulo)
        db.session.commit()
        return modulo, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def editar_modulo(modulo_id, professor_id, dados):
    """Edita um módulo (validando que pertence ao professor). Retorna (modulo, erro, codigo)."""
    modulo = db.session.get(Modulo, modulo_id)
    if not modulo or modulo.materia.id_professor != professor_id:
        return None, 'Módulo não encontrado', 404

    try:
        if dados.get('nome'):
            modulo.nome = dados['nome'].strip()
        if 'descricao' in dados:
            modulo.descricao = (dados.get('descricao') or '').strip() or None
        if dados.get('ordem') is not None:
            modulo.ordem = int(dados['ordem'])
        db.session.commit()
        return modulo, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def deletar_modulo(modulo_id, professor_id):
    """Exclui um módulo (e suas lições). Retorna (resultado, erro, codigo)."""
    modulo = db.session.get(Modulo, modulo_id)
    if not modulo or modulo.materia.id_professor != professor_id:
        return None, 'Módulo não encontrado', 404

    try:
        db.session.delete(modulo)
        db.session.commit()
        return True, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


# ── Lições ───────────────────────────────────────────────────────────

def criar_licao(modulo_id, professor_id, nome, descricao=None):
    """Cria uma lição dentro de um módulo do professor. Retorna (licao, erro, codigo)."""
    modulo = db.session.get(Modulo, modulo_id)
    if not modulo or modulo.materia.id_professor != professor_id:
        return None, 'Módulo não encontrado', 404

    if not nome or not nome.strip():
        return None, 'Informe o nome da lição', 400

    try:
        ordem = len(modulo.licoes)
        licao = Licao(nome=nome.strip(), descricao=(descricao or '').strip() or None,
                       ordem=ordem, id_modulo=modulo_id)
        db.session.add(licao)
        db.session.commit()
        return licao, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def editar_licao(licao_id, professor_id, dados):
    """Edita uma lição (validando que pertence ao professor). Retorna (licao, erro, codigo)."""
    licao = db.session.get(Licao, licao_id)
    if not licao or licao.modulo.materia.id_professor != professor_id:
        return None, 'Lição não encontrada', 404

    try:
        if dados.get('nome'):
            licao.nome = dados['nome'].strip()
        if 'descricao' in dados:
            licao.descricao = (dados.get('descricao') or '').strip() or None
        if dados.get('ordem') is not None:
            licao.ordem = int(dados['ordem'])
        db.session.commit()
        return licao, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def deletar_licao(licao_id, professor_id):
    """Exclui uma lição. As questões ligadas a ela ficam sem lição (não são apagadas)."""
    licao = db.session.get(Licao, licao_id)
    if not licao or licao.modulo.materia.id_professor != professor_id:
        return None, 'Lição não encontrada', 404

    try:
        db.session.delete(licao)
        db.session.commit()
        return True, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def listar_licoes_do_professor(professor_id):
    """Lista todas as lições das turmas do professor, com o nome do módulo/turma
    (útil para popular o seletor de lição na hora de criar/editar uma questão)."""
    licoes = []
    for materia in Materia.query.filter_by(id_professor=professor_id).all():
        for modulo in sorted(materia.modulos, key=lambda mo: (mo.ordem, mo.id_modulo)):
            for licao in sorted(modulo.licoes, key=lambda li: (li.ordem, li.id_licao)):
                licoes.append({
                    'id': licao.id_licao,
                    'nome': licao.nome,
                    'modulo': modulo.nome,
                    'turma': materia.nome_materia,
                })
    return licoes


# ── Questões ─────────────────────────────────────────────────────────

def listar_questoes():
    return [q.to_dict() for q in ModeloQuestao.query.all()]


def criar_questao(nome, tipo, conteudo, id_licao=None):
    """Cria a questão-modelo e uma instância, opcionalmente já ligada a uma lição.

    Retorna (questao, erro, codigo).
    """
    if id_licao is not None and not db.session.get(Licao, id_licao):
        return None, 'Lição não encontrada', 404

    try:
        questao = ModeloQuestao(nome=nome.strip(), tipo=tipo.strip(), conteudo=conteudo)
        db.session.add(questao)
        db.session.flush()
        db.session.add(QuestaoInstanciada(modelo_id=questao.id, valores_variaveis={}, id_licao=id_licao))
        db.session.commit()
        return questao, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def editar_questao(questao_id, dados):
    """Edita uma questão-modelo e, opcionalmente, a lição de sua(s) instância(s).

    Retorna (questao, erro, codigo).
    """
    questao = db.session.get(ModeloQuestao, questao_id)
    if not questao:
        return None, 'Questão não encontrada', 404

    try:
        if dados.get('nome'):
            questao.nome = dados['nome'].strip()
        if dados.get('tipo'):
            questao.tipo = dados['tipo'].strip()
        if dados.get('conteudo') is not None:
            questao.conteudo = dados['conteudo']
        if 'id_licao' in dados:
            id_licao = dados.get('id_licao')
            if id_licao is not None and not db.session.get(Licao, id_licao):
                return None, 'Lição não encontrada', 404
            for inst in questao.questoes_instanciadas:
                inst.id_licao = id_licao
        db.session.commit()
        return questao, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def deletar_questao(questao_id):
    """Exclui uma questão-modelo. Retorna (resultado, erro, codigo)."""
    questao = db.session.get(ModeloQuestao, questao_id)
    if not questao:
        return None, 'Questão não encontrada', 404

    try:
        db.session.delete(questao)
        db.session.commit()
        return True, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def sincronizar_instancias():
    """Cria instâncias para modelos sem nenhuma. Retorna (criadas, erro, codigo)."""
    criadas = 0
    try:
        for modelo in ModeloQuestao.query.all():
            existe = QuestaoInstanciada.query.filter_by(modelo_id=modelo.id).first()
            if not existe:
                db.session.add(QuestaoInstanciada(modelo_id=modelo.id, valores_variaveis={}))
                criadas += 1
        db.session.commit()
        return criadas, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500
