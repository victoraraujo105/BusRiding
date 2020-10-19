'''
	Esse módulo declara a função main, que inicializa toda a aplicação.
	Não há motivos para importar esse módulo, ele deve ser executado.
	Por exemplo, na linha de comando: "py ./main.py"
'''

import datetime as dt
import tkinter as tk
import ttk
from tkinter import messagebox



def main():
	'''
		Início da aplicação. Inicia a interface gráfica e executa o mainloop,
		responsável por manter o programa rodando, recebendo eventos do usuário (cliques, etc.).
		O uso de imports dentro de main é necessário para evitar dependências circulares.
	'''
	print('OK')
	root = tk.Tk()

	# precisa de root (instância de Tk)
	import monitoradas
	from mount import App

	# esse objeto carrega as informações dos widgets da interface gráfica
	app = App(root)

	# precisam de root completamente definido
	import date

	# calculamos um intervalo para que o relógio seja atualizado no próximo minuto exato
	data_atual = monitoradas.data_atual
	d = data_atual.replace(second=0, microsecond=0) - data_atual
	interval = round(60_000 + d.total_seconds()*1_000)

	# aqui, programamos a execução de atualizar_relogio para o próximo minuto
	# atualizar_relogio irá chamar a si mesmo a cada minuto
	app.root.after(interval, lambda: date.atualizar_relogio(app))
	app.root.mainloop()

# garantimos que main não executará caso alguém importe esse módulo main.py
# ninguém atualmente importa main.py, mas aqui fica já a garantia.
# main vai executar ao ser chamado na linha de comando "py ./main.py"
# a variável __name__ é inicializada pelo interpretador
if __name__ == '__main__':
	main()
	