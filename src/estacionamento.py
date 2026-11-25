"""Regras de negócio do estacionamento rotativo simplificado."""

from datetime import datetime
from math import ceil
import re

CAPACIDADE = 10
VALOR_POR_HORA = 5.00
ESTACIONADOS: dict[str, dict] = {}


def validar_placa(placa: str) -> str:
    """Valida e normaliza placas no padrão antigo ou Mercosul."""
    if not isinstance(placa, str):
        raise ValueError("A placa deve ser um texto")
    normalizada = placa.strip().upper().replace("-", "").replace(" ", "")
    if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", normalizada):
        raise ValueError("Placa inválida")
    return normalizada


def verificar_vaga(estacionados: dict, capacidade: int = CAPACIDADE) -> bool:
    """Retorna True quando existe ao menos uma vaga disponível."""
    if not isinstance(capacidade, int) or capacidade <= 0:
        raise ValueError("A capacidade deve ser um número inteiro positivo")
    if len(estacionados) > capacidade:
        raise ValueError("Quantidade de veículos excede a capacidade")
    return len(estacionados) < capacidade


def registrar_entrada(placa: str, estacionados: dict, capacidade: int = CAPACIDADE,
                      horario: datetime | None = None) -> dict:
    """Registra um veículo se a placa for válida e houver vaga."""
    placa_validada = validar_placa(placa)
    if placa_validada in estacionados:
        raise ValueError("Veículo já está estacionado")
    if not verificar_vaga(estacionados, capacidade):
        raise ValueError("Estacionamento lotado")
    entrada = horario or datetime.now()
    if not isinstance(entrada, datetime):
        raise ValueError("Horário de entrada inválido")
    registro = {"placa": placa_validada, "entrada": entrada}
    estacionados[placa_validada] = registro
    return registro


def calcular_tempo_permanencia(entrada: datetime, saida: datetime) -> int:
    """Calcula a permanência em minutos, arredondando frações para cima."""
    if not isinstance(entrada, datetime) or not isinstance(saida, datetime):
        raise ValueError("Os horários devem ser datas válidas")
    segundos = (saida - entrada).total_seconds()
    if segundos < 0:
        raise ValueError("A saída não pode ser anterior à entrada")
    return ceil(segundos / 60)


def calcular_valor(minutos: int, valor_hora: float = VALOR_POR_HORA) -> float:
    """Cobra R$ 5,00 por hora ou fração; permanência zero não gera cobrança."""
    if not isinstance(minutos, int) or minutos < 0:
        raise ValueError("O tempo deve ser um número inteiro de minutos não negativo")
    if valor_hora < 0:
        raise ValueError("O valor por hora não pode ser negativo")
    horas_cobradas = ceil(minutos / 60)
    return round(horas_cobradas * valor_hora, 2)


def registrar_saida(placa: str, estacionados: dict,
                    horario: datetime | None = None) -> dict:
    """Finaliza o estacionamento, calcula a cobrança e libera a vaga."""
    placa_validada = validar_placa(placa)
    if placa_validada not in estacionados:
        raise KeyError("Veículo não encontrado")
    saida = horario or datetime.now()
    registro = estacionados[placa_validada]
    minutos = calcular_tempo_permanencia(registro["entrada"], saida)
    valor = calcular_valor(minutos)
    resultado = {
        "placa": placa_validada,
        "entrada": registro["entrada"].isoformat(),
        "saida": saida.isoformat(),
        "tempo_minutos": minutos,
        "valor": valor,
    }
    del estacionados[placa_validada]
    return resultado
