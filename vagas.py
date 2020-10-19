'''
    Define o comportamento do widget que contém o texto da quantidade de vagas.
'''

import constantes as cte
import monitoradas

vagas = monitoradas.vagas
# índice 0 se refere ao valor mínimo da quantidade de vagas: 2
# índice 1 se refere à quantidade 4
# índice 2 se refere à quantidade 6
# indice i se refere à (2 + 2 * i)


def vagas_termo(n): return 2 + 2*n


def incrementar_vagas(evento=None):
    '''
        Aumenta a quantidade de vagas em 2.
    '''
    atualizar_vagas()
    monitoradas.indice_vagas += 1
    monitoradas.indice_vagas %= cte.MAXIMO_NUMERO_DE_FILEIRAS
    vagas.set(vagas_termo(monitoradas.indice_vagas))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'


def decrementar_vagas(evento=None):
    '''
        Diminui a quantidade de vagas em 2.
    '''
    atualizar_vagas()
    monitoradas.indice_vagas -= 1
    monitoradas.indice_vagas %= cte.MAXIMO_NUMERO_DE_FILEIRAS
    vagas.set(vagas_termo(monitoradas.indice_vagas))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'


def atualizar_vagas(evento=None):
    chave = 'vagas_invalida'
    try:
        vagas_novo = int(vagas.get())
        if vagas_novo in range(2, 2*cte.MAXIMO_NUMERO_DE_FILEIRAS+1):
            # o valor digitado pelo usuário é válido!
            # vamos alterar então o valor do índice monitorado
            # essa transformação é a função inversa de vagas_termo
            # já que temos uma quantidade de vagas e queremos saber qual índice se refere a essa vaga
            # por exemplo,
            # 2 vagas -> índice 0
            # 4 vagas -> índice 1
            monitoradas.indice_vagas = (vagas_novo - 1)//2
            chave = None
    except ValueError:
        pass
    vagas.set(vagas_termo(monitoradas.indice_vagas))
    return chave
