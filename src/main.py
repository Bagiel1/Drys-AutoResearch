import subprocess
import time
import os
import shutil

carteira= ["WEGE3","SUZB3"]

tempo_descanso= 5
maximo= 2

def limpar_memoria_main():
    path_memoria= os.path.expanduser("~/.openclaw/agents/main")

    if os.path.exists(path_memoria):
        shutil.rmtree(path_memoria, ignore_errors=True)

        comando= ["openclaw", "agents", "add", "main"]
        subprocess.run(comando, input="\n", text=True, capture_output="True")

def executar_agente(mensagem, thinking_level='low'):
    comando = [
        "openclaw", "agent",
        "--agent", "main",
        "--local",
        "--thinking", thinking_level,
        "--message", mensagem
    ]
    res = subprocess.run(comando, capture_output=True, text=True)
    return res 

def auditor_relatorio(relatorio, ticker):
    print(f"   [!] Auditoria final iniciando para {ticker}...")
    mensagem = (
        f"Você é um auditor sênior de investimentos. Analise este relatório de {ticker}:\n\n"
        f"{relatorio}\n\n"
        "Sua tarefa: Reescreva o relatório corrigindo possíveis contradições, "
        "organizando em tópicos claros (Markdown) e garantindo que o veredito "
        "(Comprar/Vender/Segurar) esteja bem fundamentado. "
        "Adicione uma seção final chamada 'ANÁLISE DE RISCO'."
        "Seja extremamente assertivo. O veredito deve ser COMPRA, VENDA ou MANTER. Proibido 'monitorar'"
    )
    res = executar_agente(mensagem, thinking_level="medium")
    return res.stdout

def extrair_metricas(relatorio, ticker):
    mensagem = (
        f"Baseado no relatório abaixo, extraia apenas três informações: "
        f"1. Recomendação (Compra, Venda ou Neutro), "
        f"2. Score de 0 a 10 (onde 0 é péssimo e 10 é excelente), "
        f"3. Nível de Risco (Baixo, Médio, Alto). "
        f"Retorne no formato: Recomendação | Score | Risco. Exemplo: Compra | 8.5 | Médio\n\n"
        f"Relatório: {relatorio}"
        f"Nao escreva nada a mais que isso."
    )
    res = executar_agente(mensagem)
    return res.stdout.strip()

def extrair_perguntas(contexto, ticker):
    
    mensagem= (f"Analise o que já foi levantado sobre {ticker}: \n\n{contexto}\n\n"
        "As pesquisas anteriores falharam em convencer o Juiz. "
        "Identifique 2 detalhes MUITO ESPECÍFICOS e diferentes que ainda não foram respondidos com precisão. "
        "Exemplo: Em vez de 'P/L', peça 'Relação Preço/Lucro projetada para o final de 2026 segundo o último balanço'."
        "Retorne apenas os tópicos, um por linha.")
    res= executar_agente(mensagem)

    perguntas = []
    for linha in res.stdout.split('\n'):
        linha_limpa = linha.replace('-', '').replace('*', '').strip()
        if linha_limpa:
            perguntas.append(linha_limpa)
    return perguntas[:3]

def juiz(resposta_anterior, ticker):
    
    mensagem = (
        f"Analise criticamente este relatório de {ticker}: {resposta_anterior}\n\n"
        "Critérios de Rejeição (Diga NAO caso ele se encaixe em 2 desses requisitos):"
        "1. Não apresenta o P/L (Preço/Lucro) atualizado de 2025 ou 2026."
        "2. Não menciona o ROE (Retorno sobre Patrimônio) da empresa."
        "3. Não cita pelo menos uma notícia relevante dos últimos 30 dias."
        "4. O texto é genérico e não cita números específicos de balanço.\n\n"
        "5. Se o texto for apenas um resumo superficial sem esses dados técnicos, "
        "responda apenas NAO. Se estiver completo com indicadores e notícias, responda apenas SIM."
        "Justifique a resposta em uma linha abaixo bem sucintamente, no maximo 3 palavras."
        "Exemplo:\n"
        "NAO\n"
        "Falta PL atualizado"
    )
    resposta_juiz= executar_agente(mensagem, thinking_level="medium")

    resposta_juiz= resposta_juiz.stdout.strip().upper()
    return resposta_juiz

