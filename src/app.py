from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src import estacionamento as regras

app = FastAPI(title="Estacionamento Rotativo", version="1.0.0")


class EntradaInput(BaseModel):
    placa: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/entrada", status_code=201)
def entrada(dados: EntradaInput):
    try:
        registro = regras.registrar_entrada(dados.placa, regras.ESTACIONADOS)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return {"mensagem": "Entrada registrada", "placa": registro["placa"],
            "entrada": registro["entrada"].isoformat()}


@app.get("/estacionamentos")
def listar_estacionamentos():
    return [
        {"placa": item["placa"], "entrada": item["entrada"].isoformat()}
        for item in regras.ESTACIONADOS.values()
    ]


@app.get("/estacionamentos/{placa}")
def consultar_estacionamento(placa: str):
    try:
        placa_validada = regras.validar_placa(placa)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    registro = regras.ESTACIONADOS.get(placa_validada)
    if registro is None:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return {"placa": registro["placa"], "entrada": registro["entrada"].isoformat()}


@app.post("/saida/{placa}")
def saida(placa: str):
    try:
        return regras.registrar_saida(placa, regras.ESTACIONADOS)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro).strip("'")) from erro


@app.get("/vagas")
def consultar_vagas():
    ocupadas = len(regras.ESTACIONADOS)
    return {"capacidade": regras.CAPACIDADE, "ocupadas": ocupadas,
            "disponiveis": regras.CAPACIDADE - ocupadas}
