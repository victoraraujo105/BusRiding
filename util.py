'''
    Define diversas funções (altera a interface gráfica, seleciona/add/remove linhas, reserva viagens).
'''

import tkinter as tk
from tkinter import messagebox, ttk
import estado
import monitoradas
import gerar
from gerar import minutos_dia, gerar_id_linha, campos_linha_formatados, gerar_id_onibus, gerar_id_reserva, decodificar_id_reserva, campos_reserva_formatados
import control as ctrl
import constantes as cte
import formatar as fm
import date
import destino as dest
import vagas as vg
import inteira as it
import popup
import history as hst
import datetime as dt


def reinsert_linha(app, linha, visivel=True):
    '''
        Reinsere uma linha que havia sido removida (ou não inicializada).
    '''
    dados = estado.linhas_entradas[linha]
    app.linhas.insert(parent='',
                      index='end',
                      values=campos_linha_formatados(dados),
                      iid=linha)
    t = minutos_dia(dados.horario)
    data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
    minutos_atual = data_atual.hour*60 + data_atual.minute

    if t == minutos_atual:
        periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
    elif t < minutos_atual:
        periodo = range(1, cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
    else:
        periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)
    estado.linhas_entradas[linha] = cte.ESTRUTURA_LINHA(*dados[:-1], dict())
    onibus_invisiveis = set()
    if not visivel:
        app.linhas.detach(linha)
        onibus_invisiveis.update(estado.linhas_entradas[linha].onibus)
    for d in periodo:
        # para cada dia no período, vamos adicionar um ônibus nessa linha
        partida = (data_atual + dt.timedelta(d)
                   ).replace(hour=dados.horario.hour, minute=dados.horario.minute)
        onibus = gerar_id_onibus(linha, partida)
        assentos = dados.onibus.get(onibus, dict())
        app.linhas.insert(parent=linha, index='end', values=(
            '-', fm.form_data(partida), 2*int(dados.fileiras) - len(assentos), '-'), iid=onibus)
        estado.linhas_entradas[linha].onibus[onibus] = assentos
        if visivel and onibus in estado.onibus_invisiveis:
            app.linhas.detach(onibus)
            onibus_invisiveis.add(onibus)
        elif visivel:
            monitoradas.onibus_visiveis.add(onibus)
    return onibus_invisiveis


def povoar_treeviews(app):
    '''
        Inicializa a interface gráfica com os dados persistidos.
    '''
    onibus_invisiveis = set()
    for linha in estado.ordem_inicial_linhas:
        onibus_invisiveis.update(reinsert_linha(app, linha))
    estado.ordem_inicial_linhas = tuple()
    for linha in estado.linhas_entradas.keys() - estado.linhas_visiveis:
        onibus_invisiveis.update(reinsert_linha(app, linha, False))
    for reserva in estado.ordem_inicial_reservas:
        app.reservas.insert(parent='',
                            index=0,
                            values=campos_reserva_formatados(reserva),
                            iid=reserva)
    estado.onibus_invisiveis = onibus_invisiveis
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))
    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
    print('Dados persistentes carregados.')


def del_selecao(app):
    '''
        Responde à deleção dos itens selecionados, e chama a função adequada para cada tipo de item.
    '''
    try:
        aba_selecionada = app.abas.index(app.abas.select())
        if aba_selecionada == 0:
            # estamos na aba das linhas
            remover_selecao_del(app)
        elif aba_selecionada == 1:
            # estamos na aba das reservas
            devolver(app)
    except KeyError:
        pass


SORTING_KEYS = {'linhas': lambda id: [estado.linhas_entradas[id][0], estado.linhas_entradas[id][1].time(), *estado.linhas_entradas[id][2:4]],
                'reservas': decodificar_id_reserva,
                'arrecadado': lambda id: [estado.linhas_entradas[id][:2], monitoradas.arrecadado[id]],
                'ocupacao': lambda id: [estado.linhas_entradas[id][:2], *monitoradas.ocupacao_media_semanal[id]]}