def pesquisar_ativo(ticker):
    limpar_memoria_main()
    print(f"------Iniciando a Pesquisa de {ticker}\n")

    mensagem= f"Analise as ultimas noticias de {ticker} de 2026, faça uma analise profunda sobre o ativo e de o veredito se a recomendação é comprar, vender ou segurar."
    resultado_inicial= executar_agente(mensagem)
    
    resultado_acumulado= resultado_inicial.stdout

    for i in range(maximo):

        time.sleep(tempo_descanso)
        print(f"   [!] Resfriando a API por {tempo_descanso}s...")

        resposta_simnao= juiz(resultado_acumulado, ticker)
        resposta_simnao = resposta_simnao.upper().replace("Ã", "A").replace(".", "").strip()
        decisao= resposta_simnao.split('\n')[0]

        print(f"   -> Tentativa {i+1} de {maximo} para {ticker}... Juiz disse {decisao}")
        if len(resposta_simnao.split('\n')) > 1:
            motivo_juiz= resposta_simnao.split('\n')[1]
            print(f"      [MOTIVO]: {resposta_simnao.split('\n')[1]}")

        if('SIM' in decisao):
            print(f"   [+] Juiz aprovou o relatório de {ticker}!")
            break
        
        elif('NAO' in decisao):
            msg_resgate = (
                f"Você é um editor de dados. O relatório atual de {ticker} está com este erro: '{motivo_juiz}'.\n\n"
                f"Relatório Atual: {resultado_acumulado}\n\n"
                "Sua missão: REESCREVA o relatório acima corrigindo EXCLUSIVAMENTE os dados citados no erro. "
                "Mantenha o restante do texto, mas garanta que o dado novo (P/L e ROE reais de 2025/2026) "
                "substitua o dado antigo e errado. Seja preciso e não invente outros dados."
            )
            time.sleep(tempo_descanso)
            print(f"   [!] Resfriando a API por {tempo_descanso}s...")
            res_resgate= executar_agente(msg_resgate, thinking_level="medium")


            resultado_acumulado= res_resgate.stdout

            lacunas= extrair_perguntas(resultado_acumulado, ticker)
            for item in lacunas:
                print(f"Mensagem sobre {item}\n")
                mensagem= (
                f"Busque DADOS NUMÉRICOS REAIS e ATUALIZADOS sobre {item} do ativo {ticker}. "
                "Não responda com generalidades. Se for P/L, traga o número. Se for notícia, traga a data e o fato."
                )

                time.sleep(tempo_descanso)
                print(f"   [!] Resfriando a API por {tempo_descanso}s...")
                res= executar_agente(mensagem, thinking_level="medium")

                resultado_acumulado += f"\n\n## Info Adicional ({item}): \n{res.stdout}"

    time.sleep(tempo_descanso)
    print(f"   [!] Resfriando a API por {tempo_descanso}s...")
    relatorio_final= auditor_relatorio(resultado_acumulado, ticker)

    return relatorio_final

if not os.path.exists("samples"):
    os.makedirs("samples")

arquivo_saida= "samples/analise_carteira.md"
    
with open(arquivo_saida, "w") as f:
    pass

resumo_executivo = []

for ativo in carteira:
    relatorio_final = pesquisar_ativo(ativo)
    metricas = extrair_metricas(relatorio_final, ativo)
    
    resumo_executivo.append({"ativo": ativo, "info": metricas})

    with open(arquivo_saida, "a") as f:
        f.write(f"## Análise Detalhada: {ativo}\n\n{relatorio_final}\n\n---\n\n")

print("   [!] Gerando Tabela Resumo...")
with open(arquivo_saida, "r+") as f:
    conteudo = f.read()
    f.seek(0, 0)
    f.write("# 📊 DASHBOARD DE INVESTIMENTOS - DRÝS CAPITAL\n\n")
    f.write("## Relatório Consolidado de Análise Sintética\n\n")
    f.write("| Ativo | Recomendação | Score | Risco |\n")
    f.write("|-------|--------------|-------|-------|\n")
    
    for item in resumo_executivo:
        partes = [p.strip() for p in item["info"].split("|")]
        if len(partes) == 3:
            rec, score, risco = partes
            f.write(f"| {item['ativo']:<6} | {rec:<12} | {score:<5} | {risco:<7} |\n")
    
    f.write("\n\n" + conteudo) 