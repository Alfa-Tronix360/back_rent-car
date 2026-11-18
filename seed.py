"""Dados iniciais do Rent-a-Car.

Corre automaticamente no arranque da API (idempotente): só cria os dados
se a base de dados estiver vazia.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

import models
from auth import hash_password


def _ja_existe(db: Session) -> bool:
    return db.query(models.Usuario).count() > 0


def seed(db: Session) -> None:
    if _ja_existe(db):
        return

    # ---------- Utilizadores ----------
    admin = models.Usuario(
        nome="Administrador",
        email="admin@rentacar.ao",
        hashed_password=hash_password("admin123"),
        perfil="admin",
    )
    funcionario = models.Usuario(
        nome="Funcionário",
        email="funcionario@rentacar.ao",
        hashed_password=hash_password("funcionario123"),
        perfil="funcionario",
    )
    db.add_all([admin, funcionario])
    db.commit()

    # ---------- Veículos ----------
    veiculos = [
        models.Veiculo(
            matricula="LD-01-AA", marca="Toyota", modelo="Corolla", ano=2022,
            categoria="Sedan", combustivel="Gasolina", transmissao="Automática",
            lugares=5, preco_dia=45000, estado="Disponível",
        ),
        models.Veiculo(
            matricula="LD-02-BB", marca="Toyota", modelo="Hilux", ano=2021,
            categoria="Pickup", combustivel="Diesel", transmissao="Manual",
            lugares=5, preco_dia=75000, estado="Disponível",
        ),
        models.Veiculo(
            matricula="LD-03-CC", marca="Hyundai", modelo="i10", ano=2023,
            categoria="Económico", combustivel="Gasolina", transmissao="Manual",
            lugares=4, preco_dia=30000, estado="Disponível",
        ),
        models.Veiculo(
            matricula="LD-04-DD", marca="Mitsubishi", modelo="Pajero", ano=2020,
            categoria="SUV", combustivel="Diesel", transmissao="Automática",
            lugares=7, preco_dia=90000, estado="Manutenção",
        ),
        models.Veiculo(
            matricula="LD-05-EE", marca="Kia", modelo="Sportage", ano=2022,
            categoria="SUV", combustivel="Gasolina", transmissao="Automática",
            lugares=5, preco_dia=65000, estado="Disponível",
        ),
    ]
    db.add_all(veiculos)
    db.commit()

    # ---------- Clientes ----------
    clientes = [
        models.Cliente(
            nome="João Manuel", documento="004512345LA041", email="joao.manuel@email.ao",
            telefone="+244 923 111 222", endereco="Luanda, Talatona",
            carta_conducao="CD-123456", validade_carta="2027-05-10",
        ),
        models.Cliente(
            nome="Maria Fernandes", documento="003298765LA042", email="maria.fernandes@email.ao",
            telefone="+244 924 333 444", endereco="Luanda, Miramar",
            carta_conducao="CD-654321", validade_carta="2026-11-20",
        ),
        models.Cliente(
            nome="Carlos Domingos", documento="002134567LA043", email="carlos.domingos@email.ao",
            telefone="+244 925 555 666", endereco="Benguela, Centro",
            carta_conducao="CD-112233", validade_carta="2028-02-15",
        ),
    ]
    db.add_all(clientes)
    db.commit()

    # ---------- Alugueres ----------
    hoje = datetime.now()
    alugueres = [
        models.Aluguer(
            numero="ALG-0001", cliente_id=clientes[0].id, veiculo_id=veiculos[0].id,
            data_inicio=hoje - timedelta(days=3), data_fim=hoje + timedelta(days=2),
            valor_diaria=45000, dias=5, total=225000, estado="Ativo",
            observacoes="Aluguer em curso.",
        ),
        models.Aluguer(
            numero="ALG-0002", cliente_id=clientes[1].id, veiculo_id=veiculos[1].id,
            data_inicio=hoje + timedelta(days=5), data_fim=hoje + timedelta(days=10),
            valor_diaria=75000, dias=5, total=375000, estado="Reservado",
        ),
        models.Aluguer(
            numero="ALG-0003", cliente_id=clientes[2].id, veiculo_id=veiculos[2].id,
            data_inicio=hoje - timedelta(days=15), data_fim=hoje - timedelta(days=12),
            valor_diaria=30000, dias=3, total=90000, estado="Concluído",
        ),
    ]
    db.add_all(alugueres)
    db.commit()

    # O veículo do aluguer ativo fica marcado como alugado
    veiculos[0].estado = "Alugado"

    # ---------- Pagamentos ----------
    pagamentos = [
        models.Pagamento(
            aluguer_id=alugueres[0].id, valor=100000, metodo="Transferência",
            estado="Pago", data=hoje - timedelta(days=3),
        ),
        models.Pagamento(
            aluguer_id=alugueres[1].id, valor=100000, metodo="Multicaixa",
            estado="Pago", data=hoje - timedelta(days=1),
        ),
        models.Pagamento(
            aluguer_id=alugueres[2].id, valor=90000, metodo="Numerário",
            estado="Pago", data=hoje - timedelta(days=15),
        ),
    ]
    db.add_all(pagamentos)
    db.commit()

    print("Seed concluído: 2 utilizadores, 5 veículos, 3 clientes, 3 alugueres, 3 pagamentos.")


if __name__ == "__main__":
    import database

    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