def move_to_beginning(lista, i):
    # remove o último elemento e o insere no início da lista
    lista = list(lista)
    lista.insert(0, lista.pop(i))
    return lista


def treeview_sort_column(app, tv, col, rev):
    '''
        Ordena as linhas com base em uma coluna.
    '''
    entradas = tv.get_children()
    if len(entradas) == 0:
        return
    ctrl.update_action(app, 'sort')
    unsorted_entradas = entradas
    sorted_entradas = sorted(entradas, key=lambda i: move_to_beginning(
        SORTING_KEYS[tv.winfo_name()](i), col), reverse=rev)

    for i, item in enumerate(sorted_entradas):
        tv.move(item, '', i)

    ctrl.update_action(app, 'sort')
    historico_redo = monitoradas.historico_redo
    historico_undo = monitoradas.historico_undo
    historico_redo.clear()
    historico_undo.append(['sort', tv, unsorted_entradas])

    tv.heading(col,
               command=lambda coluna=col: treeview_sort_column(
                   app, tv, coluna, not rev))


def last_separator(event, treeview):
    x, y = event.x, event.y

    if treeview.identify_region(x, y) == 'separator':
        coluna = treeview.identify_column(x)

        # pegar num de colunas
        if coluna == f'#{len(treeview["columns"])}' or coluna == '#0':
            # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
            return 'break'


def remover_selecao(app, indices, itens):
    linhas = app.linhas
    # assim as linhas são acessadas primeiro, removendo possíveis ônibus filhos, já que o detach de uma linha desabilita junto os seus filhos (ônibus)
    cur_itens = sorted(linhas.selection())
    if cur_itens == []:
        try:
            cur_itens = [linhas.get_children()[0]]

        except IndexError:
            released(1)
            return indices, itens

    cur_indices = []
    for item in cur_itens.copy():
        if item in estado.linhas_visiveis:
            estado.linhas_visiveis.remove(item)
            onibus_filhos = estado.linhas_entradas[item].onibus.keys()
            monitoradas.onibus_visiveis -= onibus_filhos
            estado.onibus_invisiveis.update(onibus_filhos)
        elif item in monitoradas.onibus_visiveis:
            monitoradas.onibus_visiveis.remove(item)
            estado.onibus_invisiveis.add(item)
        else:
            # remove ônibus filhos caso sua linha haja sido selecionada
            cur_itens.remove(item)
            continue
        ctrl.update_action(app, 'rmv')
        cur_indices.append(linhas.index(item))
        linhas.detach(item)
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))

    indices.extend(cur_indices)
    itens.extend(cur_itens)

    return indices, itens


def released(event):
    monitoradas.pressed = False


def check_pressed_rmv(app, indices, itens):
    pressed = monitoradas.pressed

    if pressed:
        indices, itens = remover_selecao(app, indices, itens)

        app.root.after(20, lambda *_: check_pressed_rmv(app, indices, itens))
    else:
        if len(indices) > 0:
            historico_undo = monitoradas.historico_undo
            historico_redo = monitoradas.historico_redo
            historico_redo.clear()
            indices = indices[::-1]
            itens = itens[::-1]
            if len(historico_undo) == 0 or historico_undo[-1] != ['rmv', indices, itens]:
                ctrl.update_action(app, 'rmv')
                historico_redo.clear()
                historico_undo.append(['rmv', indices, itens])


def remover_linhas(app, event):
    monitoradas.pressed = True if event.num == 1 else False
    indices, itens = remover_selecao(app, [], [])
    app.root.after(200, lambda *_: check_pressed_rmv(app, indices, itens))


