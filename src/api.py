from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import agent_union
import time
import json
import os

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR= "cache_reports"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


@app.get("/analise/{ticker}")
async def generate(ticker: str):
    caminho_arquivo = f"{CACHE_DIR}/{ticker}.json"
    if os.path.exists(caminho_arquivo) and time.time() - os.path.getmtime(caminho_arquivo) < 86400:
        print(f"[{ticker}] Achei no CACHE! Entregando rápido...")
        
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_cache= json.load(f)
        return dados_cache
    
    else:
        print(f"Opa, chegou um pedido para {ticker}! Iniciando a IA...")
        AI_result= agent_union(ticker)
        dados_formatadas= json.loads(AI_result)
        dados_formatadas["ativo"]= ticker

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_formatadas, f, ensure_ascii=False, indent=4)

        print(f"IA terminou {ticker}! Devolvendo pro cliente.")
        return dados_formatadas
