'''
    Define funções para importação e exportação de arquivos.
'''

import estado
import monitoradas
import constantes as cte
import formatar as fm
import inteira as it
import datetime as dt
from gerar import minutos_dia, decodificar_id_reserva, gerar_id_linha, gerar_id_onibus, gerar_id_reserva, coordenadas_assento, assento_coordenadas
import tkinter as tk
from tkinter import filedialog
import ttk
import ntpath
import util


def exportar_linhas_invalidas(linhas_invalidas, heading, parent):
    '''
        Exporta os dados sobre linhas inválidas.
        O argumento linhas_invalidas é uma lista de strings já prontas para serem escritas.
        O argumento heading é a primeira linha do arquivo exportado, útil para explicar o conteúdo do arquivo.
    '''
    endereco = filedialog.asksaveasfilename(title='Exportar Linhas Inválidas', defaultextension='.csv', filetypes=[
                                            ('csv', '*.csv'), ('txt', '*.txt'), ('todos', '*')], parent=parent)
    if endereco == '':
        return
    # vamos criar um arquivo no endereço indicado pelo usuário
    with open(endereco, 'w') as arquivo_reservas:
        # escrevemos a primeira linha conforme o argumento heading
        arquivo_reservas.write('%s\n' % heading)
        for linha in linhas_invalidas:
            # escrevemos cada linha em linhas_invalidas
            arquivo_reservas.write(linha)


def reservar(app, indice, reserva):
    '''
        Atualiza o estado da aplicação para incluir a reserva especificada no argumento.
    '''
    # lembrando que reserva é um wrapper (veja csv_to_reserva) e reserva.reserva é o id da reserva
    estado.reservas.add(reserva.reserva)
    # o wrapper nos dá as informações que precisamos
    campus = reserva.campus.title()
    partida = reserva.partida.strftime('%d/%m/%y %H:%M')
    assento = reserva.assento
    passagem = '%8s: R$%s' % (cte.INDICE_PASSAGEM[reserva.passagem].title(
    ), it.inteira_termo(reserva.inteira, reserva.passagem))
    # adicionamos a reserva à interface gráfica
    app.reservas.insert(parent='',
                        index=indice,
                        values=(campus, partida, assento, passagem),
                        iid=reserva.reserva)

    onibus = reserva.onibus
    linha = reserva.linha
    estado.linhas_entradas[linha].onibus[onibus][reserva.assento] = reserva.passagem

    # vamos atualizar o valor da coluna "assentos livres" do ônibus associado à reserva
    prev_values = app.linhas.set(onibus)
    prev_values['assentos livres'] = int(prev_values['assentos livres']) - 1
    # colocamos foco e selecionamos o ônibus para o qual foi realizada a reserva
    app.linhas.see(onibus)
    app.linhas.selection_add(onibus)
    app.linhas.item(onibus, values=tuple(prev_values.values()))
    app.contador_reservas['text'] = fm.form_cont_reservas(len(estado.reservas))


def reserva_to_csv(reserva):
    '''
        Retorna uma string com os dados da reserva separados por vírgula.
        O argumento é o id da reserva.
    '''
    reserva = decodificar_id_reserva(reserva)

    campus = reserva.campus.title()
    partida = reserva.partida.strftime('%d/%m/%y %H:%M')
    assento = str(reserva.assento)
    passagem = cte.INDICE_PASSAGEM[reserva.passagem.tipo]

    linha = ', '.join([campus, partida, assento, passagem])+'\n'
    return linha