def remover_selecao_del(app):
    '''
        Remove as linhas selecionadas.
    '''
    linhas = app.linhas
    itens = sorted(linhas.selection())
    if itens == []:
        # nenhuma linha selecionada
        return
    indices = []
    for item in itens.copy():
        if item in estado.linhas_visiveis:
            estado.linhas_visiveis.remove(item)
            onibus_filhos = estado.linhas_entradas[item].onibus.keys()
            monitoradas.onibus_visiveis -= onibus_filhos
            estado.onibus_invisiveis.update(onibus_filhos)
        elif item in monitoradas.onibus_visiveis:
            monitoradas.onibus_visiveis.remove(item)
            estado.onibus_invisiveis.add(item)
        else:
            itens.remove(item)
            continue
        ctrl.update_action(app, 'rmv')
        indices.append(linhas.index(item))
        linhas.detach(item)

    # atualiza os contadores, já que removemos algumas linhas
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))

    if len(indices) > 0:
        historico_undo = monitoradas.historico_undo
        historico_redo = monitoradas.historico_redo
        indices = indices[::-1]
        itens = itens[::-1]
        if len(historico_undo) == 0 or historico_undo[-1] != ['rmv', indices, itens]:
            ctrl.update_action(app, 'rmv')
            historico_redo.clear()
            # adicionamos o evento da remoção no histórico, para permitir CTRL+Z
            historico_undo.append(['rmv', indices, itens])


widgets_indices = {0: 'linhas', 1: 'reservas'}  # abas


def select_all(app, evento):
    '''
        Seleciona todos os itens na aba atual.
    '''
    try:
        widget = getattr(
            app, widgets_indices[app.abas.index(app.abas.select())])
        widget.selection_add(widget.get_children())
    except KeyError:
        pass


