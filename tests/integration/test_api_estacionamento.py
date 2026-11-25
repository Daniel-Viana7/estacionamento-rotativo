import pytest
from fastapi.testclient import TestClient

from src.app import app
from src import estacionamento as regras

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpar_estacionamento():
    regras.ESTACIONADOS.clear()
    yield
    regras.ESTACIONADOS.clear()


def test_health_retorna_ok():
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_post_entrada_cria_registro():
    resposta = client.post("/entrada", json={"placa": "ABC1234"})
    assert resposta.status_code == 201
    assert resposta.json()["placa"] == "ABC1234"
    assert "entrada" in resposta.json()


def test_post_entrada_placa_invalida_retorna_400():
    resposta = client.post("/entrada", json={"placa": "INVALIDA"})
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Placa inválida"


def test_get_estacionamentos_lista_veiculos():
    client.post("/entrada", json={"placa": "ABC1234"})
    resposta = client.get("/estacionamentos")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["placa"] == "ABC1234"


def test_get_estacionamentos_lista_vazia():
    resposta = client.get("/estacionamentos")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_get_estacionamento_por_placa():
    client.post("/entrada", json={"placa": "ABC1234"})
    resposta = client.get("/estacionamentos/ABC1234")
    assert resposta.status_code == 200
    assert resposta.json()["placa"] == "ABC1234"


def test_get_estacionamento_inexistente_retorna_404():
    resposta = client.get("/estacionamentos/ABC1234")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Veículo não encontrado"


def test_post_saida_finaliza_e_retorna_cobranca():
    client.post("/entrada", json={"placa": "ABC1234"})
    # Ajusta a entrada para um horário conhecido para tornar a cobrança determinística.
    from datetime import datetime, timedelta
    regras.ESTACIONADOS["ABC1234"]["entrada"] = datetime.now() - timedelta(minutes=61)
    resposta = client.post("/saida/ABC1234")
    assert resposta.status_code == 200
    assert resposta.json()["placa"] == "ABC1234"
    assert resposta.json()["valor"] == 10.0
    assert "ABC1234" not in regras.ESTACIONADOS


def test_post_saida_veiculo_inexistente_retorna_404():
    resposta = client.post("/saida/ABC1234")
    assert resposta.status_code == 404


def test_get_vagas_retorna_capacidade_e_disponibilidade():
    client.post("/entrada", json={"placa": "ABC1234"})
    resposta = client.get("/vagas")
    assert resposta.status_code == 200
    assert resposta.json() == {"capacidade": 10, "ocupadas": 1, "disponiveis": 9}


def test_get_vagas_estacionamento_vazio():
    resposta = client.get("/vagas")
    assert resposta.status_code == 200
    assert resposta.json()["disponiveis"] == 10