def csv_to_reserva(app, linha, data_presente=monitoradas.data_atual, data_maxima=monitoradas.data_atual + dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)):
    '''
        Cria e retorna um wrapper sobre a reserva com base na string linha.
        Aqui está o formato do wrapper:

        wrapper = {
            'validez': valor_booleano,
            'texto': 'Ok',
            'reserva': id_da_reserva,
            'campus': id_do_campus,
            'partida': partida,
            'assento': assento,
            'passagem': passagem,
            'inteira': inteira,
            'linha': id_da_linha,
            'onibus': id_do_onibus
        }

        Mas as propriedades são acessíveis pela sintaxe de objeto (wrapper.validez) em vez
        da sintaxe de dict (wrapper['validez'])

        Caso a reserva não seja válida, essa função verifica o erro e coloca uma mensagem de erro na propriedade
        "texto" do wrapper, além de atribuir False para a propriedade "validez".
    '''
    # note que type('', (), DICIONARIO) é utilizado para que possamos nos referir às propriedades com a sintaxe de
    # objeto, em vez da sintaxe de dicionário.
    # Ou seja, podemos usar OBJETO.PROPRIEDADE em vez de DICIONARIO['PROPRIEDADE'], o que ajuda no desenvolvimento,
    # já que a IDE é capaz de detectar propriedades inexistentes antes mesmo de o código rodar.
    try:
        campus, partida, assento, * \
            passagem = map(str.strip, linha.split(',', 4)[:4])
    except ValueError:
        return type('', (), {'validez': False, 'texto': 'quantidade insuficiente de campos, esperava-se ao menos 3'})
    campus = campus.replace('-', ' ').strip()
    if campus == '':
        return type('', (), {'validez': False, 'texto': 'destino vazio'})
    try:
        partida = dt.datetime.strptime(partida, '%d/%m/%y %H:%M')
        if not data_presente <= partida <= data_maxima:
            return type('', (), {'validez': False, 'texto': 'data fora do intervalo previsto'})
    except ValueError:
        return type('', (), {'validez': False, 'texto': f'data não segue formato previsto: {data_maxima.strftime("%d/%m/%y %H:%M")}'})
    try:
        assento = int(assento)
        if assento not in range(1, 4*cte.MAXIMO_NUMERO_DE_FILEIRAS + 1):
            return type('', (), {'validez': False, 'texto': 'assento fora do intervalo previsto'})
    except ValueError:
        return type('', (), {'validez': False, 'texto': f'assento não é inteiro em [1, {4*cte.MAXIMO_NUMERO_DE_FILEIRAS}]'})
    if passagem == []:
        passagem = cte.PASSAGEM_INDICE['inteira']
    else:
        passagem = cte.PASSAGEM_INDICE.get(passagem[0].lower(), None)
        if passagem is None:
            return type('', (), {'validez': False, 'texto': 'tipo de passagem inválida'})

    linha = gerar_id_linha(campus, partida)
    if linha not in estado.linhas_entradas:
        return type('', (), {'validez': False, 'texto': 'linha inexistente'})
    elif linha not in estado.linhas_visiveis:
        return type('', (), {'validez': False, 'texto': 'linha desabilitada'})

    onibus = gerar_id_onibus(linha, partida)
    if onibus in estado.onibus_invisiveis:
        return type('', (), {'validez': False, 'texto': 'ônibus desabilitado'})
    if assento in estado.linhas_entradas[linha].onibus[onibus]:
        return type('', (), {'validez': False, 'texto': 'assento reservado'})
    num_fileiras = estado.linhas_entradas[linha].fileiras
    shift = (sum(coordenadas_assento(assento, num_fileiras)) + 1) % 2
    assentos_indisponiveis = {assento_coordenadas(
        i, 2 * j + (i + shift) % 2, num_fileiras) for j in range(2) for i in range(num_fileiras)}
    if assento in assentos_indisponiveis:
        return type('', (), {'validez': False, 'texto': 'assento indisponível'})
    reserva = gerar_id_reserva(onibus, assento, passagem)
    inteira = estado.linhas_entradas[linha].inteira
    atributos = {'validez': True, 'texto': 'Ok', 'reserva': reserva, 'campus': campus, 'partida': partida,
                 'assento': assento, 'passagem': passagem, 'inteira': inteira, 'linha': linha, 'onibus': onibus}
    return type('reserva', (), atributos)


