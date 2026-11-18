from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
import database, models, schemas
from auth import get_current_user

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[schemas.ClienteOut])
def listar(
    q: Optional[str] = None,
    db: Session = Depends(database.get_db),
    _user: models.Usuario = Depends(get_current_user),
):
    query = db.query(models.Cliente)
    if q:
        termo = f"%{q}%"
        query = query.filter(
            or_(
                models.Cliente.nome.ilike(termo),
                models.Cliente.documento.ilike(termo),
                models.Cliente.email.ilike(termo),
                models.Cliente.telefone.ilike(termo),
            )
        )
    return query.order_by(models.Cliente.nome).all()


@router.get("/{id}", response_model=schemas.ClienteOut)
def obter(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente


@router.post("", response_model=schemas.ClienteOut, status_code=201)
def criar(payload: schemas.ClienteCreate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    cliente = models.Cliente(**payload.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{id}", response_model=schemas.ClienteOut)
def atualizar(id: str, payload: schemas.ClienteUpdate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    for k, v in payload.model_dump().items():
        setattr(cliente, k, v)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{id}")
def eliminar(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    ligados = db.query(models.Aluguer).filter(models.Aluguer.cliente_id == id).count()
    if ligados:
        raise HTTPException(status_code=400, detail=f"Não é possível eliminar: existem {ligados} aluguer(es) ligados a este cliente.")
    db.delete(cliente)
    db.commit()
    return {"ok": True, "id": id}