def editar_linha(app):
    '''
        Edita informações sobre uma linha.
    '''
    selecao = app.linhas.selection()
    if len(selecao) != 1 or app.linhas.parent(selecao[0]) != '':
        texto = 'Selecione uma única linha.'
        messagebox.showwarning(title='Impossível Editar', message=texto)
        return
    [linha] = selecao
    dados_linha = estado.linhas_entradas[linha]
    # a condição a seguir é True sse existe algum ônibus com reservas na linha selecionada.
    if any(len(x) != 0 for x in dados_linha.onibus.values()):
        texto = 'Linha possui reservas.'
        messagebox.showwarning(title='Impossível Editar', message=texto)
        return

    campos = [dest.atualizar_destino(), date.update(
        app), vg.atualizar_vagas(), it.atualizar_inteira()]

    for campo in campos:
        if popup.campos_invalidos[campo]():
            return

    destino_alterada = monitoradas.destino.get()
    tempo_exibido = monitoradas.tempo_exibido
    vagas_alterada = monitoradas.vagas.get()
    inteira_alterada = monitoradas.inteira.get()
    linha_alterada = gerar_id_linha(destino_alterada, tempo_exibido)

    h = minutos_dia(estado.linhas_entradas[linha].horario)

    if linha_alterada in estado.linhas_entradas:
        if linha_alterada in estado.linhas_visiveis:
            if linha != linha_alterada:
                texto = 'Linha já existe.'
                messagebox.showwarning(
                    title='Impossível Editar', message=texto)
            elif dados_linha[2:4] != [int(vagas_alterada)//2, round(float(inteira_alterada)*100 - 300)]:
                dados_linha_alterada = estado.linhas_entradas[linha] = cte.ESTRUTURA_LINHA(
                    *dados_linha[:2], int(vagas_alterada)//2, round(float(inteira_alterada)*100 - 300), dados_linha[-1])
                app.linhas.item(
                    linha, values=campos_linha_formatados(dados_linha_alterada))

                app.linhas.selection_set(linha_alterada)
                monitoradas.historico_redo.clear()
                monitoradas.historico_undo.append(
                    ['change', dados_linha, dados_linha_alterada, False])
                app.contador_linhas['text'] = fm.form_cont_linhas(
                    len(estado.linhas_visiveis))
                app.contador_onibus['text'] = fm.form_cont_onibus(
                    len(monitoradas.onibus_visiveis))

        else:
            texto = 'Linha desabilitada, deseja reabilitá-la?'
            resposta = messagebox.askyesno(
                title='Impossível Editar', message=texto, default='no')
            if resposta:
                app.linhas.reattach(linha_alterada, '',
                                    app.linhas.index(linha))
                app.linhas.item(
                    linha_alterada, open=app.linhas.item(linha, 'open'))
                estado.linhas_visiveis.add(linha_alterada)
                onibus_filhos_visiveis = set(
                    app.linhas.get_children(linha_alterada))
                estado.onibus_invisiveis -= onibus_filhos_visiveis
                monitoradas.onibus_visiveis.update(onibus_filhos_visiveis)
                ctrl.update_action(app, 'Restaurar')
                estado.horarios_linhas[h].remove(linha)
                app.linhas.delete(linha)
                estado.linhas_visiveis.remove(linha)
                for onibus in estado.linhas_entradas[linha].onibus:
                    monitoradas.onibus_visiveis.discard(onibus)
                    estado.onibus_invisiveis.discard(onibus)

                monitoradas.historico_redo.clear()
                monitoradas.historico_undo.append(
                    ['change', estado.linhas_entradas[linha], estado.linhas_entradas[linha_alterada], True])
                estado.linhas_possiveis.add((dados_linha.destino.title(), h))
                del estado.linhas_entradas[linha]
                app.linhas.selection_set(linha_alterada)
                app.contador_linhas['text'] = fm.form_cont_linhas(
                    len(estado.linhas_visiveis))
                app.contador_onibus['text'] = fm.form_cont_onibus(
                    len(monitoradas.onibus_visiveis))
        return
    h_alt = tempo_exibido.hour*60 + tempo_exibido.minute
    estado.linhas_possiveis.remove((destino_alterada, h_alt))
    estado.linhas_possiveis.add((dados_linha.destino.title(), h))
    estado.horarios_linhas[h].remove(linha)
    estado.horarios_linhas[h_alt] = estado.horarios_linhas.get(
        h_alt, set()).union({linha_alterada})
    dest.add_destino(app)
    ctrl.update_action(app, 'change')
    indice = app.linhas.index(linha)
    app.linhas.insert(parent='',
                      index=indice,
                      values=(destino_alterada, fm.form_tempo(
                          tempo_exibido), vagas_alterada, inteira_alterada),
                      iid=linha_alterada,
                      open=app.linhas.item(linha, 'open'))
    app.linhas.delete(linha)
    estado.linhas_visiveis.remove(linha)
    estado.linhas_visiveis.add(linha_alterada)

    onibus_filhos = dict()

    data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
    for d in range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1):
        partida = (data_atual + dt.timedelta(d)
                   ).replace(hour=tempo_exibido.hour, minute=tempo_exibido.minute)
        if data_atual <= partida <= data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA):
            onibus = gerar_id_onibus(linha_alterada, partida)
            app.linhas.insert(parent=linha_alterada, index='end', values=(
                '-', fm.form_data(partida), vagas_alterada, '-'), iid=onibus)
            monitoradas.onibus_visiveis.add(onibus)
            onibus_filhos[onibus] = dict()

    estado.linhas_entradas[linha_alterada] = cte.ESTRUTURA_LINHA(destino_alterada, tempo_exibido, int(
        vagas_alterada)//2, round(float(inteira_alterada)*100 - 300), onibus_filhos)

    for onibus in estado.linhas_entradas[linha].onibus:
        monitoradas.onibus_visiveis.discard(onibus)
        estado.onibus_invisiveis.discard(onibus)

    monitoradas.historico_redo.clear()
    monitoradas.historico_undo.append(
        ['change', estado.linhas_entradas[linha], estado.linhas_entradas[linha_alterada], False])

    del estado.linhas_entradas[linha]
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))

    ctrl.update_action(app, 'change')
    app.linhas.selection_set(linha_alterada)