def importar_reservas(app):
    '''
        Importa os dados sobre as reservas no caminho escolhido pelo usuário.
    '''
    enderecos = filedialog.askopenfilenames(title='Importar Reservas', filetypes=[
                                            ('csv', '*.csv'), ('txt', '*.txt'), ('todos', '*')])
    if all([ntpath.basename(endereco).strip() == '' for endereco in enderecos]):
        return
    reservas = []
    data_atual = monitoradas.data_atual
    data_maxima = data_atual + \
        dt.timedelta(cte.MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA)

    # a janela a seguir é um relatório com os resultados da importação
    janela = tk.Toplevel()
    janela.grab_set()
    janela.title('Relatório Importação')
    janela.resizable(True, True)
    janela.minsize(700, 300)
    janela.transient(app.root)

    frame = ttk.Frame(janela)
    frame.pack(fill='both', expand=True)

    def form_reservas_feitas(
        n): return 'Reservas feitas: %s' % fm.separar_milhares(n)
    label_reservas_feitas = ttk.Label(frame, text=form_reservas_feitas(0))
    label_reservas_feitas.grid(
        row=0, column=0, sticky='nwes', padx=10, pady=10)
    frame.rowconfigure(0, weight=0)
    frame.columnconfigure(0, weight=1)

    # a partir daqui, vamos armazenar as linhas inválidas do arquivo importado
    # e explicar o motivo da invalidez
    linhas_invalidas = []
    def form_linhas_invalidas(
    ): return '  Linhas inválidas: %s  ' % fm.separar_milhares(len(linhas_invalidas))
    painel_linhas_invalidas = ttk.LabelFrame(
        frame, text=form_linhas_invalidas(), padding=10)
    painel_linhas_invalidas.grid(
        row=1, column=0, sticky='nwes', padx=10, pady=10)
    frame.rowconfigure(1, weight=1)

    treeview_linhas_invalidas = ttk.Treeview(painel_linhas_invalidas, columns=(
        'Arquivo', 'Linha', 'Motivo'), selectmode='none')
    treeview_linhas_invalidas.column('#0', width=20, stretch=0)
    for i, coluna in enumerate(('Arquivo', 'Linha', 'Motivo')):
        treeview_linhas_invalidas.heading(i, text=coluna)
        treeview_linhas_invalidas.column(
            i, width=0, minwidth=len(coluna)*15, anchor='center')
    treeview_linhas_invalidas.bind(
        '<Motion>', lambda ev: util.last_separator(ev, treeview_linhas_invalidas))
    treeview_linhas_invalidas.bind(
        '<1>', lambda ev: util.last_separator(ev, treeview_linhas_invalidas))
    treeview_linhas_invalidas.grid(row=0, column=0, sticky='nsew')
    painel_linhas_invalidas.rowconfigure(0, weight=1)
    painel_linhas_invalidas.columnconfigure(0, weight=1)

    linhas_invalidas_scroller_v = ttk.Scrollbar(
        painel_linhas_invalidas, orient='vertical', command=treeview_linhas_invalidas.yview)
    linhas_invalidas_scroller_v.grid(row=0, column=1, sticky='ns')

    linhas_invalidas_scroller_h = ttk.Scrollbar(
        painel_linhas_invalidas, orient='horizontal', command=treeview_linhas_invalidas.xview)
    linhas_invalidas_scroller_h.grid(row=1, column=0, sticky='ew')

    treeview_linhas_invalidas['yscrollcommand'] = linhas_invalidas_scroller_v.set
    treeview_linhas_invalidas['xscrollcommand'] = linhas_invalidas_scroller_h.set

    for endereco in enderecos:
        nome_arquivo = ntpath.basename(endereco)
        treeview_linhas_invalidas.insert(
            '', 'end', nome_arquivo, open=True, values=(nome_arquivo, '-', '-'))
        treeview_linhas_invalidas.detach(nome_arquivo)
        with open(endereco, 'r') as arquivo_reservas:
            for i, linha in enumerate(arquivo_reservas, 1):
                if linha.startswith(('-', '\n')):
                    continue
                # vamos criar o objeto reserva com base na linha lida
                reserva = csv_to_reserva(app, linha, data_atual, data_maxima)

                if reserva.validez:
                    # aqui, sabemos que a reserva é válida
                    # então podemos realizá-la
                    indice = len(reservas)
                    reservar(app, indice, reserva)
                    # reserva.reserva é o id da reserva, que contém informações
                    # sobre ônibus, assento e passagem associados à reserva
                    reservas.append([indice, reserva.reserva])
                    label_reservas_feitas['text'] = form_reservas_feitas(
                        len(reservas))
                    continue
                # aqui, a reserva é inválida
                # o motivo está em reserva.texto, e foi adicionado pela função csv_to_reserva

                # (((((linha[:-1] if linha[-1] == '\n' else linha))))) significa que
                # vamos ignorar a quebra de linha, se ela existir no final da linha, para que a explicação
                # da invalidez ocupe apenas uma linha
                linhas_invalidas.append(
                    '%s, --> %s\n' % (linha[:-1] if linha[-1] == '\n' else linha, reserva.texto))
                painel_linhas_invalidas['text'] = form_linhas_invalidas()
                # vamos adicionar à interface gráfica uma linha com o motivo
                treeview_linhas_invalidas.insert(
                    nome_arquivo, 'end', values=('-', i, reserva.texto))

        if len(linhas_invalidas) > 0:
            treeview_linhas_invalidas.reattach(nome_arquivo, '', 'end')
            heading = '- Linha, --> Motivo\n'
            botao_exportar = ttk.Button(painel_linhas_invalidas, text='Exportar Linhas Inválidas',
                                        command=lambda: exportar_linhas_invalidas(linhas_invalidas, heading, janela))
            botao_exportar.grid(row=2, column=0, sticky='we')
    if reservas != []:
        # coloca o foco sobre a primeira reserva (note que reservas[0] é o primeiro wrapper
        # e reservas[0][1] é o id da reserva associado ao primeiro wrapper)
        app.reservas.see(reservas[0][1])
        # seleciona todas as reservas (note que x[1] é o id da reserva associado a cada wrapper x em reservas)
        # adicionadas pela importação
        app.reservas.selection_set([x[1] for x in reservas])
        monitoradas.historico_redo.clear()
        # atualiza o histórico para permitir CTRL+Z
        monitoradas.historico_undo.append(['import_reservas', reservas])


