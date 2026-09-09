from werkzeug.security import generate_password_hash
from app.models import db, Aluno, Desempenho, Licao, Materia


def obter_dados_aluno(aluno_id):
    """Obtém dados completos do aluno incluindo desempenho e lições."""
    aluno = db.session.get(Aluno, aluno_id)
    if not aluno:
        return None

    desempenhos = Desempenho.query.filter_by(id_aluno=aluno_id).all()
    licoes = Licao.query.all()

    notas = [float(d.nota) for d in desempenhos if d.nota]
    media_notas = sum(notas) / len(notas) if notas else 0

    return {
        'aluno': aluno.to_dict(),
        'desempenho': {
            'atividades_completas': len([d for d in desempenhos if d.status == 'concluido']),
            'media_notas': round(media_notas, 2),
            'total_atividades': len(desempenhos)
        },
        'licoes': [
            {'id': l.id_licao, 'nome': l.nome, 'descricao': l.descricao}
            for l in licoes
        ]
    }


def buscar_turma_por_codigo(codigo):
    """Busca uma turma pelo código de ingresso (estilo Google Classroom).

    Retorna (turma_dict, erro, codigo_http).
    """
    if not codigo or not codigo.strip():
        return None, 'Informe o código da turma', 400

    materia = Materia.query.filter_by(codigo_turma=codigo.strip().upper()).first()
    if not materia:
        return None, 'Nenhuma turma encontrada com esse código', 404

    return materia.to_dict_publico(), None, 200


def cadastrar_aluno(nome, email, usuario, senha, genero='Prefiro não dizer', nome_social=None):
    """Cria um aluno. Retorna (aluno, erro, codigo)."""
    if Aluno.query.filter_by(usuario=usuario).first():
        return None, 'Usuário já existe', 409

    if Aluno.query.filter_by(email=email).first():
        return None, 'Email já cadastrado', 409

    try:
        aluno = Aluno(
            nome_completo=nome,
            email=email,
            usuario=usuario,
            senha=generate_password_hash(senha),
            genero=genero,
            nome_social=nome_social,
        )
        db.session.add(aluno)
        db.session.commit()
        return aluno, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500
