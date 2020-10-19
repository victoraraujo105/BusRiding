'''
    Define funções que respondem a CTRL+Z e CTRL+SHIFT+Z (undo e redo, respectivamente).
'''

import mount
import estado
import monitoradas
import datetime as dt
import formatar as fm
import control as ctrl
import constantes as cte
from gerar import minutos_dia, gerar_id_linha, campos_linha_formatados, gerar_id_onibus, decodificar_id_onibus, gerar_id_reserva, decodificar_id_reserva, campos_reserva_formatados

def reattach_linhas(app, indices, itens):
    '''
        Readiciona as linhas (itens) nos indices indicados.
    '''
    actions = 0

    for i, item in zip(indices, itens):
        if item in estado.linhas_entradas and item not in estado.linhas_visiveis:    # linhas são entidades dinâmicas, precisa checar se ônibus removidos não expiraram e inserir novos ônibus
            app.linhas.reattach(item, '', i)
            estado.linhas_visiveis.add(item)
            app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
            onibus_filhos_visiveis = set(app.linhas.get_children(item))
            estado.onibus_invisiveis -= onibus_filhos_visiveis
            monitoradas.onibus_visiveis.update(onibus_filhos_visiveis)
            app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))

        elif item in estado.onibus_invisiveis:  # inserir apenas se estiver no intervalo válido
            estado.onibus_invisiveis.remove(item)
            monitoradas.onibus_visiveis.add(item)
            app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
            app.linhas.reattach(item, item[:-7], i)
            app.linhas.see(item)
        else:
            continue
        actions += 1
    
    if actions > 0:
        app.abas.select(app.aba_linhas)
        app.linhas.selection_set(itens)
    return actions


def detach_linhas(app, indices, itens):
    actions = 0

    for item in itens:
        if item in estado.linhas_visiveis:
            estado.linhas_visiveis.remove(item)
            app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
            onibus_filhos_visiveis = set(app.linhas.get_children(item))
            monitoradas.onibus_visiveis -= onibus_filhos_visiveis
            estado.onibus_invisiveis.update(onibus_filhos_visiveis)
            app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
        elif item in monitoradas.onibus_visiveis:
            monitoradas.onibus_visiveis.remove(item)
            estado.onibus_invisiveis.add(item)
            app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
        else:
            continue
        app.linhas.detach(item)
        actions += 1
    
    if actions > 0:
        app.abas.select(app.aba_linhas)
    
    return actions


def descadastrar_linhas(app, dados):
    actions = 0
    reservas_changed = False

    for dados_linha, reservas in dados:
        linha = gerar_id_linha(*dados_linha[:2])
        for reserva in reservas:
            estado.reservas.discard(reserva)
            app.reservas.delete(reserva)
            reservas_changed = True
                    
        app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))

        t = minutos_dia(dados_linha.horario)

        del estado.linhas_entradas[linha]
        estado.linhas_possiveis.add((dados_linha.destino.title(), t))
        estado.horarios_linhas[t].remove(linha)
        estado.linhas_visiveis.remove(linha)
        app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
        onibus_filhos = dados_linha.onibus.keys()
        monitoradas.onibus_visiveis -= onibus_filhos
        estado.onibus_invisiveis -= onibus_filhos
        app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
        app.linhas.delete(linha)

        actions += 1
    
    if not reservas_changed:
        app.abas.select(app.aba_linhas)    

    return actions


