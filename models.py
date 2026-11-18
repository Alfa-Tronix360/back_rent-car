import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


def agora():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=generate_uuid)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    perfil = Column(String, nullable=False, default="funcionario")  # admin | funcionario
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=agora)


class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(String, primary_key=True, default=generate_uuid)
    matricula = Column(String, unique=True, index=True, nullable=False)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    ano = Column(Integer, nullable=True)
    categoria = Column(String, nullable=True)  # Económico, Sedan, SUV, Pickup, Van
    combustivel = Column(String, nullable=True)  # Gasolina, Diesel, Elétrico, Híbrido
    transmissao = Column(String, nullable=True)  # Manual, Automática
    lugares = Column(Integer, default=5)
    preco_dia = Column(Float, nullable=False, default=0)
    estado = Column(String, default="Disponível")  # Disponível, Alugado, Manutenção
    imagem_url = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=agora)

    alugueres = relationship("Aluguer", back_populates="veiculo")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(String, primary_key=True, default=generate_uuid)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=True)  # BI / NIF
    email = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    carta_conducao = Column(String, nullable=True)
    validade_carta = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=agora)

    alugueres = relationship("Aluguer", back_populates="cliente")


class Aluguer(Base):
    __tablename__ = "alugueres"

    id = Column(String, primary_key=True, default=generate_uuid)
    numero = Column(String, nullable=True)
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    veiculo_id = Column(String, ForeignKey("veiculos.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    valor_diaria = Column(Float, default=0)
    dias = Column(Integer, default=1)
    total = Column(Float, default=0)
    estado = Column(String, default="Reservado")  # Reservado, Ativo, Concluído, Cancelado
    observacoes = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=agora)

    cliente = relationship("Cliente", back_populates="alugueres")
    veiculo = relationship("Veiculo", back_populates="alugueres")
    pagamentos = relationship("Pagamento", back_populates="aluguer", cascade="all, delete-orphan")


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(String, primary_key=True, default=generate_uuid)
    aluguer_id = Column(String, ForeignKey("alugueres.id"), nullable=False)
    valor = Column(Float, nullable=False, default=0)
    metodo = Column(String, nullable=True)  # Numerário, Transferência, Multicaixa, Cartão
    estado = Column(String, default="Pago")  # Pago, Pendente
    data = Column(DateTime, default=agora)
    data_criacao = Column(DateTime, default=agora)

    aluguer = relationship("Aluguer", back_populates="pagamentos")