def exportar_reservas(app):
    '''
        Exporta os dados sobre as reservas no caminho escolhido pelo usuário.
    '''
    # O explorador de arquivos pede ao usuário um caminho para onde os dados devem ser exportados
    endereco = filedialog.asksaveasfilename(title='Exportar Reservas', defaultextension='.csv', filetypes=[
                                            ('csv', '*.csv'), ('txt', '*.txt'), ('todos', '*')])
    # vamos exportar as reservas selecionados pelo usuário
    selecao = app.reservas.selection()
    if len(selecao) == 0:
        # se o usuário não selecionou nenhuma reserva, iremos exportar todas
        selecao = app.reservas.get_children()
    # vamos criar um arquivo no caminho especificado
    with open(endereco, 'w') as arquivo_reservas:
        arquivo_reservas.write(
            '- Destino, Partida (dia/mês/ano hora:minuto), Assento, Passagem (inteira, meia ou gratuita)\n\n')
        for reserva in selecao:
            # e escrever uma linha para cada reserva
            arquivo_reservas.write(reserva_to_csv(reserva))


def adicionar_linha(app, indice, linha, data_atual=monitoradas.data_atual):
    '''
        Altera o estado da aplicação (incluindo a interface gráfica) para incluir a linha especificada no argumento.
    '''
    destino = linha.campus.title()
    if destino not in estado.destinos:
        # adicionamos o destino da linha do argumento, caso ele não exista
        estado.destinos.append(destino)
        estado.linhas_possiveis.update({(destino, t) for t in range(1440)})
        estado.destinos.sort()  # mantemos a ordenação
        app.entrada_destino['values'] = estado.destinos
        monitoradas.destino.set(estado.destinos[0])
    t = minutos_dia(linha.horario)
    estado.horarios_linhas[t] = estado.horarios_linhas.get(
        t, set()).union({linha.id})
    # incluimos a linha na interface gráfica
    estado.linhas_possiveis.discard((destino, t))
    app.linhas.insert(parent='',
                      index=indice,
                      values=(destino, fm.form_tempo(linha.horario), 2 *
                              linha.fileiras, it.inteira_termo(linha.inteira)),
                      iid=linha.id)
    estado.linhas_visiveis.add(linha.id)
    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))

    estado.linhas_entradas[linha.id] = cte.ESTRUTURA_LINHA(
        destino, linha.horario, linha.fileiras, linha.inteira, dict())

    minutos_atual = minutos_dia(data_atual)

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
        partida = (data_atual + dt.timedelta(d)
                   ).replace(hour=linha.horario.hour, minute=linha.horario.minute)
        onibus = gerar_id_onibus(linha.id, partida)
        app.linhas.insert(parent=linha.id, index='end', values=(
            '-', fm.form_data(partida), 2*linha.fileiras, '-'), iid=onibus)
        monitoradas.onibus_visiveis.add(onibus)
        # todos os assentos estão livres
        estado.linhas_entradas[linha.id].onibus[onibus] = dict()
        app.contador_onibus['text'] = fm.form_cont_onibus(
            len(monitoradas.onibus_visiveis))

    app.contador_linhas['text'] = fm.form_cont_linhas(
        len(estado.linhas_visiveis))
    app.contador_onibus['text'] = fm.form_cont_onibus(
        len(monitoradas.onibus_visiveis))