def recadastrar_linhas(app, dados):
    actions = 0
    reservas_changed = False

    app.linhas.selection_set(*[])
    app.reservas.selection_set(*[])

    for dados_linha, reservas in dados:
        linha = gerar_id_linha(*dados_linha[:2])

        estado.linhas_entradas[linha] = cte.ESTRUTURA_LINHA(*dados_linha[:-1], dict())

        for reserva in reservas:
            estado.reservas.add(reserva)
            app.reservas.insert(parent='',
                                index=0,
                                values=campos_reserva_formatados(reserva),
                                iid=reserva)
            reservas_changed = True

        app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
        
        t = minutos_dia(dados_linha.horario)
        estado.linhas_possiveis.remove((dados_linha.destino.title(), t))

        estado.horarios_linhas[t] = estado.horarios_linhas.get(t, set()).union({linha})
        estado.linhas_visiveis.add(linha)
        app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))

        app.linhas.insert(parent='',
                        index=0,
                        values=campos_linha_formatados(dados_linha),
                        iid=linha)

        data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
        minutos_atual = data_atual.hour*60 + data_atual.minute
    
        if t == minutos_atual:
            periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
        elif t < minutos_atual:
            periodo = range(1, cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
        else:
            periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)

        for d in periodo: 
            partida = (data_atual + dt.timedelta(d)).replace(hour=dados_linha.horario.hour, minute=dados_linha.horario.minute)
            onibus = gerar_id_onibus(linha, partida)
            assentos = dados_linha.onibus.get(onibus, dict())
            app.linhas.insert(parent=linha, index='end', values=('-', fm.form_data(partida), 2*int(dados_linha.fileiras) - len(assentos), '-'), iid=onibus)
            monitoradas.onibus_visiveis.add(onibus)
            app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
            estado.linhas_entradas[linha].onibus[onibus] = assentos

        app.linhas.selection_add(linha)
        app.reservas.selection_add(*reservas)

        actions += 1

    if not reservas_changed:
        app.abas.select(app.aba_linhas)

    return actions


def desort(app, treeview, entradas):
    actions = 0
    app.abas.select(treeview.master)
    monitoradas.historico_redo[-1] = ['sort', treeview, treeview.get_children()]
    for i, entrada in enumerate(entradas):
        treeview.reattach(entrada, '', i)
        actions += 1
    return actions


def resort(app, treeview, entradas):
    actions = 0
    app.abas.select(treeview.master)
    monitoradas.historico_undo[-1] = ['sort', treeview, treeview.get_children()]
    for i, entrada in enumerate(entradas):
        treeview.reattach(entrada, '', i)
        actions += 1
    return actions


def restaurar(app, dados_anterior, dados_alterada, existia):
    app.abas.select(app.aba_linhas)
    linha_anterior = gerar_id_linha(*dados_anterior[:2])
    linha_alterada = gerar_id_linha(*dados_alterada[:2])
    indice = app.linhas.index(linha_alterada)
    expanded = app.linhas.item(linha_alterada, 'open')
    
    if linha_alterada == linha_anterior:
        app.linhas.item(linha_alterada, values=campos_linha_formatados(dados_anterior))
        app.linhas.selection_set(linha_anterior)
        app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
        app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
        return 1
    if existia:
        estado.linhas_visiveis.remove(linha_alterada)
        onibus_filhos_visiveis = set(app.linhas.get_children(linha_alterada))
        monitoradas.onibus_visiveis -= onibus_filhos_visiveis
        estado.onibus_invisiveis.update(onibus_filhos_visiveis)
        app.linhas.detach(linha_alterada)
    else:
        t = minutos_dia(dados_alterada.horario)

        estado.horarios_linhas[t].remove(linha_alterada)
        estado.linhas_visiveis.remove(linha_alterada)
        onibus_filhos = dados_alterada.onibus.keys()
        monitoradas.onibus_visiveis -= onibus_filhos
        estado.onibus_invisiveis -= onibus_filhos
        del estado.linhas_entradas[linha_alterada]
        estado.linhas_possiveis.add((dados_alterada.destino.title(), t))

        app.linhas.delete(linha_alterada)
    t_ant = minutos_dia(dados_anterior.horario)
    assentos = dados_anterior.fileiras*2
    estado.horarios_linhas[t_ant] = estado.horarios_linhas.get(t_ant, set()).union({linha_anterior})
    app.linhas.insert(parent='',
                    index=indice,
                    values=campos_linha_formatados(dados_anterior),
                    iid=linha_anterior,
                    open=expanded)
    estado.linhas_visiveis.add(linha_anterior)
    estado.linhas_possiveis.remove((dados_anterior.destino.title(), t_ant))

    estado.linhas_entradas[linha_anterior] = cte.ESTRUTURA_LINHA(*dados_anterior[:-1], dict())

    data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
    for d in range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1):
        partida = (data_atual + dt.timedelta(d)).replace(hour=dados_anterior.horario.hour, minute=dados_anterior.horario.minute)
        if data_atual <= partida <= data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA):
            onibus = gerar_id_onibus(linha_anterior, partida)
            app.linhas.insert(parent=linha_anterior, index='end', values=('-', fm.form_data(partida), assentos, '-'), iid=onibus)
            monitoradas.onibus_visiveis.add(onibus)
            estado.linhas_entradas[linha_anterior].onibus[onibus] = dict()
    

    app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
    app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
    app.linhas.selection_set(linha_anterior)
    
    return 1


