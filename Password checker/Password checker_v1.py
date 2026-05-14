import requests
import json
import hashlib
import os 
from datetime import datetime, timedelta

#URL da lista de senhas comuns(seclist)

URL_SENHAS = (
    "https://raw.githubusercontent.com/danielmiessler/"
    "SecLists/master/Passwords/Common-Credentials/"
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
        "salvo_em": datetime.now(). isoformat(),
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
    
    print(f"[CACHE] {dados["total"]} senhas carregada no cache local")
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


    