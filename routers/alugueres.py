from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
import database, models, schemas
from auth import get_current_user

router = APIRouter(prefix="/alugueres", tags=["alugueres"])

ESTADOS_ATIVOS = ("Reservado", "Ativo")


def _parse_data(valor: str) -> datetime:
    try:
        return datetime.fromisoformat(valor)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Data inválida: {valor}")


def _calcular_dias(inicio: datetime, fim: datetime) -> int:
    if fim <= inicio:
        raise HTTPException(status_code=400, detail="A data de fim deve ser posterior à data de início.")
    return max(1, (fim.date() - inicio.date()).days)


def _proximo_numero(db: Session) -> str:
    total = db.query(models.Aluguer).count()
    return f"ALG-{total + 1:04d}"


def _verificar_disponibilidade(db: Session, veiculo_id: str, inicio: datetime, fim: datetime, ignorar_id: Optional[str] = None):
    query = db.query(models.Aluguer).filter(
        models.Aluguer.veiculo_id == veiculo_id,
        models.Aluguer.estado.in_(ESTADOS_ATIVOS),
        models.Aluguer.data_inicio < fim,
        models.Aluguer.data_fim > inicio,
    )
    if ignorar_id:
        query = query.filter(models.Aluguer.id != ignorar_id)
    conflito = query.first()
    if conflito:
        raise HTTPException(
            status_code=400,
            detail=f"O veículo já está reservado/alugado no período indicado ({conflito.numero}).",
        )


@router.get("", response_model=list[schemas.AluguerOut])
def listar(
    estado: Optional[str] = None,
    cliente_id: Optional[str] = None,
    veiculo_id: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(database.get_db),
    _user: models.Usuario = Depends(get_current_user),
):
    query = db.query(models.Aluguer)
    if estado:
        query = query.filter(models.Aluguer.estado == estado)
    if cliente_id:
        query = query.filter(models.Aluguer.cliente_id == cliente_id)
    if veiculo_id:
        query = query.filter(models.Aluguer.veiculo_id == veiculo_id)
    alugueres = query.order_by(models.Aluguer.data_criacao.desc()).all()
    if q:
        termo = q.lower()
        alugueres = [
            a for a in alugueres
            if termo in (a.numero or "").lower()
            or termo in (a.cliente.nome if a.cliente else "").lower()
            or termo in (a.veiculo.matricula if a.veiculo else "").lower()
            or termo in (a.veiculo.marca if a.veiculo else "").lower()
            or termo in (a.veiculo.modelo if a.veiculo else "").lower()
        ]
    return alugueres


@router.get("/{id}", response_model=schemas.AluguerOut)
def obter(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    aluguer = db.query(models.Aluguer).filter(models.Aluguer.id == id).first()
    if not aluguer:
        raise HTTPException(status_code=404, detail="Aluguer não encontrado.")
    return aluguer


@router.post("", response_model=schemas.AluguerOut, status_code=201)
def criar(payload: schemas.AluguerCreate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == payload.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente não encontrado.")
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == payload.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=400, detail="Veículo não encontrado.")

    inicio = _parse_data(payload.data_inicio)
    fim = _parse_data(payload.data_fim)
    dias = _calcular_dias(inicio, fim)
    _verificar_disponibilidade(db, veiculo.id, inicio, fim)

    valor_diaria = payload.valor_diaria if payload.valor_diaria is not None else veiculo.preco_dia
    estado = payload.estado or "Reservado"

    aluguer = models.Aluguer(
        numero=_proximo_numero(db),
        cliente_id=cliente.id,
        veiculo_id=veiculo.id,
        data_inicio=inicio,
        data_fim=fim,
        valor_diaria=valor_diaria,
        dias=dias,
        total=dias * valor_diaria,
        estado=estado,
        observacoes=payload.observacoes,
    )
    db.add(aluguer)
    if estado == "Ativo":
        veiculo.estado = "Alugado"
    db.commit()
    db.refresh(aluguer)
    return aluguer


@router.put("/{id}", response_model=schemas.AluguerOut)
def atualizar(id: str, payload: schemas.AluguerUpdate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    aluguer = db.query(models.Aluguer).filter(models.Aluguer.id == id).first()
    if not aluguer:
        raise HTTPException(status_code=404, detail="Aluguer não encontrado.")

    dados = payload.model_dump(exclude_unset=True)

    if "cliente_id" in dados and not db.query(models.Cliente).filter(models.Cliente.id == dados["cliente_id"]).first():
        raise HTTPException(status_code=400, detail="Cliente não encontrado.")
    if "veiculo_id" in dados and not db.query(models.Veiculo).filter(models.Veiculo.id == dados["veiculo_id"]).first():
        raise HTTPException(status_code=400, detail="Veículo não encontrado.")

    inicio = _parse_data(dados["data_inicio"]) if dados.get("data_inicio") else aluguer.data_inicio
    fim = _parse_data(dados["data_fim"]) if dados.get("data_fim") else aluguer.data_fim
    dias = _calcular_dias(inicio, fim)

    veiculo_id = dados.get("veiculo_id", aluguer.veiculo_id)
    estado = dados.get("estado", aluguer.estado)
    if estado in ESTADOS_ATIVOS:
        _verificar_disponibilidade(db, veiculo_id, inicio, fim, ignorar_id=aluguer.id)

    aluguer.cliente_id = dados.get("cliente_id", aluguer.cliente_id)
    aluguer.veiculo_id = veiculo_id
    aluguer.data_inicio = inicio
    aluguer.data_fim = fim
    aluguer.dias = dias
    aluguer.valor_diaria = dados.get("valor_diaria", aluguer.valor_diaria)
    aluguer.total = dias * aluguer.valor_diaria
    aluguer.estado = estado
    if "observacoes" in dados:
        aluguer.observacoes = dados["observacoes"]

    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if veiculo:
        if estado == "Ativo":
            veiculo.estado = "Alugado"
        elif estado in ("Concluído", "Cancelado") and veiculo.estado == "Alugado":
            veiculo.estado = "Disponível"

    db.commit()
    db.refresh(aluguer)
    return aluguer


@router.delete("/{id}")
def eliminar(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    aluguer = db.query(models.Aluguer).filter(models.Aluguer.id == id).first()
    if not aluguer:
        raise HTTPException(status_code=404, detail="Aluguer não encontrado.")
    veiculo = aluguer.veiculo
    db.delete(aluguer)
    if veiculo and veiculo.estado == "Alugado":
        veiculo.estado = "Disponível"
    db.commit()
    return {"ok": True, "id": id}