def mudar(app, dados_anterior, dados_alterada, existia):
    app.abas.select(app.aba_linhas)
    linha_anterior = gerar_id_linha(*dados_anterior[:2])
    linha_alterada = gerar_id_linha(*dados_alterada[:2])
    if linha_anterior == linha_alterada:
        app.linhas.item(linha_anterior, values=campos_linha_formatados(dados_alterada))
        app.linhas.selection_set(linha_alterada)
        app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
        app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
        return 1
    indice = app.linhas.index(linha_anterior)
    expanded = app.linhas.item(linha_anterior, 'open')
    t = minutos_dia(dados_anterior.horario)
    estado.horarios_linhas[t].remove(linha_anterior)
    estado.linhas_visiveis.remove(linha_anterior)
    onibus_filhos = dados_anterior.onibus.keys()
    monitoradas.onibus_visiveis -= onibus_filhos
    estado.onibus_invisiveis -= onibus_filhos
    del estado.linhas_entradas[linha_anterior]
    app.linhas.delete(linha_anterior)
    estado.linhas_possiveis.add((dados_anterior.destino.title(), t))
    
    if existia:
        app.linhas.reattach(linha_alterada, '', indice)
        app.linhas.item(linha_alterada, open=expanded)
        estado.linhas_visiveis.add(linha_alterada)
        onibus_filhos_visiveis = set(app.linhas.get_children(linha_alterada))
        estado.onibus_invisiveis -= onibus_filhos_visiveis
        monitoradas.onibus_visiveis.update(onibus_filhos_visiveis)
    else:
        t = minutos_dia(dados_alterada.horario)
        assentos = dados_alterada.fileiras*2
        estado.horarios_linhas[t] = estado.horarios_linhas.get(t, set()).union({linha_alterada})
        app.linhas.insert(parent='',
                        index=indice,
                        values=campos_linha_formatados(dados_alterada),
                        iid=linha_alterada,
                        open=expanded)
        estado.linhas_visiveis.add(linha_alterada)
        estado.linhas_possiveis.remove((dados_alterada.destino.title(), t))

        estado.linhas_entradas[linha_alterada] = cte.ESTRUTURA_LINHA(*dados_alterada[:-1], dict())

        data_atual = monitoradas.data_atual.replace(second=0, microsecond=0)
        for d in range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1):
            partida = (data_atual + dt.timedelta(d)).replace(hour=dados_alterada.horario.hour, minute=dados_alterada.horario.minute)
            if data_atual <= partida <= data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA):
                onibus = gerar_id_onibus(linha_alterada, partida)
                app.linhas.insert(parent=linha_alterada, index='end', values=('-', fm.form_data(partida), assentos, '-'), iid=onibus)
                monitoradas.onibus_visiveis.add(onibus)
                estado.linhas_entradas[linha_alterada].onibus[onibus] = dict()
        
    
    app.contador_onibus['text'] = fm.form_cont_onibus(len(monitoradas.onibus_visiveis))
    app.contador_linhas['text'] = fm.form_cont_linhas(len(estado.linhas_visiveis))
    app.linhas.selection_set(linha_alterada)
    

    return 1


def unbook(app, reserva):
    estado.reservas.discard(reserva)
    app.reservas.delete(reserva)
    onibus = reserva[:-6]
    linha = onibus[:-7]

    del estado.linhas_entradas[linha].onibus[onibus][decodificar_id_reserva(reserva).assento]

    prev_values = app.linhas.set(onibus)
    prev_values['assentos livres'] = int(prev_values['assentos livres']) + 1
    app.linhas.see(onibus)
    app.linhas.selection_set(onibus)
    app.linhas.item(onibus, values=tuple(prev_values.values()))
    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
    return 1


