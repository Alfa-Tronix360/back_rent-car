from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas
from auth import get_current_user

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


@router.get("", response_model=list[schemas.PagamentoOut])
def listar(
    aluguer_id: Optional[str] = None,
    db: Session = Depends(database.get_db),
    _user: models.Usuario = Depends(get_current_user),
):
    query = db.query(models.Pagamento)
    if aluguer_id:
        query = query.filter(models.Pagamento.aluguer_id == aluguer_id)
    return query.order_by(models.Pagamento.data.desc()).all()


@router.post("", response_model=schemas.PagamentoOut, status_code=201)
def criar(payload: schemas.PagamentoCreate, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    aluguer = db.query(models.Aluguer).filter(models.Aluguer.id == payload.aluguer_id).first()
    if not aluguer:
        raise HTTPException(status_code=400, detail="Aluguer não encontrado.")

    dados = payload.model_dump()
    if dados.get("data"):
        try:
            dados["data"] = datetime.fromisoformat(dados["data"])
        except Exception:
            dados.pop("data", None)
    else:
        dados.pop("data", None)

    pagamento = models.Pagamento(**dados)
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


@router.delete("/{id}")
def eliminar(id: str, db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    pagamento = db.query(models.Pagamento).filter(models.Pagamento.id == id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado.")
    db.delete(pagamento)
    db.commit()
    return {"ok": True, "id": id}
