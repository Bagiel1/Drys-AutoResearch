import time
import os
import requests
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()
gateway_token= os.getenv("GATEWAY_TOKEN")

tempo_descanso= 2
maximo= 2

headers= {
    "Authorization": f"Bearer {gateway_token}",
    "Content-Type": "application/json"
}

def get_real_data(ticker):
    ticker_yf= f"{ticker}.SA" if not ticker.endswith(".SA") else ticker

    try:
        share= yf.Ticker(ticker_yf)
        info= share.info

        pl= info.get('trailingPE', 'N/A')
        roe= info.get('returnOnEquity', 'N/A')

        if isinstance(pl, float):
            pl= f"{pl:.2f}"

        if isinstance(roe, float):
            roe_format= f"{roe * 100:.2f}%"
        else:
            roe_format= str(roe)

        raw_data= f"OFICIAL DATA (YFINANCE) - P/L: {pl} | ROE: {roe_format}"
        return raw_data

    except Exception as e:
        return f"OFICIAL DATA (YFINCANCE) - ERROR: {e}"

def exec_agent_api(user_prompt, agent="main", system_prompt= None):
    url= "http://127.0.0.1:18789/v1/chat/completions"
    message= []

    if system_prompt:
        message.append({"role": "system", "content": system_prompt})

    message.append({"role": "user", "content": user_prompt})

    payload= {
        "model": f"openclaw/{agent}",
        "messages": message
    }

    answer= requests.post(url, headers= headers, json= payload)
    data= answer.json()

    if "choices" not in data:
        print(f"[API ERROR]: {data}")
        return "API ERROR"
    
    text_answer= data['choices'][0]['message']['content']
    return text_answer


def auditor_report(report, ticker):
    print(f"   [!] Final audit for {ticker}...")
    personality = (
        "Você é um auditor sênior de investimentos implacável. "
        "Você não tem medo de dar recomendações diretas. Você NUNCA fica em cima do muro."
    )
    task = (
        f"Analise este relatorio de {ticker}: \n\n{report}\n\n"
        "Sua tarefa: Reescreva o relatório organizando em tópicos claros (Markdown).\n"
        "ATENÇÃO: Corrija todas as contradições. Se houver informações divergentes entre "
        "o texto original e a seção 'Adendo da Auditoria', os dados do Adendo são a "
        "VERDADE ABSOLUTA e devem substituir os originais.\n"
        "Não escreva a palavra 'Adendo' no texto final. Incorpore a correção naturalmente. "
        "Adicione uma seção chamada 'ANÁLISE DE RISCOS'.\n\n"
        "REGRA ABSOLUTA E INQUEBRÁVEL: A ÚLTIMA LINHA do seu texto DEVE ser "
        "exclusivamente o veredito final no formato exato: '**Veredito: COMPRA**', '**Veredito: VENDA**' ou '**Veredito: MANTER**'. "
        "Sem exceções."
    )

    answer= exec_agent_api(
        user_prompt= task, 
        agent= "auditor",
        system_prompt= personality
    )

    return answer


def extract_metrics(report, ticker):
    personality = (
        "Você é um extrator de dados robótico. Você não inventa palavras."
    )
    task = (
        f"Baseado no relatório abaixo, extraia apenas três informações: "
        f"1. Recomendação (Compra, Venda ou Manter), "
        f"2. Score de 0 a 10 (onde 0 é péssimo e 10 é excelente), "
        f"3. Nível de Risco (Baixo, Médio, Alto). "
        f"Retorne OBRIGATORIAMENTE no formato: Recomendação | Score | Risco. Exemplo: Compra | 8.5 | Médio\n\n"
        f"Relatório: {report}\n\n"
        f"Não escreva absolutamente nada a mais."
    )
    
    metrics = exec_agent_api(user_prompt=task, agent="metrics", system_prompt=personality)
    return metrics


'''
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
'''

def rescue_agent(report, ticker, reason, oficial_data):
    personality = (
        "Sua função é corrigir relatórios de seus colegas. "
        "Você NUNCA reescreve textos completos e não inventa dados."
    )
    task = (
        f"O relatório de {ticker} está com este erro: '{reason}'.\n\n"
        f"DADOS OFICIAIS REAIS PARA USAR NA CORREÇÃO: {oficial_data}\n\n"
        f"Relatório Atual: {report}\n\n"
        "Sua missão: Escreva APENAS UM PARÁGRAFO contendo a informação exata para suprir essa falha, "
        "USANDO SE NECESSÁRIO OS DADOS OFICIAIS FORNECIDOS ACIMA. "
        "Se o dado oficial for N/A, diga que o indicador é N/A ou inexistente. "
        "Não reescreva o relatório todo. Retorne OBRIGATORIAMENTE apenas a frase com a correção."
    )

    rescue_answer= exec_agent_api(user_prompt=task, agent="rescue", system_prompt=personality)

    return rescue_answer    
    
