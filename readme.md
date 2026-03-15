# 📊 Drys-AutoResearch

**Drys-AutoResearch** é um framework de análise financeira autónoma que utiliza uma arquitetura **Multi-Agente** para mitigar alucinações em Modelos de Linguagem (LLMs). O sistema foi projetado para minerar indicadores técnicos e factos relevantes em tempo real, garantindo governança de dados para decisões de investimento.

---

## 🧠 Arquitetura e Governança

O diferencial deste projeto é o loop de **Reflexão Crítica e Enriquecimento**. O sistema opera em camadas lógicas:

1.  **Exploração de Contexto**
    * Realiza a varredura primária na web em busca de notícias e fundamentos do ativo.
2.  **O Juiz (Quality Assurance)**
    * Analisa o relatório preliminar e aplica um "veto" (NAO) caso faltem indicadores cruciais (P/L, ROE, Notícias de 2026).
3.  **Self-Healing (Agente de Resgate)**
    * Acionado sob veto, identifica as lacunas apontadas pelo Juiz e realiza uma pesquisa cirúrgica para corrigir o contexto.
4.  **Deep Research (Enriquecimento de Dados)**
    * Independentemente da aprovação inicial, o sistema identifica e responde a 2 perguntas extremamente específicas sobre o futuro do ativo (ex: projeções de CAPEX ou impactos de leilões específicos) para garantir profundidade analítica.
5.  **Auditoria Sénior**
    * Consolida o output final, elimina contradições e emite o veredito assertivo (COMPRA, VENDA ou MANTER).

---

## 🛠️ Guia de Instalação e Uso

### 1. Pré-requisitos
* Python 3.10 ou superior.
* OpenClaw CLI instalado.

### 2. Configuração do Ambiente
Primeiro, autentique a sua API Key e configure o agente principal:

    # Autenticação na OpenAI via CLI
    openclaw auth

    # Criação do agente utilizando GPT-4o
    openclaw agents add main --model gpt-4o

### 3. Execução do Projeto
Clone o repositório e inicie a pipeline:

    python main.py

O dashboard consolidado será gerado automaticamente no diretório:  
`samples/analise_carteira.md`

---

## 📁 Estrutura do Repositório

* `main.py`: Orquestrador da lógica de agentes e controlo de fluxo.
* `samples/`: Exemplos de outputs gerados pelo sistema (ex: Análise da WEGE3).

---
*Desenvolvido por Gabriel (Bagiel) – Estudante de Sistemas de Informação (ICMC-USP).*
