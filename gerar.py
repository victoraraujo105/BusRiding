'''
    Define funções para gerar e decodificar id de linhas, ônibus e reservas, e para gerar linhas aleatórias.
'''

import tkinter as tk
from tkinter import messagebox
import ttk
import datetime as dt
import monitoradas
import formatar as fm
import vagas as vg
import inteira as it
import constantes as cte
import control as ctrl
import estado
from collections import namedtuple


def minutos_dia(momento):
    '''
        Calcula a quantidade de minutos que se passarem desde o início do dia, com base na data "momento"
        especificada pelo argumento (objeto datetime).
    '''
    return momento.hour*60 + momento.minute


def gerar_id_linha(destino, horario):
    '''
        Gera um id para uma linha com os dados dos argumentos.
        O id preserva esses dados, pode ser decodificado e é usado para inserir componentes
        na interface gráfica.
    '''
    d = destino.lower()
    h = '%04d' % minutos_dia(horario)
    id = '-'.join([d, h])
    return id


def campos_linha_formatados(dados):
    '''
        Retorna uma tupla (campus, horario, assentos, inteira) de informações formatadas
        conforme os dados do argumento.
    '''
    # essas variáveis são os dados não formatados
    # referentes, respectivamente, a: campus, horario, assentos, inteira.
    c, h, a, i = dados[:4]
    campus = c.title()
    horario = h.strftime('%H:%M')
    assentos = int(a)*2
    inteira = '%.2f' % ((300 + i)/100)
    return campus, horario, assentos, inteira


def gerar_id_onibus(linha, partida):
    '''
        Gera um id para um ônibus com os dados dos argumentos.
        O id preserva esses dados, pode ser decodificado e é usado para inserir componentes
        na interface gráfica.
    '''
    id = '-'.join([linha, partida.strftime('%d%m%y')])
    return id


def decodificar_id_onibus(id):
    '''
        Retorna um datetime conforme o horário codificado no id do ônibus do argumento.
    '''
    # a informação ignorada (variável _) é o destino: não precisamos dele nessa função.
    # h é o horário (quantidade de minutos desde o início do dia) e p é uma data
    _, h, p = id.split('-')
    partida = dt.datetime.strptime(p, '%d%m%y') + dt.timedelta(minutes=int(h))
    return partida


def gerar_id_reserva(onibus, assento, passagem):
    '''
        Gera um id de uma reserva conforme os dados dos argumentos.
        O id preserva esses dados, pode ser decodificado e é usado para inserir componentes
        na interface gráfica.
    '''
    return '-'.join([onibus, '%03d' % assento, '%d' % passagem])


# atributos dos objetos reserva e passagem
estrutura_reserva = namedtuple(
    'reserva', ['campus', 'partida', 'assento', 'passagem'])
estrutura_passagem = namedtuple('passagem', ['tipo', 'inteira'])


def decodificar_id_reserva(reserva):
    '''
        Retorna um objeto com as propriedades "campus", "partida", "assento", "passagem"
        em que "passagem" é um objeto com as propriedades "tipo" e "inteira".
        Esses dados são obtidos pelo id da reserva passado como argumento.
    '''
    # os últimos 6 caracteres do id reserva são "-001-2" por exemplo,
    # em que 001 é o assento e 2 é o tipo de passagem (nesse caso, inteira)
    # então, ignorando esses últimos 6 caracteres, temos o id do ônibus
    onibus = reserva[:-6]
    # os últimos 7 caracteres do id do ônibus são "-010203" por exemplo,
    # em que 01 é o dia, 02 é o mês (fevereiro) e 03 é o ano (2003).
    # então, ignorando esses últimos 7 caracteres, temos o id da linha
    linha = onibus[:-7]
    # a seguir, as informações presentes no id da reserva:
    destino, h, p, assento, passagem = reserva.split('-', 5)
    partida = dt.datetime.strptime(p, '%d%m%y') + dt.timedelta(minutes=int(h))
    assento = int(assento)
    # 2 significa inteira, 1 significa meia, 0 significa gratuita
    passagem = int(passagem)
    inteira = estado.linhas_entradas[linha].inteira

    return estrutura_reserva(destino, partida, assento, estrutura_passagem(passagem, inteira))


