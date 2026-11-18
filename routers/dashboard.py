from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database, models
from auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _iso(dt) -> str | None:
    return dt.isoformat() if dt else None


@router.get("/stats")
def stats(db: Session = Depends(database.get_db), _user: models.Usuario = Depends(get_current_user)):
    veiculos = db.query(models.Veiculo).all()
    alugueres = db.query(models.Aluguer).all()
    pagamentos = db.query(models.Pagamento).all()
    total_clientes = db.query(models.Cliente).count()

    agora = datetime.now()

    receita_total = sum(p.valor for p in pagamentos if p.estado == "Pago")
    receita_mes = sum(
        p.valor for p in pagamentos
        if p.estado == "Pago" and p.data and p.data.year == agora.year and p.data.month == agora.month
    )
    por_cobrar = sum(
        max(0.0, a.total - sum(p.valor for p in a.pagamentos if p.estado == "Pago"))
        for a in alugueres
        if a.estado in ("Reservado", "Ativo")
    )

    # Receita dos últimos 6 meses
    meses = []
    ano, mes = agora.year, agora.month
    for _ in range(6):
        meses.append((ano, mes))
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1
    meses.reverse()
    receita_por_mes = []
    for (a, m) in meses:
        valor = sum(
            p.valor for p in pagamentos
            if p.estado == "Pago" and p.data and p.data.year == a and p.data.month == m
        )
        receita_por_mes.append({"mes": f"{MESES_PT[m - 1]}/{str(a)[2:]}", "valor": valor})

    ultimos = sorted(alugueres, key=lambda a: a.data_criacao, reverse=True)[:6]
    ultimos_alugueres = [{
        "id": a.id,
        "numero": a.numero,
        "cliente": a.cliente.nome if a.cliente else "—",
        "veiculo": f"{a.veiculo.marca} {a.veiculo.modelo}" if a.veiculo else "—",
        "matricula": a.veiculo.matricula if a.veiculo else "—",
        "estado": a.estado,
        "total": a.total,
        "data_inicio": _iso(a.data_inicio),
        "data_fim": _iso(a.data_fim),
    } for a in ultimos]

    proximas = sorted(
        [a for a in alugueres if a.estado == "Ativo" and a.data_fim >= agora],
        key=lambda a: a.data_fim,
    )[:5]
    proximas_devolucoes = [{
        "id": a.id,
        "numero": a.numero,
        "cliente": a.cliente.nome if a.cliente else "—",
        "veiculo": f"{a.veiculo.marca} {a.veiculo.modelo}" if a.veiculo else "—",
        "matricula": a.veiculo.matricula if a.veiculo else "—",
        "data_fim": _iso(a.data_fim),
    } for a in proximas]

    return {
        "veiculos": {
            "total": len(veiculos),
            "disponiveis": sum(1 for v in veiculos if v.estado == "Disponível"),
            "alugados": sum(1 for v in veiculos if v.estado == "Alugado"),
            "manutencao": sum(1 for v in veiculos if v.estado == "Manutenção"),
        },
        "clientes": total_clientes,
        "alugueres": {
            "total": len(alugueres),
            "ativos": sum(1 for a in alugueres if a.estado == "Ativo"),
            "reservados": sum(1 for a in alugueres if a.estado == "Reservado"),
            "concluidos": sum(1 for a in alugueres if a.estado == "Concluído"),
        },
        "financeiro": {
            "receita_total": receita_total,
            "receita_mes": receita_mes,
            "por_cobrar": por_cobrar,
        },
        "receita_por_mes": receita_por_mes,
        "ultimos_alugueres": ultimos_alugueres,
        "proximas_devolucoes": proximas_devolucoes,
    }
