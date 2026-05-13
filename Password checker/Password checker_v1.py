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
        
    print(f"[cache] {len(lista_senhas)} Senhas salvas em '{CACHE_LOCAL}'")
    
    