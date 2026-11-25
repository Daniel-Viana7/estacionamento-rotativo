from datetime import datetime, timedelta

import pytest

from src import estacionamento as e


@pytest.mark.parametrize("placa, esperado", [
    ("ABC1234", "ABC1234"), ("abc1234", "ABC1234"),
    ("ABC-1234", "ABC1234"), ("ABC1D23", "ABC1D23"),
    (" abc1d23 ", "ABC1D23"),
])
def test_validar_placa_valida(placa, esperado):
    # Arrange: placa válida em diferentes formatos.
    # Act
    resultado = e.validar_placa(placa)
    # Assert
    assert resultado == esperado


@pytest.mark.parametrize("placa", ["", "ABC123", "ABCD123", "1234ABC", "ABC-12X4"])
def test_validar_placa_invalida(placa):
    with pytest.raises(ValueError, match="Placa inválida"):
        e.validar_placa(placa)


def test_validar_placa_tipo_incorreto():
    with pytest.raises(ValueError, match="texto"):
        e.validar_placa(None)


@pytest.mark.parametrize("ocupados, capacidade, esperado", [
    ({}, 10, True), ({"A": 1}, 10, True), ({str(i): i for i in range(9)}, 10, True),
    ({str(i): i for i in range(10)}, 10, False), ({}, 1, True),
])
def test_verificar_vaga(ocupados, capacidade, esperado):
    assert e.verificar_vaga(ocupados, capacidade) is esperado


@pytest.mark.parametrize("capacidade", [0, -1, 1.5])
def test_verificar_vaga_capacidade_invalida(capacidade):
    with pytest.raises(ValueError):
        e.verificar_vaga({}, capacidade)


def test_verificar_vaga_excesso_de_veiculos():
    with pytest.raises(ValueError, match="excede"):
        e.verificar_vaga({"A": 1, "B": 2}, 1)


@pytest.mark.parametrize("placa", ["AAA0000", "BBB1111", "CCC2D33", "DDD4444", "EEE5F66"])
def test_registrar_entrada_com_sucesso(placa):
    estacionados = {}
    horario = datetime(2026, 1, 1, 10, 0)
    registro = e.registrar_entrada(placa, estacionados, horario=horario)
    assert registro == {"placa": placa, "entrada": horario}
    assert placa in estacionados


def test_registrar_entrada_placa_duplicada():
    estacionados = {"ABC1234": {"placa": "ABC1234", "entrada": datetime.now()}}
    with pytest.raises(ValueError, match="já está estacionado"):
        e.registrar_entrada("ABC1234", estacionados)


def test_registrar_entrada_estacionamento_lotado():
    estacionados = {str(i): {} for i in range(10)}
    with pytest.raises(ValueError, match="lotado"):
        e.registrar_entrada("ABC1234", estacionados)


def test_registrar_entrada_horario_invalido():
    with pytest.raises(ValueError, match="Horário"):
        e.registrar_entrada("ABC1234", {}, horario="hoje")


@pytest.mark.parametrize("minutos", [0, 1, 30, 60, 61])
def test_calcular_tempo_permanencia(minutos):
    entrada = datetime(2026, 1, 1, 10, 0)
    saida = entrada + timedelta(minutes=minutos)
    assert e.calcular_tempo_permanencia(entrada, saida) == minutos


def test_calcular_tempo_arredonda_segundos_para_minuto():
    inicio = datetime(2026, 1, 1, 10, 0)
    assert e.calcular_tempo_permanencia(inicio, inicio + timedelta(seconds=1)) == 1


def test_calcular_tempo_saida_anterior():
    inicio = datetime(2026, 1, 1, 10, 0)
    with pytest.raises(ValueError, match="anterior"):
        e.calcular_tempo_permanencia(inicio, inicio - timedelta(minutes=1))


def test_calcular_tempo_datas_invalidas():
    with pytest.raises(ValueError, match="datas válidas"):
        e.calcular_tempo_permanencia("10h", datetime.now())


@pytest.mark.parametrize("minutos, esperado", [
    (0, 0.0), (1, 5.0), (59, 5.0), (60, 5.0), (61, 10.0),
])
def test_calcular_valor_por_hora_ou_fracao(minutos, esperado):
    assert e.calcular_valor(minutos) == esperado


def test_calcular_valor_com_taxa_personalizada():
    assert e.calcular_valor(120, 7.5) == 15.0


@pytest.mark.parametrize("minutos", [-1, 1.5, -60])
def test_calcular_valor_tempo_invalido(minutos):
    with pytest.raises(ValueError, match="tempo"):
        e.calcular_valor(minutos)


def test_calcular_valor_taxa_negativa():
    with pytest.raises(ValueError, match="valor por hora"):
        e.calcular_valor(60, -1)


@pytest.mark.parametrize("minutos, esperado", [(0, 0.0), (1, 5.0), (60, 5.0), (61, 10.0), (180, 15.0)])
def test_registrar_saida_calcula_valor_e_libera_vaga(minutos, esperado):
    inicio = datetime(2026, 1, 1, 10, 0)
    estacionados = {"ABC1234": {"placa": "ABC1234", "entrada": inicio}}
    resultado = e.registrar_saida("ABC1234", estacionados, inicio + timedelta(minutes=minutos))
    assert resultado["valor"] == esperado
    assert resultado["tempo_minutos"] == minutos
    assert "ABC1234" not in estacionados


def test_registrar_saida_veiculo_inexistente():
    with pytest.raises(KeyError, match="não encontrado"):
        e.registrar_saida("ABC1234", {})


def test_registrar_saida_placa_invalida():
    with pytest.raises(ValueError, match="Placa inválida"):
        e.registrar_saida("ERRADA", {})


def test_registrar_saida_horario_anterior_nao_remove_veiculo():
    inicio = datetime(2026, 1, 1, 10, 0)
    estacionados = {"ABC1234": {"placa": "ABC1234", "entrada": inicio}}
    with pytest.raises(ValueError, match="anterior"):
        e.registrar_saida("ABC1234", estacionados, inicio - timedelta(minutes=1))
    assert "ABC1234" in estacionados