def rebook(app, reserva):
    estado.reservas.add(reserva)
    app.reservas.insert(parent='',
                        index=0,
                        values=campos_reserva_formatados(reserva),
                        iid=reserva)
    app.reservas.see(reserva)
    app.reservas.selection_set(reserva)

    onibus = reserva[:-6]
    linha = onibus[:-7]
    info_reserva = decodificar_id_reserva(reserva)
    assento, passagem = info_reserva.assento, info_reserva.passagem.tipo
    estado.linhas_entradas[linha].onibus[onibus][assento] = passagem

    prev_values = app.linhas.set(onibus)
    prev_values['assentos livres'] = int(prev_values['assentos livres']) - 1
    app.linhas.see(onibus)
    app.linhas.selection_set(onibus)
    app.linhas.item(onibus, values=tuple(prev_values.values()))
    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
    return 1

def rereservar_reservas(app, reservas):
    actions = 0
    app.reservas.selection_set(*[])
    app.linhas.selection_set(*[])
    for indice, reserva in reservas:
        estado.reservas.add(reserva)
        app.reservas.insert(parent='',
                        index=indice,
                        values=campos_reserva_formatados(reserva),
                        iid=reserva)
        app.reservas.selection_add(reserva)
        
        onibus = reserva[:-6]
        linha = onibus[:-7]
        info_reserva = decodificar_id_reserva(reserva)
        assento, passagem = info_reserva.assento, info_reserva.passagem.tipo
        estado.linhas_entradas[linha].onibus[onibus][assento] = passagem

        prev_values = app.linhas.set(onibus)
        prev_values['assentos livres'] = int(prev_values['assentos livres']) - 1
        app.linhas.see(onibus)
        app.linhas.selection_add(onibus)
        app.linhas.item(onibus, values=tuple(prev_values.values()))
        actions += 1

    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))
    
    return actions

def devolver_reservas(app, reservas):
    actions = 0
    app.linhas.selection_set(*[])
    for _, reserva in reservas:
        estado.reservas.discard(reserva)
        app.reservas.delete(reserva)

        onibus = reserva[:-6]
        linha = onibus[:-7]

        del estado.linhas_entradas[linha].onibus[onibus][decodificar_id_reserva(reserva).assento]

        prev_values = app.linhas.set(onibus)
        prev_values['assentos livres'] = int(prev_values['assentos livres']) + 1
        app.linhas.see(onibus)
        app.linhas.selection_add(onibus)
        app.linhas.item(onibus, values=tuple(prev_values.values()))

        actions += 1

    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))

    return actions


desfazer = {
    'rmv': reattach_linhas,
    'add': descadastrar_linhas,
    'sort': desort,
    'change': restaurar,
    'book': unbook,
    'show': detach_linhas,
    'refund': rereservar_reservas,
    'import_reservas': devolver_reservas
}
refazer = {
    'rmv': detach_linhas,
    'add': recadastrar_linhas,
    'sort': resort,
    'change': mudar,
    'book': rebook,
    'show': reattach_linhas,
    'refund': devolver_reservas,
    'import_reservas': rereservar_reservas
}


def undo(app, evento=None):
    print('CTRL+Z')
    try:
        evento = chave, *dados = monitoradas.historico_undo.pop(-1)
        monitoradas.historico_redo.append(evento)
        actions = desfazer[chave](app, *dados)
        if actions == 0:
            undo(app)
        else:
            print(cte.ACOES_COMPLEMENTARES.get(chave, cte.ACTIONS.get(chave, chave)))
            ctrl.update_action(app, cte.ACOES_COMPLEMENTARES.get(chave, chave))
    except IndexError:
        print('Nothing to undo...')


def redo(app, evento=None):
    print('CTRL+SHIFT+Z')

    try:
        evento = chave, *dados = monitoradas.historico_redo.pop(-1)
        monitoradas.historico_undo.append(evento)
        actions = refazer[chave](app, *dados)
        if actions == 0:
            redo(app)
        else:
            print(cte.ACTIONS.get(chave, chave))
            ctrl.update_action(app, chave)
    except IndexError:
        print('Nothing to redo...')