def adicionar_linha(app):
    '''
        Adiciona uma linha com base nos campos de texto.
    '''
    # lemos todos os campos de texto
    campos = [dest.atualizar_destino(), date.update(
        app), vg.atualizar_vagas(), it.atualizar_inteira()]

    for campo in campos:
        if popup.campos_invalidos[campo]():
            return
    # aqui, todos os campos de texto possuem valores válidos, então vamos criar a linha

    linhas = app.linhas
    destino = monitoradas.destino.get()
    tempo_exibido = monitoradas.tempo_exibido
    vagas = monitoradas.vagas.get()
    inteira = monitoradas.inteira.get()
    linha = gerar_id_linha(destino, tempo_exibido)
    # antes de inseri-la graficamente, temos que verificar se ela já existe
    if linha in estado.linhas_entradas:
        # Linha desabilitada. Deseja reabilitá-la?
        if linha not in estado.linhas_visiveis:
            texto = 'Linha desabilitada, deseja reabilitá-la?.'
            resposta = messagebox.askyesno(
                title='Linha existe', message=texto, default='yes')
            if resposta:
                app.linhas.reattach(linha, '', 0)
                estado.linhas_visiveis.add(linha)
                onibus_filhos_visiveis = set(app.linhas.get_children(linha))
                estado.onibus_invisiveis -= onibus_filhos_visiveis
                monitoradas.onibus_visiveis.update(onibus_filhos_visiveis)
                ctrl.update_action(app, 'Restaurar')

                monitoradas.historico_redo.clear()
                monitoradas.historico_undo.append(['show', [0], [linha]])
                app.linhas.selection_set(linha)
                app.contador_linhas['text'] = fm.form_cont_linhas(
                    len(estado.linhas_visiveis))
                app.contador_onibus['text'] = fm.form_cont_onibus(
                    len(monitoradas.onibus_visiveis))
                # nova ação: reabilitar
        else:
            app.linhas.see(linha)
            app.linhas.selection_set(linha)
        return
    h = minutos_dia(tempo_exibido)
    estado.linhas_possiveis.discard((destino, h))
    estado.horarios_linhas[h] = estado.horarios_linhas.get(
        h, set()).union({linha})

    dest.add_destino(app)
    ctrl.update_action(app, 'add')
    linhas.insert(parent='',
                  index=0,
                  values=(destino, fm.form_tempo(
                      tempo_exibido), vagas, inteira),
                  iid=linha)
    estado.linhas_visiveis.add(linha)
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))

    estado.linhas_entradas[linha] = cte.ESTRUTURA_LINHA(
        destino, tempo_exibido, int(vagas)//2, round(float(inteira)*100 - 300), dict())

    data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
    for d in range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1):
        partida = (data_atual + dt.timedelta(d)
                   ).replace(hour=tempo_exibido.hour, minute=tempo_exibido.minute)
        if data_atual <= partida <= data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA):
            onibus = gerar_id_onibus(linha, partida)
            linhas.insert(parent=linha, index='end', values=(
                '-', fm.form_data(partida), vagas, '-'), iid=onibus)
            monitoradas.onibus_visiveis.add(onibus)
            estado.linhas_entradas[linha].onibus[onibus] = dict()
            app.contador_onibus['text'] = fm.form_cont_onibus(
                len(monitoradas.onibus_visiveis))

    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))

    historico_undo = monitoradas.historico_undo
    historico_redo = monitoradas.historico_redo
    historico_redo.clear()
    historico_undo.append(['add', [[estado.linhas_entradas[linha], list()]]])
    linhas.selection_set(linha)


