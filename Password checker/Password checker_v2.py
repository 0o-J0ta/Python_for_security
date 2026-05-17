import requests
import json
import re
import hashlib
import os 
import getpass
from datetime import datetime, timedelta

#URL da lista de senhas comuns(seclist)

URL_SENHAS = (
    "https://raw.githubusercontent.com/danielmiessler/"
    "SecLists/refs/heads/master/Passwords/Common-Credentials/"
    "10-million-password-list-top-1000.txt"
)

#Dessa forma não vai ficar baixando toda vez que eu executar pra chamar a lista
CACHE_LOCAL = "cache_senhas.json"

#tempo de validão (coloquei em horas pra ficar mais facil)
HORAS_CACHE = 12

#Funções
 
#Cache

def cache_valido():
    #Verifica se o cache local existe e ainda está dentro do prazo de validade configurado.
    
    #validação da localização do arquivo
    if not os.path.exists(CACHE_LOCAL):
        return False
    
    #r -> read(leitura)
    with open(CACHE_LOCAL, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    if "salvo_em" not in dados:
        return False
    
    #conversão do meu timestamp gravado para o objeto do datetime
    salvo_em = datetime.fromisoformat(dados["salvo_em"])
    
    prazo_valido = salvo_em + timedelta(hours=HORAS_CACHE)
    ainda_valido = datetime.now() < prazo_valido
    
    return ainda_valido

def salvar_cache(lista_senhas):
    # salva a lista de senhas em um arquivo JSON local, junto com o timestamp de quando foi baixada
    
    dados_cache = {
        "salvo_em": datetime.now().isoformat(),
        "total": len(lista_senhas),
        "senhas": lista_senhas
    }
    
    with open(CACHE_LOCAL, "w", encoding="utf-8") as f:
        json.dump(dados_cache, f, ensure_ascii=False, indent=2)
        
    print(f"[CACHE] {len(lista_senhas)} Senhas salvas em '{CACHE_LOCAL}'")
    
def carregar_cache():
    #aqui eu ja vou deixar para baixar o arquivo local
    
    with open(CACHE_LOCAL, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    print(f"[CACHE] {dados['total']} senhas carregada no cache local")
    return dados["senhas"]

#busca as senhas

def buscar_senhas_comuns():
    #nessa função vai ficar a busca pela minha lista de senhas comuns
    
    if cache_valido():
        print("[INFO] Usando cache local(dentro do prazo de 12h)")
        return carregar_cache()
    
    print("[INFO] Baixando lista de senhas comuns...")
    print(f"[INFO] fonte: {URL_SENHAS}")
    
    try:
        #temporizador de 10 segundos
        resposta = requests.get(URL_SENHAS, timeout=10)
        
        #validador da requisição. 
        resposta.raise_for_status() 
        
        #Processa o conteúdo linha por linha
        #splitlines() divide pelo \n
        #strip() remove espaços e \r no Windows
        #ignora linhas vazias com o "if senha"
        lista_senhas = [
            linha.strip()
            for linha in resposta.text.splitlines()
            if linha.strip()
        ]
        
        print(f"[OK] {len(lista_senhas)} senhas carregadas com sucesso!!")
        
        #salva a minha lista por 12h
        salvar_cache(lista_senhas)
        return lista_senhas
    
    #except, se não der certo na primeira requisição ele continua o programa pra esse etapa
    
    except requests.exceptions.ConnectionError:
        print("[ERRO] sem conexão com a internet")
        
    except requests.exceptions.Timeout:
        print("[ERRO] A requisição demorou mais de 10 segundos")    
        
    except requests.exceptions.HTTPError as x:
        print(f"[ERRO] Resposta HTTP invalida: {x}")
        
    #se der um erro desses, mas tem cache vai usar ele (se tiver expirado tbm)
    if os.path.exists(CACHE_LOCAL):
        print("[AVISO] Usando cache expirado como fallback") #contingência, mas coloque assim pra ficar mais tecnico 
        return carregar_cache()
        
    #sem net e sem o cache tbm
    print("[AVISO] Retornando lista mínima de emergência")
    return[
        "123456", "password", "123456789", "12345678",
        "12345", "1234567", "1234567890", "qwerty",
        "abc123", "password1", "111111", "senha"
    ]    
    
#Validação da senha

def verificar_senha(senha, lista_senhas):
    #Verifica se a senha está na lista de senhas comuns, a comparação é feita em minúsculas para pegar
    
    return senha.lower() in [s.lower() for s in lista_senhas]

def analisador_senha(senha, lista):
    #Parte central do codigo, vai validar se esta dentro da lista e os criterios de uma senha forte
    #Retorna tbm o score
    
    lista = buscar_senhas_comuns()
    problemas = []
    score = 100
    
    #validação se é uma senha comum:
    if verificar_senha(senha, lista):
        problemas.append("CRÍTICO - Está na lista de senhas mais comuns do mundo!")
        score -= 80
        
    #Comprimento da senha
    if len(senha) <8:
        problemas.append(f"Muito curta ({len(senha)} chars) - Ideal seria 12+")
        score -= 10
    
    elif len(senha) <12:
        problemas.append(f"Comprimento razoavel ({len(senha)} chars) - Idela seria 12+")
        score -= 10
    
    #validação do tipo do caracter
    if not re.search(r"[^\w\s]",senha):
        problemas.append("Sem caracteres £$P&C!@!$")
        score -= 10

    if not re.search(r"[A-Z]",senha):
        problemas.append("Sem letras MAIÚSCULAS")
        score -= 10
        
    if not re.search(r"[a-z]",senha):
        problemas.append("Sem letras minusculas")
        score -= 10
    
    if not re.search(r"[0-9]",senha):
        problemas.append("Sem NUM3R02")
        score -= 10
        
    #limite do score
    score = max(0, min(100, score))
    
    #Classificação do nivel da senha
    if score >= 80:
        nivel="FORTE"
    
    elif score >= 50:
        nivel="MÉDIA"
        
    elif score >= 20:
        nivel = "FRACA"
    
    else:
        nivel = "MUITO FRAQUINHA"
        
    return {
        "Senha": senha,
        "Score": score,
        "Nivel": nivel,
        "Problemas": problemas,
        "Total lista": len(lista)
               
    }
        
#Exibição do resultado da senha informada

def exibir_resultado(resultado):
    
    print("")
    print("=" * 60)
    print("RESULTADO DA ANALISE".center(60))
    print("=" * 60)
    
    #Teste de barra de score(A ideia que quis colocar e para ter uma barra de progresso para ver se a senha é boa ou não)
    score = resultado["Score"]
    nivel = resultado["Nivel"]
    preenchimento = int(score / 5)
    vazio = 20 - preenchimento
    
    #Definição da barra de acordo com o nivel de progresso da senha
    if score >= 80:
        barra = "[" + "#" * preenchimento + "-" * vazio + "]"
    
    elif score >= 50:
        barra = "[" + "#" * preenchimento + "-" * vazio + "]"
    
    elif score >= 20:
        barra = "[" + "#" * preenchimento + "-" * vazio + "]"
    
    else:
        barra = "[" + "#" * preenchimento + "-" * vazio + "]"
        
    print(f"\n Score: {score}/100 {barra}")
    print(f"Nivel: {nivel}")
    print(f" Verificando contra {resultado['Total lista']} senhas comuns")
    print("")
    
    # Indicativo de problemas encontrados dentro da senha
    if resultado["Problemas"]:
        print("PROBLEMAS ENCONTRADOS:")
        print("-" * 60)
        
        for p in resultado["Problemas"]:
            print(f"  [!] {p}")
            
    else:
        print("[OK] Nenhum problema encontrado!")
        print(" Sua senha passou em todos os criterios.")

    print("")

    # Diagnostico sobre a senha informada
    print("  DICA:")
    print("-" * 60)
    
    if nivel == "FORTE":
        print(" Otima senha! Continue usando combinacoes")
        print(" de letras, numeros e simbolos assim.")
        
    elif nivel == "MEDIA":
        print(" Senha razoavel. Tente adicionar mais")
        print(" caracteres especiais e aumentar o tamanho.")
        
    elif nivel == "FRACA":
        print(" Senha fraca. Recomendamos trocar por uma")
        print(" com 12+ caracteres, maiusculas, numeros e")
        print(" simbolos como: !@#$%")
        
    else:
        print(" Senha muito fraca ou comprometida.")
        print(" Troque IMEDIATAMENTE por uma senha forte.")

    print("=" * 60)
    
 
def menu_principal():
    
    print("=" * 60)
    print("PASSWORD VALIDATOR".center(60))
    print("SecLists + Python".center(60))
    print("=" * 60)
    print("")

    # Baixa a lista UMA vez antes do loop, pra evitar de ficar aparecendo varias vezes que a lista foi baixada
    
    print("[INFO] Carregando lista de senhas comuns...")
    lista = buscar_senhas_comuns()

    print("")
    print("Digite uma senha para analisar.")
    print("Digite 'sair' para encerrar.")
    print("Digite 'limpar' para limpar a tela.")
    print("-" * 60)

    # Loop para não sair do programa ate que seja executado o "sair"
    while True:

        print("")

        
        senha = getpass.getpass("Digite sua senha para validação: ")


        # Encerra o programa
        if senha.lower() == "sair":
            print()
            print("  Encerrando o Password Validator.")
            print("  Mantenha suas senhas seguras!")
            print("=" * 50)
            break

        # Limpa a tela
        if senha.lower() == "limpar":
            os.system("cls" if os.name == "nt" else "clear")
            continue

        # Senha vazia — pede de novo
        if not senha.strip():
            print("  [AVISO] Voce não digitou nada. Tente novamente.")
            continue

        # ── Analisa a senha digitada ──
        resultado = analisador_senha(senha, lista)
        exibir_resultado(resultado)

        # Pergunta se quer testar outra
        print()
        continuar = input("  Testar outra senha? (s/n): ").strip().lower()

        if continuar != "s":
            print()
            print("  Encerrando o Password Validator.")
            print("  Mantenha suas senhas seguras!")
            print("=" * 50)
            break

#programa principal para executar o menu
if __name__ == "__main__":
    menu_principal()