def linha_to_csv(linha):
    '''
        Retorna uma string com os dados do objeto (wrapper) linha separados por vírgula.
    '''
    dados = estado.linhas_entradas[linha]

    campus = dados.destino.title()
    horario = dados.horario.strftime('%H:%M')
    assentos = '%d' % (2*dados.fileiras)
    inteira = it.inteira_termo(dados.inteira)

    linha = ', '.join([campus, horario, assentos, inteira])+'\n'
    return linha


def csv_to_linha(app, linha, data_atual=monitoradas.data_atual):
    '''
        Cria e retorna um wrapper sobre a linha com base na string linha.
        Aqui está o formato do wrapper:

        atributos = {
            'validez': valor_booleano,
            'texto': 'Ok',
            'id': id_da_linha,
            'campus': campus,
            'horario': horario,
            'fileiras': fileiras,
            'inteira': inteira
        }

        Mas as propriedades são acessíveis pela sintaxe de objeto (wrapper.validez) em vez
        da sintaxe de dict (wrapper['validez'])

        Caso a reserva não seja válida, essa função verifica o erro e coloca uma mensagem de erro na propriedade
        "texto" do wrapper, além de atribuir False para a propriedade "validez".
    '''
    # note que type('', (), DICIONARIO) é utilizado para que possamos nos referir às propriedades com a sintaxe de
    # objeto, em vez da sintaxe de dicionário.
    # Ou seja, podemos usar OBJETO.PROPRIEDADE em vez de DICIONARIO['PROPRIEDADE'], o que ajuda no desenvolvimento,
    # já que a IDE é capaz de detectar propriedades inexistentes antes mesmo de o código rodar.
    try:
        campus, horario, assentos, inteira = map(
            str.strip, linha.split(',', 4)[:4])
    except ValueError:
        return type('', (), {'validez': False, 'texto': 'quantidade insuficiente de campos, esperava-se 4'})
    campus = campus.replace('-', ' ').strip()
    if campus == '':
        return type('', (), {'validez': False, 'texto': 'destino vazio'})
    try:
        horario = dt.datetime.strptime(horario, '%H:%M')
    except ValueError:
        return type('', (), {'validez': False, 'texto': f'horário não segue formato previsto: {data_atual.strftime("%H:%M")}'})
    try:
        fileiras = int(assentos)//2
        if fileiras not in range(1, cte.MAXIMO_NUMERO_DE_FILEIRAS + 1):
            return type('', (), {'validez': False, 'texto': f'número máximo de assentos livres fora do intervalo previsto: [1, {cte.MAXIMO_NUMERO_DE_FILEIRAS*4}]'})
    except ValueError:
        return type('', (), {'validez': False, 'texto': f'número máximo de assentos livres não é inteiro em [1, {4*cte.MAXIMO_NUMERO_DE_FILEIRAS}]'})
    try:
        inteira = round(float(inteira)*100 - 300)
        if inteira not in range(301):
            return type('', (), {'validez': False, 'texto': f'valor inteira fora do intervalo previsto: [3.0, 6.0]'})
    except ValueError:
        return type('', (), {'validez': False, 'texto': f'valor inteira não é float em [3.0, 6.0]'})

    linha = gerar_id_linha(campus, horario)
    if linha in estado.linhas_visiveis:
        return type('', (), {'validez': False, 'texto': 'linha existente'})
    elif linha in estado.linhas_entradas:
        return type('', (), {'validez': False, 'texto': 'linha desabilitada'})

    atributos = {'validez': True, 'texto': 'Ok', 'id': linha, 'campus': campus,
                 'horario': horario, 'fileiras': fileiras, 'inteira': inteira}
    return type('linha', (), atributos)


