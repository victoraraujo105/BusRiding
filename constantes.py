'''
    Define constantes para serem usadas pela aplicação, de maneira a deixar o código mais organizado.
    A convenção do estilo CAIXA_ALTA é utilizada para nomear constantes.
'''

import datetime as dt
from collections import namedtuple

TITULO = 'BusRiding'
TAMANHO_DA_JANELA_PRINCIPAL = (800, 400)
COLUNAS_LINHAS = ('campus', 'partida', 'assentos livres', 'inteira') # nomes das colunas da planilha
COLUNAS_RESERVAS = ('campus', 'partida', 'assento', 'passagem')
DESTINOS_INICIAIS = ['Benfica', 'Pici', 'Porangabuçu', 'Quixadá', 'Russas', 'Sobral']
MAXIMO_NUMERO_DE_FILEIRAS = 30  # inteiro positivo
MAXIMO_NUMERO_DE_DIAS_ATE_RESERVA = 15  # inteiro não negativo
DIA = dt.timedelta(1)
MIN = dt.timedelta(minutes=1)
# Mapeia os nomes de operações (rmv, add, etc...) para
# nomes que aparecerão no canto inferior direito da interface gráfica indicando que tipo de ação está
# sendo realizada. O motivo disso é porque os nomes "Remoção" (e os outros) são arbitrários e susceptíveis de
# serem alterados, já que são um detalhe visual. Esse mapeamento nos permite alterar facilmente o que será
# exibido na tela, sem prejudicar as funções que dependem do nome do evento/ação "rmv".
ACTIONS = { # passar identifiers dicts para o singular
    'rmv':'Remoção',
    'add':'Cadastro',
    'sort':'Ordenação',
    'change':'Edição',
    'book':'Reserva',
    'show': 'Restaurar',
    'refund': 'Devolver',
    'import_reservas': 'Importar' 
}
# Os nomes "add", "rmv", "book" são utilizados no histórico da aplicação como indicadores de eventos,
# e os nomes visíveis ao usuário (canto inferior direito) são definidos por esse mapeamento.
# Já existe ACTIONS, mas ACOES_COMPLEMENTARES é um mapeamento especifíco para quando o usuário está desfazendo um evento.
# Por exemplo, se a ação "add" aparece no histórico porque o usuário cadastrou uma linha, mas o usuário
# emite um CTRL+Z, iremos selecionar o último evento do histórico (add) e iremos realizar seu COMPLEMENTO.
# Nesse caso, um descadastro, e será isso que será mostrado ao usuário na interface gráfica como a ação
# executada por consequência do CTRL+Z.
ACOES_COMPLEMENTARES = {'add':'Descadastro', 'rmv':'Restauração', 'book':'Devolução', 'show': 'Desabilitar', 'refund': 'Reservar', 'import_reservas': 'Devolução'}
# Placeholders que definem o formato do texto
PLACEHOLDER_CONT_LINHAS = 'Linhas: %s'
PLACEHOLDER_CONT_ONIBUS = 'Ônibus: %s'
PLACEHOLDER_CONT_RESERVAS = 'Reservas: %s'
# Conversão e desconversão entre um valor inteiro e o tipo de passagem
INDICE_PASSAGEM = {2: 'inteira', 1: 'meia', 0: 'gratuita'}
PASSAGEM_INDICE = {'inteira': 2, 'meia': 1, 'gratuita': 0}
ESTRUTURA_LINHA = namedtuple('ESTRUTURA_LINHA', ['destino', 'horario', 'fileiras', 'inteira', 'onibus'])
# caminho (relativo) onde estão armazenados os dados persistentes da aplicação
DATA_FILE_PATH = '.busridingdata'