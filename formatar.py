'''
    Define funções de formatação
'''

import datetime as dt
import constantes as cte


def form_data(d):
    return d.strftime('%d/%m/%y')
    
def form_tempo(t):
    return t.strftime('%H:%M')

def form_campus(x):
    return x

def form_destino(x):
    return x.strip().title().replace('-', ' ').replace(',', ' ')

def separar_milhares(n):
    return f'{n:,}'.replace(',', '.')

def separar_milhares_decimal(n):
    return f'{n:,.2f}'.replace('.', 'v').replace(',', '.').replace('v', ',')

def separar_milhares_precisao(n):
    return f'{n:,}'.replace('.', 'v').replace(',', '.').replace('v', ',')

def form_cont_linhas(n):
    return cte.PLACEHOLDER_CONT_LINHAS % separar_milhares(n)

def form_cont_onibus(n):
    return cte.PLACEHOLDER_CONT_ONIBUS % separar_milhares(n)

def form_cont_reservas(n):
    return cte.PLACEHOLDER_CONT_RESERVAS % separar_milhares(n)