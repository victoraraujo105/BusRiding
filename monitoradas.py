'''
    Define e exporta variáveis que indicam estados na sessão da aplicação, como informações
    sobre o que está escrito nos widgets no momento, ou informações globais.
    Essas informações não são persistíveis (são esquecidas ao fechar a aplicação).
    Note que tk.StringVar() é um objeto mutável associado a um widget.
    Alterar o objeto StringVar (por meio de StringVar.set, por exemplo) permite que modifiquemos
    os valores nos widgets. Similarmente, esses objetos nos permitem monitorar o atual valor escrito
    nos campos de texto dos widgets.
    Note que usamos StringVar até mesmo para valores numéricos (como o preço da inteira),
    porque nos permite controlar mais facilmente a sua formatação. Quando necessário para cálculos,
    convertemos apropriadamente para valores numéricos.
'''

import tkinter as tk
import ttk
import datetime as dt
import constantes as cte
import formatar as fm
import estado

# seguimos a convenção de que nomes começando com underline indicam que a variável é privada (a esse módulo)
# então isso representa (por convenção) que não estamos exportando essa variável
_agora = dt.datetime.today()

data_atual = _agora
tempo_exibido = _agora
tempo_formatado = tk.StringVar()  # texto do widget que contém o horário (para cadastro/edição de linhas)
# last_call é o horário da última ação realizada (utilizado para remover automaticamente o texto após 1 segundo,
# veja update_actions em control.py para mais informações)
last_call = dt.datetime.today()
vagas = tk.StringVar()  # texto do widget que contém quantidade de vagas
indice_vagas = cte.MAXIMO_NUMERO_DE_FILEIRAS - 1  # veja o módulo vagas.py para explicação
inteira = tk.StringVar()  # texto do widget que contém o preço da passagem inteira
indice_inteira = 60  # veja o módulo inteira.py para explicação
cur_action = tk.StringVar()  # texto do widget que contém o texto da atual ação (veja update_actions em control.py)
destino = tk.StringVar()  # atual destino selecionado no widget
# O texto do último destino selecionado. Utilizado quando o usuário digita um destino inválido
# e queremos alterar o valor do widget para o último texto válido.
texto_anterior = '' if len(estado.destinos) == 0 else estado.destinos[0]

# O histórico da aplicação é utilizado para responder aos eventos CTRL+Z e CTRL+SHIFT+Z
# cada item da lista é uma tupla (NOME_DA_AÇÃO, INDICES_DAS_LINHAS, ITENS)
historico_undo = []
historico_redo = []
previous_selection = set()
pressed = False
num_entradas = 0
ocupar_assentos = tk.IntVar(value=0)
indice_linhas_geradas = 49 
janela_reservas = None

onibus_visiveis = set()     # ids dos ônibus habilitados q ainda não partiram
arrecadado = dict()
ocupacao_media_semanal = dict() # linha: lista cujos índices representam dias da semana, 0 é domingo

tempo_formatado.set(fm.form_tempo(tempo_exibido))
vagas.set(str(2 * (indice_vagas + 1)))
inteira.set('%.2f' %(3 + indice_inteira*.01))
cur_action.set('')
destino.set(texto_anterior)