def judge(report, ticker, oficial_data):

    personality = (
        "Você é um auditor de qualidade extremamente rígido e literal. "
        "Você não avalia a qualidade da ação, apenas verifica se os dados estão corretos e presentes."
    )
    task = (
        f"Analise este relatorio de {ticker}:\n\n{report}\n\n"
        f"DADOS OFICIAIS REAIS PARA CONFERÊNCIA:\n{oficial_data}\n\n"
        "Verifique se o relatório cumpre TODOS os 4 requisitos abaixo:\n"
        "1. Contém o valor exato do P/L informados nos dados oficiais?\n"
        "(Se o dado oficial for 'N/A', o texto DEVE dizer que é 'N/A', 'inexistente' ou 'negativo').\n"
        "2. Contém o valor exato do ROE informados nos dados oficiais? (Mesma regra do 'N/A')\n"
        "3. Cita pelo menos uma notícia, polêmica ou fato relevante?\n\n"
        "4. Relatorio esta completo e coerente, sem redundância?\n\n"
        "ATENÇÃO: Se houver uma seção chamada '### Adendo da Auditoria' no final do texto, "
        "considere APENAS os dados do Adendo, pois eles corrigem o texto original.\n\n"
        "REGRA DE DECISÃO:\n"
        "- Se possuir os 4 itens corretos, responda apenas: SIM\n"
        "- Se faltar QUALQUER UM ou estiver com o NÚMERO ERRADO, responda: NAO\n\n"
        "Se responder NAO, justifique na linha de baixo (máximo 4 palavras) dizendo o que faltou ou o que está errado."
    )

    judge_answer= exec_agent_api(user_prompt=task, agent="judge", system_prompt=personality)

    return judge_answer

def rapporteur(ticker):
    print(f"------Starting the search of {ticker}\n")

    oficial_data= get_real_data(ticker)

    personality= (
        "Você é um relator de ativos financeiros. "
        "Você é profissional e não inventa dados quando não os encontra. "
        "Caso ocorra de não encontrar o dado, somente diga que não o achou. "
    )
    task= (
        f"Analise as ultimas noticias de {ticker} de 2026, "
        "faça uma analise profunda sobre o ativo, incluindo polêmicas, "
        "fatores que possam prejudicar a segurança do investidor, e coisas positivas.\n"
        f"DADOS OFICIAIS ABSOLUTOS: {oficial_data}\n\n"
        "REGRA DE OURO PARA INDICADORES: Use os dados oficiais acima. "
        "Se o P/L ou ROE oficial estiver como 'N/A', isso significa que a empresa dá prejuízo "
        "ou o dado é matematicamente impossível. Nesse caso, NÃO tente procurar esse número na web. "
        "Escreva expressamente no seu texto que o P/L ou ROE é 'N/A' ou 'Inexistente'."
    )

    inicial_answer= exec_agent_api(user_prompt=task, agent="rapporteur", system_prompt=personality)
    
    return inicial_answer


def agent_union(ticker):
    report= rapporteur(ticker)
    oficial_data= get_real_data(ticker)
    for i in range(maximo):

        print(f"   [!] Cooling API for {tempo_descanso}s...")
        time.sleep(tempo_descanso)
        
        binary_answer= judge(report, ticker, oficial_data)
        lines= [line.strip() for line in binary_answer.split("\n") if line.strip() != ""]

        if not lines:
            lines= ["NAO", "IA NAO RETORNOU JUSTIFICATIVA."]

        decision_raw= lines[0].upper().replace("Ã", "A").replace(".", "")
        decision= "SIM" if "SIM" in decision_raw else "NAO"

        if len(lines) > 1:
            judge_reason= lines[1]

        print(f"   -> Attempt {i+1} of {maximo} for {ticker}... Judge said {decision}")

        if('SIM' in decision):
            print(f"   [+] Judge approved the report of {ticker}!")
            break
        
        elif('NAO' in decision):
            print(f"      [Reason]: {judge_reason}")
            answer_rescue= rescue_agent(report, ticker, judge_reason, oficial_data)

            report= report + f"\n\n### Adendo da Auditoria:\n{answer_rescue}"

            #lacunas= extrair_perguntas(resultado_acumulado, ticker)
            #for item in lacunas:
            #    print(f"Mensagem sobre {item}\n")
            #    mensagem= (
            #    f"Busque DADOS NUMÉRICOS REAIS e ATUALIZADOS sobre {item} do ativo {ticker}. "
            #    "Não responda com generalidades. Se for P/L, traga o número. Se for notícia, traga a data e o fato."
            #    )

    time.sleep(tempo_descanso)
    print(f"   [!] Cooling API for {tempo_descanso}s...")
    final_report= auditor_report(report, ticker)

    return final_report

def main():
    wallet= ["AMER3","OIBR3"]

    if not os.path.exists("samples"):
        os.makedirs("samples")

    out_file= "samples/wallet_analysis.md"
        
    with open(out_file, "w") as f:
        pass

    resume = []

    for share in wallet:
        final_report = agent_union(share)
        metrics = extract_metrics(final_report, share)
        
        resume.append({"ativo": share, "info": metrics})

        with open(out_file, "a") as f:
            f.write(f"## Análise Detalhada: {share}\n\n{final_report}\n\n---\n\n")

    print("   [!] Gerando Tabela Resumo...")
    with open(out_file, "r+") as f:
        conteudo = f.read()
        f.seek(0, 0)
        f.write("# 📊 DASHBOARD DE INVESTIMENTOS - DRÝS CAPITAL\n\n")
        f.write("## Relatório Consolidado de Análise Sintética\n\n")
        f.write("| Ativo | Recomendação | Score | Risco |\n")
        f.write("|-------|--------------|-------|-------|\n")
        
        for item in resume:
            partes = [p.strip() for p in item["info"].split("|")]
            if len(partes) == 3:
                rec, score, risco = partes
                f.write(f"| {item['ativo']:<6} | {rec:<12} | {score:<5} | {risco:<7} |\n")
        
        f.write("\n\n" + conteudo) 


if __name__ == "__main__":
    main()