'''
    Define uma classe App que serve unicamente pra inicializar um objeto com
    várias instâncias de componentes em suas propriedades, que fazem parte da interface gráfica.
    O único uso atualmente é em main.py:

    app = App(root)
'''

import tkinter as tk
import ttk
import constantes as cte
import monitoradas
import util
import destino as dest
import date
import estado
import inteira as it
import vagas as vg
import history as hst
import gerar
import formatar as fm
import arquivos as arq
import relatorio as rel


class App(object):
    def __init__(self, root):
        '''
            Inicializa a interface gráfica e armazena as instâncias dos componentes
            nesse objeto (self).

            O argumento root é uma instância de Tk, a janela principal da aplicação.

            O manager grid é utilizado para o posicionamento dos componentes, sendo especificado
            posições de linhas e colunas para os filhos de um componente.


            ::: self.component.grid(row=1, column=2, sticky='n')
            significa que component será posicionado na LINHA 1 e COLUNA 2 em relação ao seu master
            e alinhado ao NORTE ('n'), ou seja, o componente "gruda" no topo.
            sticky='ns' significa que o componente "gruda" no NORTE e no SUL, se esticando verticalmente.
            Outros sticky possuem significado com lógica similar.

            ::: self.component.columnconfigure(0, weight=1)
            ::: self.component.columnconfigure(1, weight=1)
            ::: self.component.columnconfigure(2, weight=1)
            significa que os filhos de component nas colunas 0, 1 e 2 possuem o mesmo PESO, ou seja,
            ocupam a mesma quantidade de espaço

            ::: self.component.bind('<Evento>', funcao)
            significa que o event handler "funcao" será associado (bind) ao evento <Evento>.
            assim, sempre que <Evento> for recebido por component, funcao irá executar
        '''
        root.minsize(
            *cte.TAMANHO_DA_JANELA_PRINCIPAL)  # tamanho mínimo da janela principal
        # título, aparece na porção superior do programa
        root.title(cte.TITULO)
        # permitimos o acesso por self.root (ou app.root, fora dessa função)
        self.root = root
        # ícone
        self.estilo = ttk.Style()
        self.estilo.configure(
            'inteira.TLabel', background='#e30000', foreground='#fff')
        self.estilo.configure(
            'meia.TLabel', background='#eb7100', foreground='#fff')
        self.estilo.configure(
            'gratuita.TLabel', background='#095f9c', foreground='#fff')
        self.estilo.configure('available.TLabel',
                              background='#07de00', foreground='#fff')
        self.estilo.configure(
            'selected.TLabel', background='#fff', foreground='#005')

        self.frame = ttk.Frame()
        self.frame.pack(fill='both', expand=True)

        # crio um objeto Notebook em root (janela principal), que permite a divisão de uma janela em abas
        self.abas = ttk.Notebook(self.frame)

        # a primeira aba, onde o usuário poderá manipular as entradas de linhas de ônibus
        self.aba_linhas = ttk.Frame(self.abas, padding=12, name='aba_linhas')
        self.aba_linhas.pack()  # peço ao módulo para exibir a aba usando o método pack

        self.linhas = ttk.Treeview(
            self.aba_linhas, columns=cte.COLUNAS_LINHAS, selectmode='extended', name='linhas')
        self.linhas.column('#0', width=20, stretch=0)
        for i, coluna in enumerate(cte.COLUNAS_LINHAS):
            self.linhas.heading(i, text=coluna.title(
            ), command=lambda col=i: util.treeview_sort_column(self, self.linhas, col, False))
            self.linhas.column(i, width=0, minwidth=len(
                coluna)*15, anchor='center')
        self.linhas.bind(
            '<Motion>', lambda ev: util.last_separator(ev, self.linhas))
        self.linhas.bind(
            '<1>', lambda ev: util.last_separator(ev, self.linhas))

        self.linhas_scroller_v = ttk.Scrollbar(
            self.aba_linhas, orient='vertical', command=self.linhas.yview)
        self.linhas_scroller_h = ttk.Scrollbar(
            self.aba_linhas, orient='horizontal', command=self.linhas.xview)

        self.linhas['yscrollcommand'] = self.linhas_scroller_v.set
        self.linhas['xscrollcommand'] = self.linhas_scroller_h.set

        # gridding - aba_linhas
        self.linhas.grid(row=0, column=0, sticky='nsew')
        self.linhas_scroller_v.grid(row=0, column=1, sticky='ens')
        self.linhas_scroller_h.grid(row=1, column=0, sticky='sew')

        self.aba_reservas = ttk.Frame(
            self.abas, padding=12, name='aba_reservas')
        self.aba_reservas.pack()

        self.reservas = ttk.Treeview(self.aba_reservas, columns=cte.COLUNAS_RESERVAS,
                                     show='headings', selectmode='extended', name='reservas')
        for i, coluna in enumerate(cte.COLUNAS_RESERVAS):
            self.reservas.heading(i, text=coluna.title(
            ), command=lambda col=i: util.treeview_sort_column(self, self.reservas, col, False))
            self.reservas.column(i, width=0, minwidth=len(
                coluna)*15, anchor='center')
        self.reservas.bind(
            '<Motion>', lambda ev: util.last_separator(ev, self.reservas))
        self.reservas.bind(
            '<1>', lambda ev: util.last_separator(ev, self.reservas))

        self.reservas_scroller_v = ttk.Scrollbar(
            self.aba_reservas, orient='vertical', command=self.reservas.yview)
        self.reservas_scroller_h = ttk.Scrollbar(
            self.aba_reservas, orient='horizontal', command=self.reservas.xview)

        self.reservas['yscrollcommand'] = self.reservas_scroller_v.set
        self.reservas['xscrollcommand'] = self.reservas_scroller_h.set

        # gridding - aba_reservas
        self.reservas.grid(row=0, column=0, sticky='nsew')
        self.reservas_scroller_v.grid(row=0, column=1, sticky='ens')
        self.reservas_scroller_h.grid(row=1, column=0, sticky='new')

        self.painel_botoes_reservas = ttk.Frame(self.aba_reservas)
        self.painel_botoes_reservas.grid(
            row=2, column=0, columnspan=1, sticky='nesw', pady=(12, 6))

        self.botao_devolver = ttk.Button(
            self.painel_botoes_reservas, command=lambda: util.devolver(self), text='Devolver')
        self.botao_devolver.grid(row=0, column=0, sticky='we')

        self.botao_importar_reservas = ttk.Button(
            self.painel_botoes_reservas, command=lambda: arq.importar_reservas(self), text='Importar')
        self.botao_importar_reservas.grid(row=0, column=1, sticky='we')

        self.botao_exportar_reservas = ttk.Button(
            self.painel_botoes_reservas, command=lambda: arq.exportar_reservas(self), text='Exportar')
        self.botao_exportar_reservas.grid(row=0, column=2, sticky='we')

        for i in range(3):
            self.painel_botoes_reservas.columnconfigure(i, weight=1)

        self.painel_entrada = ttk.Frame(self.aba_linhas)
        self.painel_entrada.columnconfigure(0, weight=1)
        self.painel_entrada.columnconfigure(1, weight=1)
        self.painel_entrada.columnconfigure(2, weight=1)
        self.painel_entrada.columnconfigure(3, weight=1)

        self.painel_destino = ttk.Frame(self.painel_entrada)
        self.painel_destino.grid(row=0, column=0, sticky='w', padx=0)

        self.painel_partida = ttk.Frame(self.painel_entrada)
        self.painel_partida.grid(row=0, column=1, sticky='we', padx=0)

        self.entrada_destino = ttk.Combobox(
            self.painel_destino, justify='center', textvariable=monitoradas.destino, values=estado.destinos, width=15)
        self.entrada_destino.bind('<FocusOut>', dest.atualizar_destino)
        self.entrada_destino.bind('<Return>', dest.validar_destino)
        self.entrada_destino.grid(row=0, column=0, sticky='ew', padx=0)

        self.botao_add_destino = ttk.Button(
            self.painel_destino, command=lambda: dest.add_destino(self), text='+', width=2)
        self.botao_add_destino.grid(row=0, column=2, sticky='w')

        self.botao_rmv_destino = ttk.Button(
            self.painel_destino, command=lambda: dest.rmv_destino(self), text='-', width=2)
        self.botao_rmv_destino.grid(row=0, column=1, sticky='w')

        self.spin_hora = ttk.Spinbox(
            self.painel_entrada, textvariable=monitoradas.tempo_formatado, justify='center', width=6)
        self.spin_hora.bind(
            '<<Increment>>', lambda e: date.increment(self, cte.MIN))
        self.spin_hora.bind(
            '<<Decrement>>', lambda e: date.decrement(self, cte.MIN))
        self.spin_hora.bind('<Return>', lambda e: date.update(self))
        self.spin_hora.grid(row=0, column=1, sticky='', padx=(0, 30))

        self.spin_vagas = ttk.Spinbox(
            self.painel_entrada, textvariable=monitoradas.vagas, justify='center', width=4)
        self.spin_vagas.bind('<<Increment>>', vg.incrementar_vagas)
        self.spin_vagas.bind('<<Decrement>>', vg.decrementar_vagas)
        self.spin_vagas.bind('<Return>', vg.atualizar_vagas)
        self.spin_vagas.grid(row=0, column=2, sticky='', padx=(30, 0))

        self.painel_inteira = ttk.Frame(self.painel_entrada)
        self.painel_inteira.columnconfigure(0, weight=1)
        self.painel_inteira.columnconfigure(1, weight=1)
        self.painel_inteira.grid(row=0, column=3, sticky='e', padx=0)

        self.reais = ttk.Label(self.painel_inteira,
                               text='R$', width=4, anchor='center')
        self.reais.grid(row=0, column=0, sticky='e')

        self.spin_inteira = ttk.Spinbox(
            self.painel_inteira, textvariable=monitoradas.inteira, justify='center', width=5)
        self.spin_inteira.bind('<<Increment>>', it.incrementar_inteira)
        self.spin_inteira.bind('<<Decrement>>', it.decrementar_inteira)
        self.spin_inteira.bind('<Return>', it.atualizar_inteira)
        self.spin_inteira.grid(row=0, column=1, sticky='ew', padx=0)

        self.painel_botoes = ttk.Frame(self.painel_entrada)
        self.painel_botoes.columnconfigure(0, weight=1)
        self.painel_botoes.columnconfigure(1, weight=1)
        self.painel_botoes.columnconfigure(2, weight=1)
        self.painel_botoes.grid(row=1, column=0, columnspan=4, sticky='ew')

        self.root.bind('<Control-z>', lambda ev: hst.undo(self, ev))
        self.root.bind('<Control-Shift-KeyPress-Z>',
                       lambda ev: hst.redo(self, ev))
        self.root.bind('<Control-a>', lambda ev: util.select_all(self, ev))
        self.root.bind('<Delete>', lambda ev: util.del_selecao(self))
        self.root.bind('<Control-w>', lambda *_: quit())
        self.root.protocol("WM_DELETE_WINDOW", lambda: estado.persistir(self))

        self.botao_remover = ttk.Button(
            self.painel_botoes, text='Remover')  # set width? maxwidth
        self.botao_remover.bind(
            '<ButtonPress>', lambda ev: util.remover_linhas(self, ev))
        self.botao_remover.bind('<ButtonRelease>', util.released)
        self.botao_remover.grid(row=0, column=0, sticky='we')

        self.botao_editar = ttk.Button(
            self.painel_botoes, text='Editar', command=lambda: util.editar_linha(self))
        self.botao_editar.grid(row=0, column=1, sticky='we')

        self.botao_adicionar = ttk.Button(
            self.painel_botoes, text='Adicionar', command=lambda: util.adicionar_linha(self))
        self.botao_adicionar.grid(row=0, column=2, sticky='we')

        self.botao_reservar = ttk.Button(
            self.painel_botoes, text='Reservar', command=lambda: util.reservar_viagem(self))
        self.botao_reservar.grid(row=1, column=3, sticky='we', padx=(10, 0))
        self.painel_botoes.columnconfigure(3, weight=1)

        self.botao_gerar = ttk.Button(
            self.painel_botoes, text='Gerar', command=lambda: gerar.gerar_linhas(self))
        self.botao_gerar.grid(row=0, column=3, sticky='we', padx=(10, 0))

        self.botao_relatorio = ttk.Button(
            self.painel_botoes, text='Relatório', command=lambda: rel.exibir_relatorio(self))
        self.botao_relatorio.grid(row=1, column=0, sticky='we')

        self.botao_importar_linhas = ttk.Button(
            self.painel_botoes, text='Importar', command=lambda: arq.importar_linhas(self))
        self.botao_importar_linhas.grid(row=1, column=1, sticky='we')

        self.botao_exportar_linhas = ttk.Button(
            self.painel_botoes, text='Exportar', command=lambda: arq.exportar_linhas(self))
        self.botao_exportar_linhas.grid(row=1, column=2, sticky='we')

        self.painel_contadores = ttk.Frame(self.frame)

        self.contador_linhas = ttk.Label(self.painel_contadores, text=fm.form_cont_linhas(
            len(estado.linhas_visiveis)), anchor='sw')
        self.contador_linhas.grid(row=0, column=0, sticky='sw')

        self.contador_onibus = ttk.Label(self.painel_contadores, text=fm.form_cont_onibus(
            len(monitoradas.onibus_visiveis)), anchor='sw')
        self.contador_onibus.grid(row=0, column=1, sticky='s')

        self.contador_reservas = ttk.Label(
            self.painel_contadores, text=fm.form_cont_reservas(len(estado.reservas)), anchor='sw')
        self.contador_reservas.grid(row=0, column=2, sticky='s')

        self.label_action = ttk.Label(
            self.painel_contadores, textvariable=monitoradas.cur_action, anchor='w', width=10)
        self.label_action.grid(row=0, column=3, sticky='se')

        for j in range(4):
            self.painel_contadores.columnconfigure(j, weight=1)

        self.painel_entrada.rowconfigure(0, weight=1)
        self.painel_entrada.rowconfigure(1, weight=1)
        self.painel_entrada.rowconfigure(2, weight=1)
        self.painel_entrada.grid(row=2, column=0, sticky='nsew')

        self.aba_linhas.columnconfigure(0, weight=2000)
        self.aba_linhas.rowconfigure(0, weight=100)
        self.aba_linhas.columnconfigure(1, weight=1)
        self.aba_linhas.rowconfigure(1, weight=1)
        self.aba_linhas.rowconfigure(2, minsize=70, weight=0)

        self.aba_reservas.columnconfigure(0, weight=2000)
        self.aba_reservas.columnconfigure(1, weight=1)
        self.aba_reservas.rowconfigure(0, weight=1)

        self.abas.add(self.aba_linhas, text='Linhas')
        self.abas.add(self.aba_reservas, text='Reservas')
        self.abas.grid(row=0, column=0, sticky='nesw')

        self.painel_contadores.grid(
            row=1, column=0, sticky='we', pady=5, padx=15)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        if estado.data is not None:
            util.povoar_treeviews(self)