def campos_reserva_formatados(reserva):
    '''
        Retorna uma tupla (campus, partida, assento, passagem) de informações formatadas
        conforme os dados do argumento a respeito de uma reserva.
        O argumento é o id da reserva.
    '''
    # conseguimos um objeto a partir do id da reserva
    reserva = decodificar_id_reserva(reserva)
    campus = reserva.campus.title()
    partida = reserva.partida.strftime('%d/%m/%y %H:%M')
    assento = reserva.assento
    passagem = '%8s: R$%s' % (cte.INDICE_PASSAGEM[reserva.passagem.tipo].title(
    ), it.inteira_termo(reserva.passagem.inteira, reserva.passagem.tipo))
    return campus, partida, assento, passagem


def coordenadas_assento(assento, num_fileiras):
    '''
        Retorn a posição (i, j) do assento com base na numeração dele e no número de fileiras.
    '''
    divisao = 2*num_fileiras
    if assento <= divisao:
        # os assentos à esquerda obedecem à ordem:
        # 1 2
        # 3 4
        # ...
        # pois os assentos pares são adjacentes ao corredor
        i = (assento - 1) // 2
        j = (assento - 1) % 2
    else:
        # os assentos à direita obedecem à ordem:
        # 20 19
        # 22 21
        # 24 23
        # ...
        # pois os assentos pares são adjacentes ao corredor
        # divisao é a quantidade de assentos na seção da esquerda
        i = (assento - divisao - 1) // 2
        j = assento % 2 + 2
    return i, j


def assento_coordenadas(i, j, num_fileiras):
    # Retorna o número do assento com base na posição (i, j)
    # Essa função faz basicamente o cálculo inverso da função "coordenadas_assento"
    # separamos em dois casos:
    # quando j <= 1, significa que o assento está na seção da esquerda
    # quando j > 1, significa que o assento está na seção da direita
    assento = 2*i + j + 1 if j <= 1 else 2*(num_fileiras + i + 2) - j
    return assento


