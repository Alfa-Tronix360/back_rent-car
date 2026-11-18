from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
import database, models, schemas
from auth import get_current_user

router = APIRouter(prefix="/veiculos", tags=["veiculos"])


@router.get("", response_model=list[schemas.VeiculoOut])
def listar(
    estado: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(database.get_db),
    _user: models.Usuario = Depends(get_current_user),
):
    query = db.query(models.Veiculo)
    if estado:
        query = query.filter(models.Veiculo.estado == estado)
    if q:
        termo = f"%{q}%"
        query = query.filter(
            or_(
                models.Veiculo.matricula.ilike(termo),
                models.Veiculo.marca.ilike(termo),
                models.Veiculo.modelo.ilike(termo),
                models.Veiculo.categoria.ilike(termo),
            )
        )
    return query.order_by(models.Veiculo.marca, models.Veiculo.modelo).all()


@router.get("/{id}", response_model=schemas.VeiculoOut)
def obter(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    return veiculo


@router.post("", response_model=schemas.VeiculoOut, status_code=201)
def criar(payload: schemas.VeiculoCreate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    existe = db.query(models.Veiculo).filter(models.Veiculo.matricula == payload.matricula).first()
    if existe:
        raise HTTPException(status_code=400, detail="Já existe um veículo com esta matrícula.")
    veiculo = models.Veiculo(**payload.model_dump())
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    return veiculo


@router.put("/{id}", response_model=schemas.VeiculoOut)
def atualizar(id: str, payload: schemas.VeiculoUpdate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    duplicado = db.query(models.Veiculo).filter(
        models.Veiculo.matricula == payload.matricula, models.Veiculo.id != id
    ).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Já existe um veículo com esta matrícula.")
    for k, v in payload.model_dump().items():
        setattr(veiculo, k, v)
    db.commit()
    db.refresh(veiculo)
    return veiculo


@router.delete("/{id}")
def eliminar(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    ligados = db.query(models.Aluguer).filter(models.Aluguer.veiculo_id == id).count()
    if ligados:
        raise HTTPException(status_code=400, detail=f"Não é possível eliminar: existem {ligados} aluguer(es) ligados a este veículo.")
    db.delete(veiculo)
    db.commit()
    return {"ok": True, "id": id}
