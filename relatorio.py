'''
    Define funções associadas à geração do relatório.
'''

import tkinter as tk
from tkinter import filedialog, ttk
import estado
from gerar import decodificar_id_reserva, decodificar_id_onibus
import inteira as it
import datetime as dt
import util
import formatar as fm
import monitoradas
import constantes as cte


def exibir_relatorio(app):
    '''
        Constrói e exibe a janela do relatório.
    '''
    data_atual = monitoradas.data_atual

    janela = tk.Toplevel()
    janela.grab_set()
    janela.title('Relatório')
    janela.resizable(True, True)
    janela.minsize(700, 700)
    janela.transient(app.root)

    frame = ttk.Frame(janela, padding=10)
    frame.pack(fill='both', expand=True)

    def toggle_states(master, children):
        master_value = master.get()
        for state in children:
            state.set(master_value)
        if master_value:
            janela.minsize(700, 700)
            botao_exportar.state(['!disabled'])
            painel_arrecadado.grid()
            painel_passagens.grid()
            painel_ocupacao.grid()
        else:
            janela.minsize(700, 250)
            botao_exportar.state(['disabled'])
            painel_arrecadado.grid_remove()
            painel_passagens.grid_remove()
            painel_ocupacao.grid_remove()

    master_state = tk.IntVar(value=1)
    checkbox_master = ttk.Checkbutton(frame, variable=master_state)
    descriptive_label = ttk.Label(frame, text='Informações', anchor='center')

    distribuicao_passageiros = [0, 0, 0]    # [gratuita, meia, inteira]
    linha_dia_reservas = dict()
    monitoradas.arrecadado = dict()
    monitoradas.ocupacao_media_semanal = dict()

    total_passageiros = len(estado.reservas)

    def hide_widget(widget, show=False):
        x, y = janela.minsize()
        if not show:
            janela.minsize(x, y - 150)
            widget.grid_remove()
            if not any(x.get() for x in [arrecadado_state, passagens_state, ocupacao_state]):
                botao_exportar.state(['disabled'])
            return
        botao_exportar.state(['!disabled'])
        janela.minsize(x, y + 150)
        widget.grid()

    def form_arrecadado(
        n): return '  Total Arrecadado: R$ %s  ' % fm.separar_milhares_decimal(n)
    painel_arrecadado = ttk.LabelFrame(
        frame, text='Total Arrecadado', padding=10)
    arrecadado_state = tk.IntVar(value=1)
    checkbox_arrecadado = ttk.Checkbutton(frame, variable=arrecadado_state, command=lambda: hide_widget(
        painel_arrecadado, arrecadado_state.get()))
    treeview_arrecadado = ttk.Treeview(painel_arrecadado, columns=(
        'Linha', 'Arrecadado'), show='headings', selectmode='none', name='arrecadado')

    for i, coluna in enumerate(('Linha', 'Arrecadado (R$)')):
        treeview_arrecadado.heading(i, text=coluna.title(
        ), command=lambda col=i: util.treeview_sort_column(app, treeview_arrecadado, col, False))
        treeview_arrecadado.column(
            i, width=0, minwidth=len(coluna)*15, anchor='center')

    treeview_arrecadado.bind(
        '<Motion>', lambda ev: util.last_separator(ev, treeview_arrecadado))
    treeview_arrecadado.bind(
        '<1>', lambda ev: util.last_separator(ev, treeview_arrecadado))

    treeview_arrecadado_scroller_v = ttk.Scrollbar(
        painel_arrecadado, orient='vertical', command=treeview_arrecadado.yview)
    treeview_arrecadado_scroller_h = ttk.Scrollbar(
        painel_arrecadado, orient='horizontal', command=treeview_arrecadado.xview)

    treeview_arrecadado['yscrollcommand'] = treeview_arrecadado_scroller_v.set
    treeview_arrecadado['xscrollcommand'] = treeview_arrecadado_scroller_h.set

    passagens_state = tk.IntVar(value=1)
    painel_passagens = ttk.LabelFrame(
        frame, text='  Distribuição de Passagens  ', padding=10)
    checkbox_passagens = ttk.Checkbutton(frame, variable=passagens_state, command=lambda: hide_widget(
        painel_passagens, passagens_state.get()))
    label_passageiros = ttk.Label(painel_passagens, text='Total de Passageiros: %s' %
                                  fm.separar_milhares(total_passageiros), anchor='center')
    label_inteira = ttk.Label(painel_passagens, anchor='center')
    label_meia = ttk.Label(painel_passagens, anchor='center')
    label_gratuita = ttk.Label(painel_passagens, anchor='center')

    def form_ocupacao(
        n): return '  Ocupação Média: %s%%  ' % fm.separar_milhares_decimal(n)
    painel_ocupacao = ttk.LabelFrame(frame, text=form_ocupacao(0), padding=10)
    ocupacao_state = tk.IntVar(value=1)
    checkbox_ocupacao = ttk.Checkbutton(frame, variable=ocupacao_state, command=lambda: hide_widget(
        painel_ocupacao, ocupacao_state.get()))

    treeview_ocupacao = ttk.Treeview(painel_ocupacao, columns=(
        'Linha', 'Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'), show='headings', selectmode='none', name='ocupacao')

    for i, coluna in enumerate(('Linha', 'Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab')):
        treeview_ocupacao.heading(i, text=coluna.title(
        ), command=lambda col=i: util.treeview_sort_column(app, treeview_ocupacao, col, False))
        treeview_ocupacao.column(
            i, width=0, minwidth=len(coluna)*15, anchor='center')

    treeview_ocupacao.bind(
        '<Motion>', lambda ev: util.last_separator(ev, treeview_ocupacao))
    treeview_ocupacao.bind(
        '<1>', lambda ev: util.last_separator(ev, treeview_ocupacao))

    treeview_ocupacao_scroller_v = ttk.Scrollbar(
        painel_ocupacao, orient='vertical', command=treeview_ocupacao.yview)
    treeview_ocupacao_scroller_h = ttk.Scrollbar(
        painel_ocupacao, orient='horizontal', command=treeview_ocupacao.xview)

    treeview_ocupacao['yscrollcommand'] = treeview_ocupacao_scroller_v.set
    treeview_ocupacao['xscrollcommand'] = treeview_ocupacao_scroller_h.set

    checkbox_master['command'] = lambda: toggle_states(
        master_state, [arrecadado_state, passagens_state, ocupacao_state])

    def exportar_relatorio():
        '''
            Exporta o relatório como um arquivo .txt
        '''
        # pede um caminho ao usuário
        endereco = filedialog.asksaveasfilename(title='Exportar Relatório', defaultextension='.txt', filetypes=[
                                                ('txt', '*.txt'), ('csv', '*.csv'), ('todos', '*')], parent=janela)
        if endereco == '':
            return
        # cria o arquivo no endereço especificado pelo usuário
        with open(endereco, 'w') as arquivo_relatorio:
            # as variáveis *_state são IntVar, que possuem valor 1 se o check está selecionado, e 0 caso contrário
            # vamos escrever no arquivo .txt apenas as seções em que os checks estão marcados
            if arrecadado_state.get():
                arquivo_relatorio.write('{:*^101}\n'.format(' ARRECADAÇÃO '))
                arquivo_relatorio.write('%s\n' % painel_arrecadado['text'])
                arquivo_relatorio.write(
                    '{:*^49} | {:*^49}\n'.format(' LINHA ', ' ARRECADADO (R$) '))
                for linha in treeview_arrecadado.get_children():
                    arquivo_relatorio.write('{Linha:^50}|{Arrecadado:^50}\n'.format_map(
                        treeview_arrecadado.set(linha)))
            if passagens_state.get():
                if arrecadado_state.get():
                    arquivo_relatorio.write('\n\n')
                arquivo_relatorio.write(
                    '{:*^101}\n'.format(' DISTRIBUIÇÃO DE PASSAGENS '))
                arquivo_relatorio.write('{:^49} : {:^49}\n'.format(
                    'TOTAL', fm.separar_milhares(total_passageiros)))
                arquivo_relatorio.write('{:^49} : {:^49}\n'.format(
                    'INTEIRA', fm.separar_milhares_precisao(percentual_inteira)+' %'))
                arquivo_relatorio.write('{:^49} : {:^49}\n'.format(
                    'MEIA', fm.separar_milhares_precisao(percentual_meia)+' %'))
                arquivo_relatorio.write('{:^49} : {:^49}\n'.format(
                    'GRATUITA', fm.separar_milhares_precisao(percentual_gratuita)+' %'))
            if ocupacao_state.get():
                if passagens_state.get():
                    arquivo_relatorio.write('\n\n')
                arquivo_relatorio.write(
                    '{:*^167}\n'.format(' OCUPAÇÃO MÉDIA SEMANAL (%) '))
                arquivo_relatorio.write(('|'.join(['{:*^20}']*8)+'\n').format(
                    ' LINHA ', ' DOM ', ' SEG ', ' TER ', ' QUAR ', ' QUI ', ' SEX ', ' SAB '))
                for linha in treeview_ocupacao.get_children():
                    nome_linha = treeview_ocupacao.set(linha, 'Linha')
                    arquivo_relatorio.write(('|'.join(['{:*^20}']*8)+'\n').format(f' {nome_linha} ', *map(
                        lambda x: ' '+fm.separar_milhares_decimal(100*x)+' ', monitoradas.ocupacao_media_semanal[linha])))

    botao_exportar = ttk.Button(
        frame, text='Exportar', command=exportar_relatorio)

    checkbox_master.grid(row=0, column=0)
    descriptive_label.grid(row=0, column=1)

    checkbox_arrecadado.grid(row=1, column=0)
    painel_arrecadado.grid(row=1, column=1, sticky='news')
    treeview_arrecadado.grid(row=0, column=0, sticky='news')
    treeview_arrecadado_scroller_v.grid(row=0, column=1, sticky='ns')
    treeview_arrecadado_scroller_h.grid(row=1, column=0, sticky='we')
    painel_arrecadado.rowconfigure(0, weight=1)
    painel_arrecadado.columnconfigure(0, weight=1)

    checkbox_passagens.grid(row=2, column=0)
    painel_passagens.grid(row=2, column=1, sticky='ns')
    label_passageiros.grid(pady=(0, 10))
    label_inteira.grid()
    label_meia.grid()
    label_gratuita.grid()
    for i in range(4):
        painel_passagens.rowconfigure(i, weight=1)
    painel_passagens.columnconfigure(0, weight=1)

    checkbox_ocupacao.grid(row=3, column=0)
    painel_ocupacao.grid(row=3, column=1, sticky='news')
    treeview_ocupacao.grid(row=0, column=0, sticky='news')
    treeview_ocupacao_scroller_v.grid(row=0, column=1, sticky='ns')
    treeview_ocupacao_scroller_h.grid(row=1, column=0, sticky='we')
    painel_ocupacao.rowconfigure(0, weight=1)
    painel_ocupacao.columnconfigure(0, weight=1)

    botao_exportar.grid(row=4, column=0, columnspan=2)

    for i in range(3):
        frame.rowconfigure(i + 1, weight=1)

    frame.columnconfigure(1, weight=1)

    for reserva in estado.reservas:
        onibus = reserva[:-6]
        linha = onibus[:-7]
        dados_reserva = decodificar_id_reserva(reserva)
        passagem, inteira = dados_reserva[-1]
        monitoradas.arrecadado[linha] = monitoradas.arrecadado.get(
            linha, 0) + it.centavos(inteira, passagem)
        distribuicao_passageiros[passagem] += 1
        linha_dia_reservas[linha] = linha_dia_reservas.get(linha, [0]*7)
        linha_dia_reservas[linha][decodificar_id_onibus(
            onibus).isoweekday() % 7] += 1

    if total_passageiros == 0:
        percentual_inteira = percentual_meia = percentual_gratuita = 0
    else:
        (percentual_gratuita,
         percentual_meia,
         percentual_inteira) = [100*distribuicao_passageiros[i]/total_passageiros for i in range(3)]

    label_inteira['text'] = 'Inteira: %s%%' % fm.separar_milhares_decimal(
        percentual_inteira)
    label_meia['text'] = 'Meia: %s%%' % fm.separar_milhares_decimal(
        percentual_meia)
    label_gratuita['text'] = 'Gratuita: %s%%' % fm.separar_milhares_decimal(
        percentual_gratuita)

    total_arrecadado = 0

    def onibus_por_dia(linha):
        data_cadastro = estado.linhas_entradas[linha].horario
        dia_da_semana = data_cadastro.isoweekday()
        intervalo = (
            data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA) - data_cadastro).days
        onibus_diarios = [0]*7

        for i in range(7):
            if i in range((intervalo + 1) % 7):
                num_onibus = (intervalo + 1)//7 + 1
            else:
                num_onibus = (intervalo + 1)//7

            onibus_diarios[(dia_da_semana + i) % 7] = num_onibus

        return onibus_diarios.copy()

    vagas_ofertadas_totais = 0
    for linha in estado.linhas_entradas:
        destino, horario = estado.linhas_entradas[linha][:2]
        nome_linha = '%s-%s' % (destino.upper(), fm.form_tempo(horario))
        monitoradas.arrecadado[linha] = monitoradas.arrecadado.get(linha, 0)
        quantia = monitoradas.arrecadado[linha]/100
        total_arrecadado += quantia
        treeview_arrecadado.insert('', 0, linha, values=(
            nome_linha, fm.separar_milhares_decimal(quantia)))
        onibus_diarios = onibus_por_dia(linha)
        capacidade_linha = estado.linhas_entradas[linha].fileiras*2
        vagas_ofertadas_totais += sum(onibus_diarios)*capacidade_linha
        # print(f'Ônibus diários: {onibus_diarios}\nCapacidade linha: {capacidade_linha}')
        monitoradas.ocupacao_media_semanal[linha] = [linha_dia_reservas.get(linha, {d: 0})[
            d]/(onibus_diarios[d]*capacidade_linha) if onibus_diarios[d] != 0 else 0 for d in range(7)]
        treeview_ocupacao.insert('', 0, linha, values=(nome_linha, *map(lambda x: '%s%%' %
                                                                        fm.separar_milhares_decimal(100*x), monitoradas.ocupacao_media_semanal[linha])))
    painel_ocupacao['text'] = form_ocupacao(
        100*len(estado.reservas)/vagas_ofertadas_totais if vagas_ofertadas_totais != 0 else 0)

    painel_arrecadado['text'] = form_arrecadado(total_arrecadado)