def gerar_linhas(app):
    '''
        Constrói uma interface que permite o cadastro de linhas aleatórias.
    '''
    limite = len(estado.linhas_possiveis)
    if limite == 0:
        messagebox.showwarning(title='Limite Atingido',
                               message=f'Limite de cadastros atingido: {len(estado.linhas_entradas)}.')
        return

    # Primeiro, definimos uma interface para coletar os dados
    # do processo de geração das linhas
    configuracoes = tk.Toplevel()
    configuracoes.grab_set()
    configuracoes.title('Gerador')
    configuracoes.geometry('200x200')
    configuracoes.resizable(False, False)
    configuracoes.transient(app.root)

    frame = ttk.Frame(configuracoes)
    frame.grid(row=0, column=0, sticky='nsew')
    # frame é o único child de configurações
    configuracoes.rowconfigure(0, weight=1)
    configuracoes.columnconfigure(0, weight=1)

    # ESTRUTURA VISUAL
    # dentro do frame, iremos colocar:
    # - um texto com a pergunta e um botão, que é a variável "prompt"
    # - um spinbox que permite a entrada de um valor numérico, que é a variável "spin_linhas"
    # - um checkbutton que permite a escolha pelo usuário de "Ocupar assentos" aleatoriamente,
    #      que é a variável "check_ocupar_assentos"
    # - um botão para finalizar o processo (gerar as linhas), que é a variável "botao_gerar"

    instrucao = f'Quantas linhas aleatórias pretendes gerar?\n\nInsira inteiro entre 1 e {limite}, inclusive ambos.'
    prompt = ttk.Label(frame,
                       text=instrucao,
                       anchor='center',
                       justify='center',
                       wraplength=180)
    prompt.grid(row=0, column=0)

    frame.rowconfigure(0, weight=1)

    # essa StringVar é a variável que irá monitorar o valor no widget spin_linhas, e
    # indica a quantidade de linhas que o usuário pretende gerar
    num = tk.StringVar()
    # n = 99
    def termo(n): return n + 1
    monitoradas.indice_linhas_geradas = min(
        monitoradas.indice_linhas_geradas, limite - 1)
    num.set(termo(monitoradas.indice_linhas_geradas))

    # as funções atualizar/incrementar/decrementar são parecidas com outras definidos para outras StringVar
    # em spinboxes:
    # incrementar e decrementar são chamadas quando o usuário clica na seta (para cima ou para baixo)
    # e atualizar verificar se o valor digitado pelo usuário é válido:
    # se não for válido, atualiza o campo de texto do spinbox para o último valor válido
    # nesse caso, armazenado em monitoradas.indice_linhas_geradas
    def atualizar_num():
        num_valido = False
        try:
            entrada = round(float(num.get()))
            if entrada in range(1, limite + 1):
                monitoradas.indice_linhas_geradas = entrada - 1
                num_valido = True
        except ValueError:
            pass
        num.set(termo(monitoradas.indice_linhas_geradas))
        return num_valido

    def incrementar_num(event):
        atualizar_num()
        monitoradas.indice_linhas_geradas += 1
        monitoradas.indice_linhas_geradas %= limite

        num.set(termo(monitoradas.indice_linhas_geradas))

        return 'break'

    def decrementar_num(event):
        atualizar_num()
        monitoradas.indice_linhas_geradas -= 1
        monitoradas.indice_linhas_geradas %= limite

        num.set(termo(monitoradas.indice_linhas_geradas))

        return 'break'

    # esse é o spinbox ao qual as funções acima se referem
    spin_linhas = ttk.Spinbox(frame,
                              textvariable=num,
                              width=6,
                              justify='center')
    spin_linhas.bind('<<Increment>>', incrementar_num)
    spin_linhas.bind('<<Decrement>>', decrementar_num)
    spin_linhas.grid(row=1, column=0)

    # O botão "Ocupar assentos"
    # o valor marcado será monitorado pela variável monitoradas.ocupar_assentos
    check_ocupar_assentos = ttk.Checkbutton(
        frame, text='Ocupar assentos.', variable=monitoradas.ocupar_assentos)
    check_ocupar_assentos.grid(row=2, column=0)

    frame.rowconfigure(1, weight=1)

    def gerar(event=None):
        '''
            Gera as linhas conforme a quantidade indicada pelo spin_linhas.
            É executado quando o usuário clica no botão de gerar, ou aperta ENTER.
        '''
        if not atualizar_num():
            # aqui, atualizar_num retornou False, o que significa que a entrada é inválida
            messagebox.showwarning(title='Entrada Inválida',
                                   message='Valor inválido!',
                                   parent=configuracoes)
            return

        from random import choice, randrange, sample
        ocupar = monitoradas.ocupar_assentos.get()
        # Uma sequência em que o valor assento_coordenadas(i, j) indica o número do assento na linha i e coluna j.
        # Note que para cada linha, há 4 colunas (índice j varia de 0 a 3).
        # As colunas 0 e 3 são adjacentes à janela e as colunas 1 e 2 são adjacentes ao corredor.
        # Essa sequência pode ser vista ao tentar reservar um assento.
        def assento_coordenadas(i, j): return 2*i + j + \
            1 if j <= 1 else 2*(num_fileiras + i + 2) - j
        dados = []
        data_atual = monitoradas.data_atual
        minutos_atual = data_atual.hour*60 + data_atual.minute
        # termo(monitoradas.indice_linhas_geradas) é o número de linhas indicado pelo spin_linhas
        # note que minutes[:termo(monitoradas.indice_linhas_geradas)] seleciona
        # justamente a quantidade de linhas que queremos!
        # como minutes foi permutado aleatoriamente, os horários em minutes escolhidos
        # pelo slicing são aleatórios e diferentes entre si
        for destino, t in sample(estado.linhas_possiveis, termo(monitoradas.indice_linhas_geradas)):
            estado.linhas_possiveis.discard((destino, t))
            # t é uma quantidade de minutos da lista minutes, que usaremos para calcular o horário dessa linha que
            # iremos cadastrar!
            interval = dt.timedelta(minutes=t)
            horario = data_atual.replace(hour=0, minute=0) + interval
            if data_atual > horario:
                horario += dt.timedelta(1)
            linha = gerar_id_linha(destino, horario)

            indice_vagas = choice(range(cte.MAXIMO_NUMERO_DE_FILEIRAS))
            num_fileiras = indice_vagas + 1
            vagas = vg.vagas_termo(indice_vagas)
            indice_inteira = choice(range(301))
            inteira = it.inteira_termo(indice_inteira)

            estado.horarios_linhas[t] = estado.horarios_linhas.get(
                t, set()).union({linha})

            app.linhas.insert(parent='',
                              index=0,
                              values=(destino, fm.form_tempo(
                                  horario), vagas, inteira),
                              iid=linha)
            estado.linhas_entradas[linha] = cte.ESTRUTURA_LINHA(
                destino, horario, num_fileiras, indice_inteira, dict())
            estado.linhas_visiveis.add(linha)

            reservas = list()

            # calculamos o período de dias em que haverá ônibus partindo
            if t == minutos_atual:
                periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
            elif t < minutos_atual:
                # aqui, o horário da linha é menor que o horário atual,
                # então não vamos criar um ônibus para o dia de hoje, pois ele já partiu
                periodo = range(1, cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA + 1)
            else:
                # aqui, o horário da linha é maior que o horário atual,
                # então vamos incluir o dia de hoje
                periodo = range(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)

            for d in periodo:
                # para cada dia no período calculado, vamos adicionar um ônibus
                # note que d = 0 representa o dia de hoje, d = 1 é amanhã, etc.
                partida = data_atual + dt.timedelta(d)
                onibus = gerar_id_onibus(linha, partida)
                assentos_disponiveis = randrange(vagas+1) if ocupar else vagas
                app.linhas.insert(parent=linha, index='end', values=(
                    '-', fm.form_data(partida), assentos_disponiveis, '-'), iid=onibus)
                estado.linhas_entradas[linha].onibus[onibus] = dict()
                if assentos_disponiveis < vagas:
                    # nesse caso, significa que o usuário pediu para "Ocupar assentos"
                    # e o valor aleatorio assentos disponíveis é menor que a quantidade de vagas
                    # então, devemos fazer algumas reservas aleatórias!
                    # primeiro, vamos escolher quais assentos serão escolhíveis
                    # (afinal, metade dos assentos serão disponíveis, então vamos escolher qual metade)
                    shift = choice(range(2))
                    # os assentos escolhíveis respeitam as condições impostas pela pandemia
                    # basicamente, selecionamos (i, (i + shift) % 2) e (i, 2 + (i + shift) % 2) para todo i
                    # por exemplo,
                    # i = 0, shift = 0 -> selecionamos (0, 0) e (0, 2)
                    # i = 1, shift = 0 -> selecionamos (1, 1) e (1, 3)
                    # i = 2, shift = 0 -> selecionamos (2, 0) e (2, 2)
                    # Note que a primeira posição é um assento da seção da esquerda
                    # e a segunda posição é um assento da seção da direita
                    # e selecionamos dois assentos por linha
                    assentos_visiveis = {assento_coordenadas(i, 2 * j + (i + shift) % 2) for j in range(2)
                                         for i in range(num_fileiras)}
                    # a função sample seleciona aleatoriamente números de assentos escolhíveis para
                    # fazermos reserva
                    for assento in sample(assentos_visiveis, vagas - assentos_disponiveis):
                        # a variável assento é um número de assento escolhível aleatório
                        # devemos reservar esse assento!
                        passagem = choice([2]*3+[1]*2+[0])
                        estado.linhas_entradas[linha].onibus[onibus][assento] = passagem
                        reserva = gerar_id_reserva(onibus, assento, passagem)
                        estado.reservas.add(reserva)
                        reservas.insert(0, reserva)
                        app.reservas.insert(parent='',
                                            index=0,
                                            values=campos_reserva_formatados(
                                                reserva),
                                            iid=reserva)
                monitoradas.onibus_visiveis.add(onibus)

            dados.append([estado.linhas_entradas[linha], reservas])

        ctrl.update_action(app, 'add')

        historico_undo = monitoradas.historico_undo
        historico_redo = monitoradas.historico_redo
        historico_redo.clear()
        historico_undo.append(['add', dados])

        app.contador_linhas['text'] = fm.form_cont_linhas(
            len(estado.linhas_visiveis))
        app.contador_onibus['text'] = fm.form_cont_onibus(
            len(monitoradas.onibus_visiveis))
        app.contador_reservas['text'] = fm.form_cont_reservas(
            len(estado.reservas))
        configuracoes.destroy()

    botao_gerar = ttk.Button(frame, text='Gerar', command=gerar)

    configuracoes.bind('<Return>', gerar)
    botao_gerar.bind('<Return>', gerar)
    botao_gerar.grid(row=3, column=0)

    frame.rowconfigure(3, weight=1)
    frame.columnconfigure(0, weight=1)