def reservar_viagem(app):
    '''
        Cria a interface gráfica para permitir a reserva de viagens.
    '''
    linhas = app.linhas
    selecao = linhas.selection()
    if len(selecao) != 1 or linhas.parent(selecao[0]) == '':
        messagebox.showwarning(title='Reserva Impossível',
                               message='Selecione uma único ônibus.')
        return

    [onibus] = selecao
    linha = onibus[:-7]

    num_fileiras, indice_inteira = estado.linhas_entradas[linha][2:4]

    def coordenadas_assento(
        a): return gerar.coordenadas_assento(a, num_fileiras)
    def assento_coordenadas(
        i, j): return gerar.assento_coordenadas(i, j, num_fileiras)

    if len(estado.linhas_entradas[linha].onibus[onibus]) == 0:
        assentos_visiveis = set(range(1, 4*num_fileiras + 1))

    else:
        assento_qualquer = next(
            assento for assento in estado.linhas_entradas[linha].onibus[onibus])
        shift = sum(coordenadas_assento(assento_qualquer)) % 2
        assentos_visiveis = {assento_coordenadas(
            i, 2 * j + (i + shift) % 2) for j in range(2) for i in range(num_fileiras)}

    # essa é a nova janela
    monitoradas.janela_reservas = tk.Toplevel(name=onibus)
    monitoradas.janela_reservas.grab_set()
    monitoradas.janela_reservas.title('Reservar Assento')
    monitoradas.janela_reservas.resizable(False, False)
    monitoradas.janela_reservas.minsize(0, 0)
    monitoradas.janela_reservas.transient(app.root)

    frame = ttk.Frame(monitoradas.janela_reservas)
    painel_assentos = ttk.Frame(frame)
    labels = dict()

    selected = ttk.Label(painel_assentos, text='None')

    def selecionar(event):
        label = event.widget
        nonlocal selected

        if selected != label:
            if selected['text'] == 'None':
                selected.destroy()
            else:
                selected.configure(style='available.TLabel')
            label.configure(style='selected.TLabel')
            selected = label
            if passagem.get() in range(3):
                botao_finalizar.state(['!disabled'])
        else:
            label.configure(style='available.TLabel')
            selected = ttk.Label(painel_assentos, text='None')
            botao_finalizar.state(['disabled'])

    estilo = {2: 'inteira.TLabel', 1: 'meia.TLabel', 0: 'gratuita.TLabel'}

    for assento in assentos_visiveis:
        labels[assento] = ttk.Label(painel_assentos,
                                    text=assento,
                                    anchor='center',
                                    takefocus=True,
                                    width=4)
        disponivel = assento not in estado.linhas_entradas[linha].onibus[onibus]
        if disponivel:
            labels[assento].bind('<Button-1>', selecionar)
        else:
            seat = estado.linhas_entradas[linha].onibus[onibus][assento]
        labels[assento]['cursor'] = 'hand2' if disponivel else 'X_cursor'
        labels[assento]['style'] = 'available.TLabel' if disponivel else estilo[seat]
        i, j = coordenadas_assento(assento)
        labels[assento].grid(row=i,
                             column=j,
                             padx=(0, 10) if j == 1 else
                             (10, 0) if j == 2 else 0)
        painel_assentos.rowconfigure(i, weight=1)

    painel_passagens = ttk.Frame(frame)
    highlight_colours = {'inteira.TLabel': '#ff2e2e',
                         'meia.TLabel': '#ff9838', 'gratuita.TLabel': '#1f90e0'}

    for tipo_passagem in ('inteira', 'meia', 'gratuita'):
        estilo_botao = tipo_passagem+'.TRadiobutton'
        estilo_label = tipo_passagem+'.TLabel'

        app.estilo.configure(estilo_botao,
                             width=15,
                             anchor='w',
                             justify='w',
                             background=app.estilo.lookup(
                                 estilo_label, 'background'),
                             foreground='#fff')

        cor_fundo = app.estilo.lookup(tipo_passagem+'.TLabel', 'background')
        cor_fundo_ativo = highlight_colours[estilo_label]
        app.estilo.map(estilo_botao, background=[
                       ('!active', cor_fundo), ('active', cor_fundo_ativo)])

    passagem = tk.IntVar()
    passagem.set(-1)

    def button_state():
        if selected['text'] == 'None':
            botao_finalizar.state(['disabled'])
            return
        botao_finalizar.state(['!disabled'])

    assentos_livres = ttk.Label(
        painel_passagens, text='Assentos Livres', anchor='center', style='available.TLabel')
    assentos_livres.grid(row=0, column=0, sticky='nsew')

    passagem_inteira = ttk.Radiobutton(
        painel_passagens,
        text=f'Inteira: R$ {it.inteira_termo(indice_inteira, 2)}',
        variable=passagem,
        value=2,
        style='inteira.TRadiobutton',
        command=button_state)
    passagem_inteira.grid(row=1, column=0, sticky='nsew')

    passagem_meia = ttk.Radiobutton(
        painel_passagens,
        text=f'Meia: R$ {it.inteira_termo(indice_inteira, 1)}',
        variable=passagem,
        value=1,
        style='meia.TRadiobutton',
        command=button_state)
    passagem_meia.grid(row=2, column=0, sticky='nsew')

    passagem_gratuita = ttk.Radiobutton(painel_passagens,
                                        text=f'Gratuita: R$ 0.00',
                                        variable=passagem,
                                        value=0,
                                        style='gratuita.TRadiobutton',
                                        command=button_state)
    passagem_gratuita.grid(row=3, column=0, sticky='nsew')

    for i in range(4):
        frame.rowconfigure(i, weight=1)

    def finalizar():
        '''
            Realiza a reserva. Chamado quando o usuário clica no botão Reservar.
        '''
        nonlocal selected
        assento = int(selected['text'])
        if len(estado.linhas_entradas[linha].onibus[onibus]) == 0:
            shift = (sum(coordenadas_assento(assento)) + 1) % 2
            assentos_invisiveis = {assento_coordenadas(
                i, 2 * j + (i + shift) % 2) for j in range(2) for i in range(num_fileiras)}
            for assento_indisponivel in assentos_invisiveis:
                labels[assento_indisponivel].grid_remove()
        tipo = passagem.get()
        estado.linhas_entradas[linha].onibus[onibus][assento] = tipo
        reserva = gerar_id_reserva(onibus, assento, tipo)
        estado.reservas.add(reserva)
        # insere essa reserva na aba de reservas
        app.reservas.insert(parent='',
                            index=0,
                            values=campos_reserva_formatados(reserva),
                            iid=reserva)
        prev_values = linhas.set(onibus)
        prev_values['assentos livres'] = int(
            prev_values['assentos livres']) - 1
        linhas.item(onibus, values=tuple(prev_values.values()))
        labels[assento]['cursor'] = 'X_cursor'
        labels[assento]['style'] = estilo[tipo]
        labels[assento].unbind('<Button-1>')
        selected = ttk.Label(painel_assentos, text='None')

        historico_undo = monitoradas.historico_undo
        historico_redo = monitoradas.historico_redo
        historico_redo.clear()
        historico_undo.append(['book', reserva])
        button_state()
        app.contador_reservas['text'] = fm.form_cont_reservas(
            len(estado.reservas))
        ctrl.update_action(app, 'book')

    def undo_reserva(event):
        historico_undo = monitoradas.historico_undo
        historico_redo = monitoradas.historico_redo
        try:
            evento = chave, *dados = historico_undo.pop(-1)
            historico_redo.append(evento)
            actions = hst.desfazer[chave](app, *dados)
            try:
                close = dados[0][:-6] != onibus
            except (IndexError, TypeError):
                close = True
            if not close:
                info_reserva = decodificar_id_reserva(dados[0])
                assento = info_reserva.assento
                nonlocal selected
                if selected['text'] != 'None':
                    selected['style'] = 'available.TLabel'
                labels[assento]['style'] = 'selected.TLabel'
                labels[assento]['cursor'] = 'hand2'
                labels[assento].bind('<Button-1>', selecionar)
                selected = labels[assento]
                button_state()
                if len(estado.linhas_entradas[linha].onibus[onibus]) == 0:
                    shift = (sum(coordenadas_assento(assento)) + 1) % 2
                    assentos_invisiveis = {assento_coordenadas(
                        i, 2 * j + (i + shift) % 2) for j in range(2) for i in range(num_fileiras)}
                    for assento_indisponivel in assentos_invisiveis:
                        labels[assento_indisponivel] = labels.get(assento_indisponivel, ttk.Label(painel_assentos,
                                                                                                  text=assento_indisponivel,
                                                                                                  anchor='center',
                                                                                                  takefocus=True,
                                                                                                  width=4,
                                                                                                  style='available.TLabel',
                                                                                                  cursor='hand2'))
                        i, j = coordenadas_assento(assento_indisponivel)
                        labels[assento_indisponivel].grid(row=i,
                                                          column=j,
                                                          padx=(0, 10) if j == 1 else
                                                          (10, 0) if j == 2 else 0)
                        painel_assentos.rowconfigure(i, weight=1)

            if actions == 0:
                hst.undo(app)
            else:
                ctrl.update_action(
                    app, cte.ACOES_COMPLEMENTARES.get(chave, chave))
        except IndexError:
            close = False
        if close:
            monitoradas.janela_reservas.destroy()

    def redo_reserva(event):
        historico_undo = monitoradas.historico_undo
        historico_redo = monitoradas.historico_redo
        try:
            evento = chave, *dados = historico_redo.pop(-1)
            historico_undo.append(evento)
            actions = hst.refazer[chave](app, *dados)
            try:
                close = dados[0][:-6] != onibus
            except (IndexError, TypeError):
                close = True
            if not close:
                info_reserva = decodificar_id_reserva(dados[0])
                assento, tipo = info_reserva.assento, info_reserva.passagem.tipo
                labels[assento]['cursor'] = 'X_cursor'
                labels[assento]['style'] = estilo[tipo]
                labels[assento].unbind('<Button-1>')
                nonlocal selected
                selected = ttk.Label(painel_assentos, text='None')
                button_state()
                if len(estado.linhas_entradas[linha].onibus[onibus]) == 1:
                    shift = (sum(coordenadas_assento(assento)) + 1) % 2
                    assentos_invisiveis = {assento_coordenadas(
                        i, 2 * j + (i + shift) % 2) for j in range(2) for i in range(num_fileiras)}
                    for assento_indisponivel in assentos_invisiveis:
                        labels[assento_indisponivel].grid_remove()

            if actions == 0:
                hst.redo(app)
            else:
                ctrl.update_action(app, chave)
        except IndexError:
            close = False
        if close:
            monitoradas.janela_reservas.destroy()

    monitoradas.janela_reservas.bind('<Control-z>', undo_reserva)
    monitoradas.janela_reservas.bind(
        '<Control-Shift-KeyPress-Z>', redo_reserva)

    botao_finalizar = ttk.Button(painel_passagens,
                                 text='Reservar',
                                 command=finalizar,
                                 state='disabled')
    botao_finalizar.grid(row=4, column=0, pady=(10, 0))

    painel_assentos.pack(side='left')
    painel_passagens.pack(side='right', padx=15)

    frame.pack(anchor='center', expand=True)