def importar_linhas(app):
    '''
        Importa os dados sobre as linhas no caminho escolhido pelo usuário.
    '''
    # pedimos para o usuário selecionar caminhos (pelo explorador de arquivos)
    enderecos = filedialog.askopenfilenames(title='Importar Linhas', filetypes=[
                                            ('csv', '*.csv'), ('txt', '*.txt'), ('todos', '*')])
    if all([ntpath.basename(endereco).strip() == '' for endereco in enderecos]):
        return
    # variáveis para monitorar o processo de importação
    linhas = []
    ids_linhas = []
    data_atual = monitoradas.data_atual

    # janela principal
    janela = tk.Toplevel()
    janela.grab_set()
    janela.title('Relatório Importação')
    janela.resizable(True, True)
    janela.minsize(700, 300)
    janela.transient(app.root)

    frame = ttk.Frame(janela)
    frame.pack(fill='both', expand=True)

    def form_linhas_adicionadas(
        n): return 'Linhas adicionadas: %s' % fm.separar_milhares(n)
    label_linhas_adicionadas = ttk.Label(
        frame, text=form_linhas_adicionadas(0))
    label_linhas_adicionadas.grid(
        row=0, column=0, sticky='nwes', padx=10, pady=10)
    frame.rowconfigure(0, weight=0)
    frame.columnconfigure(0, weight=1)

    # vamos armazenar na lista a seguir uma string com o motivo de invalidez para cada linha inválida
    linhas_invalidas = []
    def form_linhas_invalidas(
    ): return '  Linhas inválidas: %s  ' % fm.separar_milhares(len(linhas_invalidas))
    painel_linhas_invalidas = ttk.LabelFrame(
        frame, text=form_linhas_invalidas(), padding=10)
    painel_linhas_invalidas.grid(
        row=1, column=0, sticky='nwes', padx=10, pady=10)
    frame.rowconfigure(1, weight=1)

    # interface gráfica para mostrar as linhas inválidas
    treeview_linhas_invalidas = ttk.Treeview(painel_linhas_invalidas, columns=(
        'Arquivo', 'Linha', 'Motivo'), selectmode='none')
    treeview_linhas_invalidas.column('#0', width=20, stretch=0)
    for i, coluna in enumerate(('Arquivo', 'Linha', 'Motivo')):
        treeview_linhas_invalidas.heading(i, text=coluna)
        treeview_linhas_invalidas.column(
            i, width=0, minwidth=len(coluna)*15, anchor='center')
    treeview_linhas_invalidas.bind(
        '<Motion>', lambda ev: util.last_separator(ev, treeview_linhas_invalidas))
    treeview_linhas_invalidas.bind(
        '<1>', lambda ev: util.last_separator(ev, treeview_linhas_invalidas))
    treeview_linhas_invalidas.grid(row=0, column=0, sticky='nsew')
    painel_linhas_invalidas.rowconfigure(0, weight=1)
    painel_linhas_invalidas.columnconfigure(0, weight=1)

    linhas_invalidas_scroller_v = ttk.Scrollbar(
        painel_linhas_invalidas, orient='vertical', command=treeview_linhas_invalidas.yview)
    linhas_invalidas_scroller_v.grid(row=0, column=1, sticky='ns')

    linhas_invalidas_scroller_h = ttk.Scrollbar(
        painel_linhas_invalidas, orient='horizontal', command=treeview_linhas_invalidas.xview)
    linhas_invalidas_scroller_h.grid(row=1, column=0, sticky='ew')

    treeview_linhas_invalidas['yscrollcommand'] = linhas_invalidas_scroller_v.set
    treeview_linhas_invalidas['xscrollcommand'] = linhas_invalidas_scroller_h.set

    for endereco in enderecos:
        # vamos ler cada arquivo selecionado pelo usuário
        # ntpath.basename pega o nome do arquivo
        nome_arquivo = ntpath.basename(endereco)
        treeview_linhas_invalidas.insert(
            '', 'end', nome_arquivo, open=True, values=(nome_arquivo, '-', '-'))
        treeview_linhas_invalidas.detach(nome_arquivo)
        with open(endereco, 'r') as arquivo_reservas:
            for i, linha in enumerate(arquivo_reservas, 1):
                if linha.startswith(('-', '\n')):
                    # ignoramos os comentários (linhas começando com -)
                    # e linhas vazias
                    continue
                dados_linha = csv_to_linha(app, linha)
                if dados_linha.validez:
                    # a linha é válida, então vamos adicioná-la
                    indice = len(linhas)
                    # a seguir, adicionamos a linha à interface gráfica
                    adicionar_linha(app, indice, dados_linha, data_atual)
                    # e atualizamos as variáveis que estão monitorando esse processo
                    linhas.append(
                        [estado.linhas_entradas[dados_linha.id], list()])
                    ids_linhas.append(dados_linha.id)
                    label_linhas_adicionadas['text'] = form_linhas_adicionadas(
                        len(linhas))
                    continue
                # aqui, a linha é inválida
                # seu motivo se encontra em dados_linha.texto
                # pois dados_linha é o wrapper retornado por csv_to_linha

                # (((((linha[:-1] if linha[-1] == '\n' else linha))))) significa que
                # vamos ignorar a quebra de linha, se ela existir no final da linha, para que a explicação
                # da invalidez ocupe apenas uma linha
                linhas_invalidas.append(
                    '%s, --> %s\n' % (linha[:-1] if linha[-1] == '\n' else linha, dados_linha.texto))
                painel_linhas_invalidas['text'] = form_linhas_invalidas()

                treeview_linhas_invalidas.insert(
                    nome_arquivo, 'end', values=('-', i, dados_linha.texto))
        if len(linhas_invalidas) > 0:
            treeview_linhas_invalidas.reattach(nome_arquivo, '', 'end')
            heading = '- Linha, --> Motivo\n'
            botao_exportar = ttk.Button(painel_linhas_invalidas, text='Exportar Linhas Inválidas',
                                        command=lambda: exportar_linhas_invalidas(linhas_invalidas, heading, janela))
            botao_exportar.grid(row=2, column=0, sticky='we')

    if linhas != []:
        # coloca o foco sobre a primeira linha
        app.linhas.see(ids_linhas[0])
        # seleciona todas as linhas adicionadas pela importação
        app.linhas.selection_set(ids_linhas)
        monitoradas.historico_redo.clear()
        monitoradas.historico_undo.append(['add', linhas])


