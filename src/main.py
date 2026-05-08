import time
import os
import requests
from dotenv import load_dotenv
import yfinance as yf
from fastapi import FastAPI


load_dotenv()
gateway_token= os.getenv("GATEWAY_TOKEN")

tempo_descanso= 0.5
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
        dy= info.get('dividendYield', 'N/A')
        pvp= info.get('priceToBook', 'N/A')
        liqmarg= info.get('profitMargins', 'N/A')
        alavac= info.get('debtToEquity', 'N/A')

        if isinstance(pl, float):
            pl= f"{pl:.2f}"

        if isinstance(roe, float):
            roe_format= f"{roe * 100:.2f}%"
        else:
            roe_format= str(roe)

        if isinstance(dy, float):
            dy_format= f"{dy * 100:.2f}%"
        else:
            dy_format= str(dy)

        if isinstance(pvp, float):
            pvp_format= f"{pvp:.2f}"

        if isinstance(liqmarg, float):
            liqmarg_format= f"{liqmarg * 100:.2f}%"
        else:
            liqmarg_format= str(liqmarg)

        if isinstance(alavac, float):
            alavac_format= f"{alavac * 100:.2f}%"


        raw_data= f"OFICIAL DATA (YFINANCE) - P/L: {pl} | ROE: {roe_format}"
        raw_dict= {"pl": pl, "roe": roe, "dy": dy, "pvp": pvp, "liqmarg": liqmarg, "alavac": alavac}
        return raw_data, raw_dict

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
        "Sua tarefa: Transforme e reescreva este relatório EXCLUSIVAMENTE em um formato JSON válido.\n"
        "ATENÇÃO: Corrija todas as contradições. Se houver informações divergentes entre "
        "o texto original e a seção 'Adendo da Auditoria', os dados do Adendo são a "
        "VERDADE ABSOLUTA e devem substituir os originais. Incorpore a correção naturalmente sem citar a palavra 'Adendo'.\n\n"
        
        "--- REGRAS DE FORMATAÇÃO E CONTEÚDO (LEIA COM ATENÇÃO) ---\n"
        "1. 'analise_geral': Escreva o texto COMPLETO. PROIBIDO resumir. OBRIGATÓRIO: Use os caracteres exatos \\n\\n para separar os parágrafos.\n"
        "2. 'noticias': Liste TODAS as notícias na íntegra. PROIBIDO resumir. OBRIGATÓRIO: Formate em tópicos. Inicie cada nova linha exata e unicamente com o caractere '- '.\n"
        "3. 'analise_de_risco': Escreva a análise crítica COMPLETA. PROIBIDO resumir. OBRIGATÓRIO: Use os caracteres \\n\\n para separar os parágrafos.\n\n"
        
        "REGRA ABSOLUTA E INQUEBRÁVEL 1: Sua resposta não pode conter NENHUM texto antes ou depois do JSON. "
        "NÃO USE os marcadores de código do Markdown (como ```json). A primeira letra da sua resposta DEVE ser '{' e a última '}'.\n\n"
        
        "REGRA ABSOLUTA E INQUEBRÁVEL 2: Você DEVE usar OBRIGATORIAMENTE a estrutura exata de chaves abaixo para montar o seu JSON. Não invente chaves novas:\n"
        "{\n"
        '  "analise_geral": "[Insira a análise geral aqui respeitando a regra 1]",\n'
        '  "pl": "Insira o valor numérico exato do P/L ou N/A",\n'
        '  "roe": "Insira a porcentagem exata do ROE ou N/A",\n'
        '  "noticias": "[Insira os tópicos das notícias aqui respeitando a regra 2]",\n'
        '  "analise_de_risco": "[Insira a análise de riscos aqui respeitando a regra 3]",\n'
        '  "veredito": "EXATAMENTE UMA DAS TRÊS PALAVRAS: COMPRA, VENDA ou MANTER (em maiúsculo)",\n'
        '  "nivel_risco": "Escreva apenas: Baixo, Medio ou Alto", \n'
        '  "score": "Escreva apenas o numero de 0 a 10" \n'        
        "}\n"
    )

    answer= exec_agent_api(
        user_prompt= task, 
        agent= "auditor",
        system_prompt= personality
    )

    return answer

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
        "Se o P/L ou ROE oficial estiver como 'N/A', isso significa que a empresa dá prejuízo."
        "ou o dado é matematicamente impossível. Nesse caso, NÃO tente procurar esse número na web. "
        "Escreva expressamente no seu texto que o P/L ou ROE é 'N/A' ou 'Inexistente'."
        "OBRIGATÓRIO: Você DEVE usar a sua ferramenta de busca na internet (web search) para investigar a fundo o ativo {ticker}.\n"
        "REGRA ANTI-PREGUIÇA: É ESTRITAMENTE PROIBIDO retornar páginas genéricas de cotação, homepages de portais (como StatusInvest, InfoMoney Cotações, Fundamentus) ou índices vazios.\n"
        "Você deve buscar por EVENTOS REAIS e ESPECÍFICOS dos últimos 6 meses cruzando o nome da empresa com palavras como: 'lucro', 'prejuízo', 'polêmica', 'investigação', 'dívida' ou 'recuperação judicial'.\n"
        "Para cada uma das 3 notícias encontradas, você deve processar a página e descrever no seu relatório: O QUE aconteceu de fato, QUANDO aconteceu, e QUAL O IMPACTO financeiro real para a empresa."
    )

    inicial_answer= exec_agent_api(user_prompt=task, agent="rapporteur", system_prompt=personality)
    
    return inicial_answer


def agent_union(ticker):
    report= rapporteur(ticker)
    oficial_data, oficial_data_dict= get_real_data(ticker)
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

    time.sleep(tempo_descanso)
    print(f"   [!] Cooling API for {tempo_descanso}s...")
    final_report= auditor_report(report, ticker)

    final_report.update(oficial_data_dict)

    return final_report

def main():
    wallet= ["AMER3","OIBR3"]

    if not os.path.exists("samples"):
        os.makedirs("samples")

    out_file= "samples/wallet_analysis.json"
        
    with open(out_file, "w") as f:
        pass

    resume = []

    for share in wallet:
        final_report = agent_union(share)

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