# Missão - 1
# Parametros da Missão:
# 1 - A ferramente deve receber(ou criar) uma senha e avaliar ela seguindo
# os requisitos de validação de senha: 
# 1.a - Comprimentos(minimo 8) (X)
# 1.b - maiúsculas (X)
# 1.c - minúsculas (X)
# 1.d - numeros (X)
# 1.e - especiais (X) 
# 1.f - padroes comuns. (X)
# 
# 2 - Ao final de todas essas validações é gerado um relatorio de pontuação da senha (0-100) (X)

 

import requests
import re
import getpass


#Baixar as senhas Comuns
senhas_comuns_url = (
"https://raw.githubusercontent.com/gsuberland/CommonPasswordsByPolicy/master/from-rockyou/pwlist_anm_len10.txt"
)
    
temp = requests.get(senhas_comuns_url)

with open ("senhas_comum.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write(temp.text)

#Validação se a senha entra dentro da lista de senhas comuns

def carrega_senha():
    with open("senhas_comum.txt", "r", encoding="utf=8") as arquivo:
        return set (linha.strip() for linha in arquivo)

senhas_comuns = carrega_senha()

def validador_senha(senha):
    pontuacao = 0
    relatorio = []

    #validação de caracteres
    if re.search('[a-z]', senha):
        pontuacao += 10
        print('Sua senha contem letras minusculas +10')

    if re.search('[A-Z]', senha):
        pontuacao += 10
        print('Sua senha contem letras MAIÚSCULAS +10')        

    if re.search('[0-9]', senha):
        pontuacao += 10
        print('Sua senha contem NUM3R02 +10')

    if re.search(r'[^\w\s]', senha):
        pontuacao += 20
        print('Sua senha contem caracteres £$P&C!@!$ +20')

    #Validação se a senha esta dentro da lista de comuns
    if senha in senhas_comuns:
        pontuacao -= 20
        print("Infelizmente sua senha é uma das mais comuns -20")
    
    if senha not in senhas_comuns:
        pontuacao += 20
        print("Parabéns sua senha é fora do comum +20")
    
        #Validação tamanho
    if len(senha) < 8:
        pontuacao -= 10
        #Senha fraca
        print('O tamanho da sua senha é muito pequena -10')

    elif len(senha) >= 8 and len(senha) < 12:
        pontuacao += 20
        #Senha Ok
        print('OK, seu senha tem um tamanho adequado +20')
    
    else:
        pontuacao += 30
        #Senha Ótima
        print('Ótimo, sua senha e bem extensa +30')
    
    print("")
    #Pontuação
    if pontuacao >=90:
        print("""Incrivel!! Sua senha foi bem parametrizada, nunca compartilhe ela com ninguem!
Seu score foi de {}%""".format(pontuacao))
    
    elif pontuacao >=60 and pontuacao <=80:
        print("""Ok, mas se eu fosse você tomaria mais cuidado onde acessa livremente
Seu score foi de {}%""".format(pontuacao))

    else:
        print("""CUIDADO! Sua senha é muito vulneravel 
Seu score foi de {}%""".format(pontuacao))

def auditor_senhas():
    print("="*50)
    print("Auditor de senhas".center(50))
    print("="*50)
    print("")

    senha = getpass.getpass("Digite a sua senha: ")
    
    print("")
    print("="*50)
    print("Relatorio".center(50))
    print("="*50)
    print("")

    validador_senha(senha)


auditor_senhas()

#Alteração feita pelo Github web

    


