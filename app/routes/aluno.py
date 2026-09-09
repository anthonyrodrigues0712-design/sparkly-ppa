from flask import Blueprint, request, jsonify, session
from app.services import auth_service, aluno_service, questao_service, gamificacao_service, pet_service, modulo_service

aluno_bp = Blueprint('aluno', __name__)

GENEROS_VALIDOS = {
    'masculino': 'Masculino',
    'feminino': 'Feminino',
    'nao-binario': 'Não-binário',
    'prefiro-nao-dizer': 'Prefiro não dizer',
}


@aluno_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not dados.get('usuario') or not dados.get('senha'):
        return jsonify({'sucesso': False, 'erro': 'Usuário e senha são obrigatórios'}), 400

    aluno = auth_service.validar_login(dados['usuario'].strip(), dados['senha'].strip())
    if not aluno:
        return jsonify({'sucesso': False, 'erro': 'Usuário ou senha inválidos'}), 401

    session['aluno_id'] = aluno.id_aluno
    session['aluno'] = aluno.to_dict()

    return jsonify({
        'sucesso': True,
        'aluno_id': aluno.id_aluno,
        'dados': aluno_service.obter_dados_aluno(aluno.id_aluno)
    }), 200


@aluno_bp.route('/aluno', methods=['GET'])
def obter_aluno():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = aluno_service.obter_dados_aluno(aluno_id)
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Aluno não encontrado'}), 404

    return jsonify({'sucesso': True, 'dados': dados}), 200


@aluno_bp.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    if not dados or not all([dados.get('usuario'), dados.get('senha'), dados.get('email'), dados.get('nome')]):
        return jsonify({'sucesso': False, 'erro': 'Todos os campos são obrigatórios'}), 400

    genero_opcao = (dados.get('genero') or '').strip()
    if not genero_opcao:
        return jsonify({'sucesso': False, 'erro': 'Selecione um gênero'}), 400

    if genero_opcao == 'personalizado':
        genero = (dados.get('generoPersonalizado') or '').strip()
        if not genero:
            return jsonify({'sucesso': False, 'erro': 'Informe o gênero personalizado'}), 400
    elif genero_opcao in GENEROS_VALIDOS:
        genero = GENEROS_VALIDOS[genero_opcao]
    else:
        return jsonify({'sucesso': False, 'erro': 'Gênero inválido'}), 400

    nome_social = None
    if dados.get('usaNomeSocial'):
        nome_social = (dados.get('nomeSocial') or '').strip()
        if not nome_social:
            return jsonify({'sucesso': False, 'erro': 'Informe o nome social'}), 400

    aluno, erro, codigo = aluno_service.cadastrar_aluno(
        nome=dados['nome'].strip(),
        email=dados['email'].strip(),
        usuario=dados['usuario'].strip(),
        senha=dados['senha'].strip(),
        genero=genero,
        nome_social=nome_social,
    )
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({
        'sucesso': True,
        'mensagem': 'Cadastro realizado com sucesso!',
        'aluno': aluno.to_dict()
    }), codigo


@aluno_bp.route('/aluno/turmas/buscar', methods=['GET'])
def buscar_turma():
    if not session.get('aluno_id'):
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    codigo = request.args.get('codigo', '')
    turma, erro, http_codigo = aluno_service.buscar_turma_por_codigo(codigo)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), http_codigo

    return jsonify({'sucesso': True, 'turma': turma}), http_codigo


@aluno_bp.route('/aluno/questoes', methods=['GET'])
def questoes():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({
        'sucesso': True,
        'questoes': questao_service.listar_questoes_do_aluno(aluno_id)
    }), 200


@aluno_bp.route('/aluno/modulos', methods=['GET'])
def modulos():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({
        'sucesso': True,
        'modulos': modulo_service.listar_modulos_do_aluno(aluno_id)
    }), 200


@aluno_bp.route('/aluno/licoes/<int:licao_id>/questoes', methods=['GET'])
def questoes_da_licao(licao_id):
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados, erro, codigo = modulo_service.listar_questoes_da_licao(aluno_id, licao_id)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, **dados}), codigo


@aluno_bp.route('/aluno/questoes/<int:questao_id>/responder', methods=['POST'])
def responder(questao_id):
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    resposta = dados.get('resposta') if dados else None
    if resposta is None:
        return jsonify({'sucesso': False, 'erro': 'Resposta é obrigatória'}), 400

    resultado, erro, codigo = questao_service.registrar_resposta(aluno_id, questao_id, resposta)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, **resultado}), codigo


@aluno_bp.route('/aluno/missoes', methods=['GET'])
def missoes():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({
        'sucesso': True,
        'missoes': gamificacao_service.listar_missoes(aluno_id)
    }), 200


@aluno_bp.route('/aluno/ranking', methods=['GET'])
def ranking():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({
        'sucesso': True,
        'ranking': gamificacao_service.listar_ranking()
    }), 200


@aluno_bp.route('/aluno/loja/recarregar', methods=['POST'])
def recarregar_coracoes():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    aluno, erro, codigo = gamificacao_service.recarregar_coracoes(aluno_id)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'aluno': aluno.to_dict()}), codigo


@aluno_bp.route('/aluno/pet', methods=['GET'])
def obter_pet():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({'sucesso': True, **pet_service.obter_dados_pet(aluno_id)}), 200


@aluno_bp.route('/aluno/pet/nome', methods=['POST'])
def renomear_pet():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    nome = dados.get('nome') if dados else None

    pet, erro, codigo = pet_service.renomear_pet(aluno_id, nome)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'pet': pet.to_dict()}), codigo


@aluno_bp.route('/aluno/pet/cor/comprar', methods=['POST'])
def comprar_cor_pet():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    cor = dados.get('cor') if dados else None

    pet, erro, codigo = pet_service.comprar_cor(aluno_id, cor)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    aluno = aluno_service.obter_dados_aluno(aluno_id)['aluno']
    return jsonify({'sucesso': True, 'pet': pet.to_dict(), 'aluno': aluno}), codigo


@aluno_bp.route('/aluno/pet/cor/equipar', methods=['POST'])
def equipar_cor_pet():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    cor = dados.get('cor') if dados else None

    pet, erro, codigo = pet_service.equipar_cor(aluno_id, cor)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'pet': pet.to_dict()}), codigo
