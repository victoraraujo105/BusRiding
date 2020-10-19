'''
    Define funções para ler e salvar dados em um arquivo, utilizando pickle (que codifica/decodifica os
    objetos do python)
'''

import pickle as pkl


def retrieve_data(path):
    '''
        Retorna o objeto salvo no caminho especificado (path).
        Se o objeto não foi encontrado (ou em qualquer outro erro) retorna None.
    '''
    try:
        with open(path, 'rb') as f:
            return pkl.load(f)
    except:
        return


def save_data(data, path):
    '''
        Salva os dados (data) no caminho especificado (path).
    '''
    with open(path, 'wb') as f:
        pkl.dump(data, f)