def devolver(app):
    '''
        Remove as reservas selecionadas, devolvendo as vagas.
    '''
    selecao = app.reservas.selection()
    if len(selecao) == 0:
        texto = 'Selecione reservas cujos ônibus ainda não partiram.'
        messagebox.showwarning(title='Não Há O Que Devolver', message=texto)
        return

    devolviveis = [
        reserva for reserva in selecao if app.linhas.exists(reserva[:-6])]
    if len(devolviveis) < len(selecao):
        if len(devolviveis) == 0:
            texto = 'Ônibus já partiram. Impossível devolver.'
            messagebox.showwarning(title='Impossível Devolver', message=texto)
            return
        else:
            texto = 'Os ônibus de algumas reservas já partiram, deseja devolver as demais?'
            resposta = messagebox.askyesno(
                title='ônibus Partiram', message=texto, default='yes')
            if not resposta:
                return
    reservas = []
    app.linhas.selection_set(*[])
    for reserva in devolviveis:
        reservas.insert(0, [app.reservas.index(reserva), reserva])
        estado.reservas.discard(reserva)
        app.reservas.delete(reserva)

        onibus = reserva[:-6]
        linha = onibus[:-7]

        del estado.linhas_entradas[linha].onibus[onibus][decodificar_id_reserva(
            reserva).assento]

        prev_values = app.linhas.set(onibus)
        prev_values['assentos livres'] = int(
            prev_values['assentos livres']) + 1
        app.linhas.see(onibus)
        app.linhas.selection_add(onibus)
        app.linhas.item(onibus, values=tuple(prev_values.values()))

    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
    monitoradas.historico_redo.clear()
    monitoradas.historico_undo.append(['refund', reservas])
