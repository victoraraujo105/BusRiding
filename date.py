'''
    Define o comportamento do widget que contém o texto do horário para cadastro/edição de novas linhas.
'''

import monitoradas
from gerar import gerar_id_onibus
from control import update_action
import datetime as dt
import formatar as fm
import constantes as cte
import mount
import estado
import tkinter as tk

def increment(app, interval):
    '''
        Aumenta o horário em *interval*. Executa quando o usuário clica na seta para cima do spinbox.
        Aumentar o maior horário 23:59 sempre irá atualizar o horário para 00:00.
    '''
    update(app)
    monitoradas.tempo_exibido += interval
    if monitoradas.tempo_exibido - monitoradas.data_atual >= dt.timedelta(1):
        monitoradas.tempo_exibido -= dt.timedelta(1)
    monitoradas.tempo_formatado.set(fm.form_tempo(monitoradas.tempo_exibido))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'


def decrement(app, interval):
    '''
        Decrementa o horário em *interval*. Executa quando o usuário clica na seta para baixo do spinbox.
        Decrementar o menor horário 00:00 sempre irá atualizar o horário para 23:59.
    '''
    update(app)
    monitoradas.tempo_exibido -= interval
    if monitoradas.data_atual > monitoradas.tempo_exibido:
        monitoradas.tempo_exibido += dt.timedelta(1)
    monitoradas.tempo_formatado.set(fm.form_tempo(monitoradas.tempo_exibido))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'

def update(app):
    '''
        Valida o valor escrito pelo usuário no texto do horário.
        - Se o horário é inválido, retorna a string "data_invalida" para indicar invalidez.
        - Caso contrário, interpreta o horário digitado como datetime e o reescreve no widget, de
        modo a deixar padronizado a formatação do horário (por exemplo, se o usuário digita "   15:13",
        o texto do widget será atualizado para "15:13").
    '''
    chave = None
    spin_hora = app.spin_hora
    try:
        tempo_bruto = spin_hora.get().strip()
        tempo = dt.datetime.strptime(tempo_bruto, '%H:%M')
        monitoradas.tempo_exibido = monitoradas.data_atual.replace(hour=tempo.hour, minute=tempo.minute)
        if monitoradas.data_atual > monitoradas.tempo_exibido:
            monitoradas.tempo_exibido += dt.timedelta(1)
    except ValueError:
        chave = 'data_invalida'
    monitoradas.tempo_formatado.set(fm.form_tempo(monitoradas.tempo_exibido))
    return chave

def atualizar_relogio(app):
    '''
        Atualiza o relógio da aplicação, removendo ônibus que já partiram e adicionando
        ônibus na data máxima para se reservar assentos.
    '''
    print('ATUALIZAR RELOGIO')

    data_previa = monitoradas.data_atual
    data_atual = dt.datetime.today().replace(second=0, microsecond=0)
    monitoradas.data_atual = data_atual

    linhas = app.linhas
    
    # horarios_linhas nos dá um conjunto (set) de ids de linhas no horário especificado como chave
    for linha in estado.horarios_linhas.get(data_previa.hour*60 + data_previa.minute, []):
        # baseado no id da linha e na data anterior (que expirou)
        # achamos, para cada linha, o id do ônibus que partiu, e removemos
        onibus = gerar_id_onibus(linha, data_previa)
        if onibus in monitoradas.onibus_visiveis:
            if isinstance(monitoradas.janela_reservas, tk.Toplevel) and monitoradas.janela_reservas.winfo_exists():
                if monitoradas.janela_reservas.winfo_name() == onibus:
                    monitoradas.janela_reservas.destroy()
            monitoradas.onibus_visiveis.remove(onibus)
            update_action(app, 'Partida')  # sinalizamos a ação
        else:
            estado.onibus_invisiveis.discard(onibus)
        linhas.delete(onibus) # removemos o ônibus
        # modificar estado para que a remoção seja persistente
        del estado.linhas_entradas[linha].onibus[onibus]
    data_maxima = data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)
    for linha in estado.horarios_linhas.get(data_maxima.hour*60 + data_maxima.minute, []):
        # vamos adicionar 1 ônibus para cada linha no horário atualizado,
        # que partirá daqui a 15 dias (intervalo maximo para reserva)
        onibus = gerar_id_onibus(linha, data_maxima)
        vagas = 2*estado.linhas_entradas[linha].fileiras
        estado.linhas_entradas[linha].onibus[onibus] = dict()
        linhas.insert(parent=linha, index='end', values=('-', fm.form_data(data_maxima), vagas, '-'), iid=onibus)

        if linha in estado.linhas_visiveis:
            monitoradas.onibus_visiveis.add(onibus)
            update_action(app, 'Chegada')
    
    app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))

    if data_atual > monitoradas.tempo_exibido:
        monitoradas.tempo_exibido += dt.timedelta(1)

    # vamos atualizar o relógio novamente daqui a 1 minuto
    app.root.after(60_000, lambda: atualizar_relogio(app))