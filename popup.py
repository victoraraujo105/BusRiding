'''
    Define popups para operações inválidas.
'''

from tkinter import messagebox
import constantes as cte
import monitoradas

def popup_destino():
    texto='Destino em branco inválido.\nInsira algo.'
    messagebox.showwarning(title='Destino Inválido', message=texto)
    monitoradas.destino.set(monitoradas.texto_anterior)
    return True

def popup_data():
    texto='Insira horários seguindo o formato na entrada (HH:MM).'
    messagebox.showwarning(title='Data Inválida', message=texto)
    return True

def popup_vagas():
    texto=f'Total de assentos disponíveis deve ser inteiro par entre 2 e {2*cte.MAXIMO_NUMERO_DE_FILEIRAS}, inclusive ambos extremos.'
    messagebox.showwarning(title='Total de Vagas Inválido', message=texto)
    return True

def popup_inteira():
    texto='Valor da passagem inteira deve ser float entre R$ 3.00 e R$ 6.00, inclusive ambos extremos.'
    messagebox.showwarning(title='Passagem Inteira Inválida', message=texto)
    return True

# mapeamento entre chaves de erro (retornadas pelas funções "atualizar" de cada widget com campo de texto monitorado)
# e o popup relacionado a esse erro.
campos_invalidos = {
    'destino_invalido': popup_destino,
    'data_invalida': popup_data,
    'vagas_invalida': popup_vagas,
    'inteira_invalida': popup_inteira,
    None: lambda *_: False  # quando a função atualizar retorna None, não deve aparecer nenhum popup!
}
