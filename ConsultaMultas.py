#%%
print('Importando as bibliotecas...')
import requests
from datetime import datetime
import pandas as pd

#%%
print('Declarando o conteúdo da requisição da API e seus argumentos...')

url = 'https://api.infosimples.com/api/v2/consultas/antt/sifama/lista-autos'
args = {
  "login_cnpj":        "cnpj",
  "login_senha":       "senha",
  "cnpj_representado": "cnpj",
  "tipo_multa":        "{tipo_multa}", # Alterado a partir das funções
  "pagina":            "1", # Sempre pega a primeira página no princípio
  "token":             "token",
  "timeout":           600
}
#%%
print('Declarando o array com os tipos de multas e o array vazio para armazenar os registros...')
tipo_multas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
todos_os_registros = []
 
#%%
#Função de busca de paginas
print('Criação da função para obter os registros das páginas de multas:')
def obter_registros(url, args, numero_paginas,todos_os_registros):
    # Percorrer as páginas
    for pagina in range(2, numero_paginas):
        #Copia os argumentos da chamada
        args = args.copy()
        #Atualiza o argumento "pagina" baseado no número sendo aplicado na função
        args['pagina'] = str(pagina)
        print(pagina)
       
        # Faz a chamada e armazena a resposta na variável "todos os registros"
        response = requests.post(url, args)
        response_json = response.json()
        response.close()
 
        # Verifica se a resposta da api foi 200, se sim, adiciona o registro na variável
        if response_json['code'] == 200:
            todos_os_registros += response_json['data']
        elif response_json['code'] in range(600, 799):
            print("Resultado sem sucesso. Leia para saber mais:")
            print("Código: {} ({})".format(response_json['code'], response_json['code_message']))
            print("; ".join(response_json['errors']))
            break
 
    return todos_os_registros
 
#%%
print('Chamando os registros da API....')
#OBS: Devido a um erro na API do ANTT, a página 2 não é retornada.

# Faz a chamada para a primeira página. Se houverem mais páginas, elas serão acrescentadas/concatenadas 
# a partir da chamada da função obter_registros.

for tipo_multa in tipo_multas:
    # Atualizar o argumento 'tipo_multa' no args a partir da posição no array "tipo_multas"
    args['tipo_multa'] = str(tipo_multa)
    print(f'Fazendo a chamada do tipo de multa {tipo_multa} e armazenando a resposta na variável "todos os registros"...')
    response = requests.post(url, args)
    response_json = response.json()
    response.close()
   
    print("Verificando o código da resposta da API...")
    # verifica se a resposta da api foi 200, se sim, adiciona o registro na variável
    if response_json['code'] == 200:
        todos_os_registros += response_json['data']
        print("teste3")
    elif response_json['code'] in range(600, 799):
        print("Resultado sem sucesso. Leia para saber mais:")
        print("Código: {} ({})".format(response_json['code'], response_json['code_message']))
        print("; ".join(response_json['errors']))
 
    # Supondo que response_json seja um dicionário contendo a resposta JSON
    print('Pegando o número total de páginas para o tipo de multa em questão...')
    numero_paginas = response_json.get("data", [{}])[0].get("total_paginas")
    print(f'Número de páginas para o tipo de multa {tipo_multa} é: {numero_paginas}')
    
    print('Chamada da função para obter os outros registros (se existentes)...')
    # Armazena os registros em uma variável
    # Usa como parâmetro o número de páginas presentes para o tipo de multa em questão e o array de "todos_os_registros" para incluir tudo lá.
    registros = obter_registros(url, args, numero_paginas,todos_os_registros)
 
 
# %%
print('Criando o DF para receber as informações das multas:')
df_multas = pd.DataFrame()

print('Função para "normalizar" os registros vindos da API:')
for registro in registros:
    # Verifica se a coluna 'infracoes' está presente no registro
    if 'infracoes' in registro:
        # Converter a lista de infracoes em um DataFrame auxiliar
        df_temp = pd.DataFrame(registro['infracoes'])
   
        # Adiciona colunas adicionais do registro
        for key, value in registro.items():
            if key != 'infracoes':
                df_temp[key] = value
   
        # Concatena com o DataFrame principal
        df_multas = pd.concat([df_multas, df_temp], ignore_index=True)
 
# Exibe o DataFrame resultante
print(df_multas)

print('Script finalizado.')
# %%