def exportar_linhas(app):
    '''
        Exporta os dados sobre as linhas no caminho escolhido pelo usuário.
    '''
    # O explorador de arquivos pede ao usuário um caminho para onde os dados devem ser exportados
    endereco = filedialog.asksaveasfilename(title='Exportar Linhas', defaultextension='.csv', filetypes=[
                                            ('csv', '*.csv'), ('txt', '*.txt'), ('todos', '*')])

    linhas = set()
    linhas_ordenadas = []
    # vamos exportar as linhas selecionados pelo usuário
    selecao = app.linhas.selection()
    if len(selecao) == 0:
        # se o usuário não selecionou nenhuma linha, iremos exportar todas
        linhas_ordenadas = app.linhas.get_children()

    for item in selecao:
        parent = app.linhas.parent(item)
        if parent == '':
            # aqui, o parent do item selecionado é '', o que significa que item é uma linha
            linhas.add(item)
            linhas_ordenadas.append(item)
        elif parent not in linhas:
            # aqui, o parent do item selecionado não é '' (o que significa que item é um ônibus)
            # então vamos considerar a linha desse ônibus (parent) em vez do ônibus (item).
            linhas.add(parent)
            linhas_ordenadas.append(parent)

    # vamos criar um arquivo no caminho especificado
    with open(endereco, 'w') as arquivo_reservas:
        arquivo_reservas.write(
            '- Destino, Horário (hora:minuto), Assentos Disponíveis (total), Valor Inteira\n\n')
        for linha in linhas_ordenadas:
            # e escrevemos uma linha de texto para cada linha de ônibus
            arquivo_reservas.write(linha_to_csv(linha))
