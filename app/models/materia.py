from app.models import db


class Materia(db.Model):
    __tablename__ = 'materia'

    id_materia = db.Column(db.Integer, primary_key=True)
    nome_materia = db.Column(db.String(100), nullable=False)
    numero_sala = db.Column(db.String(20))
    codigo_turma = db.Column(db.String(10), unique=True, index=True)
    id_professor = db.Column(db.Integer, db.ForeignKey('professor.id_professor'))

    modulos = db.relationship(
        'Modulo', backref='materia', lazy=True,
        order_by='Modulo.ordem', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Materia {self.nome_materia}>'

    def to_dict(self):
        return {
            'id': self.id_materia,
            'nome': self.nome_materia,
            'numero_sala': self.numero_sala,
            'codigo_turma': self.codigo_turma,
            'id_professor': self.id_professor
        }

    def to_dict_publico(self):
        """Versão enxuta exibida ao aluno ao ingressar via código (sem dados sensíveis)."""
        return {
            'id': self.id_materia,
            'nome': self.nome_materia,
            'numero_sala': self.numero_sala,
            'professor': self.professor.nome_completo if self.professor else None,
            'total_modulos': len(self.modulos),
            'total_licoes': sum(len(m.licoes) for m in self.modulos),
        }
