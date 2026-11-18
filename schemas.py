from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ---------- Veículos ----------

class VeiculoBase(BaseModel):
    matricula: str
    marca: str
    modelo: str
    ano: Optional[int] = None
    categoria: Optional[str] = None
    combustivel: Optional[str] = None
    transmissao: Optional[str] = None
    lugares: Optional[int] = 5
    preco_dia: float = 0
    estado: Optional[str] = "Disponível"
    imagem_url: Optional[str] = None


class VeiculoCreate(VeiculoBase):
    pass


class VeiculoUpdate(VeiculoBase):
    pass


class VeiculoOut(VeiculoBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    data_criacao: datetime


# ---------- Clientes ----------

class ClienteBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    carta_conducao: Optional[str] = None
    validade_carta: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    data_criacao: datetime


# ---------- Alugueres ----------

class AluguerBase(BaseModel):
    cliente_id: str
    veiculo_id: str
    data_inicio: str
    data_fim: str
    valor_diaria: Optional[float] = None
    estado: Optional[str] = "Reservado"
    observacoes: Optional[str] = None


class AluguerCreate(AluguerBase):
    pass


class AluguerUpdate(BaseModel):
    cliente_id: Optional[str] = None
    veiculo_id: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    valor_diaria: Optional[float] = None
    estado: Optional[str] = None
    observacoes: Optional[str] = None


class VeiculoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    matricula: str
    marca: str
    modelo: str


class ClienteResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    telefone: Optional[str] = None


class AluguerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    numero: Optional[str] = None
    cliente_id: str
    veiculo_id: str
    data_inicio: datetime
    data_fim: datetime
    valor_diaria: float
    dias: int
    total: float
    estado: str
    observacoes: Optional[str] = None
    data_criacao: datetime
    cliente: Optional[ClienteResumo] = None
    veiculo: Optional[VeiculoResumo] = None


# ---------- Pagamentos ----------

class PagamentoBase(BaseModel):
    aluguer_id: str
    valor: float
    metodo: Optional[str] = None
    estado: Optional[str] = "Pago"
    data: Optional[str] = None


class PagamentoCreate(PagamentoBase):
    pass


class PagamentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    aluguer_id: str
    valor: float
    metodo: Optional[str] = None
    estado: str
    data: datetime
    data_criacao: datetime
