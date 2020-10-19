'''
    Define variáveis que guardam dados persistentes (salvos após a finalização do programa e
    recuperados na inicialização).
'''

import constantes as cte
from persistence import retrieve_data, save_data
from sys import argv

# lemos um arquivo e recuperamos os dados salvos
path = cte.DATA_FILE_PATH if len(argv) == 1 or argv[1].strip() == '' else argv[1]
data = retrieve_data(path)
if data is None:
    # aqui, retrieve_data retornou None, o que significa que não havia dados salvos
    # vamos, então, inicializar todos os valores
    linhas_entradas = dict()    # chaves: ids linhas cadastradas, valores: dicts --> chaves: ids onibus q não partiram, valores: dicts --> chaves: assentos ocupados, valores: passagem (0: inteira, 1: meia, 2: gratuita)
    horarios_linhas = dict()    # chaves: horario de partida em minutos [0, 1439], valores: sets de linhas q partem nesse horario
    destinos = cte.DESTINOS_INICIAIS.copy() # destinos exibidos na caixinha de entrada
    reservas = set()   # ids das reservas na ordem em q foram efetuadas
    linhas_visiveis = set() # ids das linhas habilitadas (visíveis, que não foram removidas)
    onibus_invisiveis = set()   # ids dos ônibus removidos q ainda não partiram
    ordem_inicial_linhas = tuple()
    ordem_inicial_reservas = tuple()
    linhas_possiveis = {(destino, t) for destino in destinos for t in range(1440)}
    # Colocar em monitoradas após implementação da persistência
    # pois a cada execução do programa será preciso percorrer as linhas
    # deletando ônibus q partiram e acrescentando os que chegaram
else:
    print('Carregando dados persistentes...')
    # essa sintaxe permite declarar várias variáveis no escopo do módulo de maneira prática:
    # por exemplo:
    # se DATA é um objeto com propriedades A e B:
    # podemos fazer:
    # A = DATA.A
    # B = DATA.B
    # para definir os nomes A e B nesse módulo
    # mas uma maneira mais prática é utilizar a sintaxe de desestruturação:
    # (A, B) = DATA
    (linhas_entradas,
    horarios_linhas,
    destinos,
    reservas,
    linhas_visiveis,
    onibus_invisiveis,
    ordem_inicial_linhas,
    ordem_inicial_reservas,
    linhas_possiveis) = data

def persistir(app):
    '''
        Coletamos os dados da aplicação e salvamos em um arquivo.
    '''
    print('Salvando dados persistentes...')
    data = (linhas_entradas,
    horarios_linhas,
    destinos,
    reservas,
    linhas_visiveis,
    onibus_invisiveis,
    app.linhas.get_children(),
    app.reservas.get_children(),
    linhas_possiveis)
    save_data(data, cte.DATA_FILE_PATH)
    print('Dados persistentes salvos!')
    app.root.destroy()
