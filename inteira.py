'''
    Define o comportamento do widget que contém o texto do preço da inteira.
'''

import monitoradas
import constantes as cte

# índice 0 se refere ao valor mínimo 3.00
# índice 1 se refere à 3.01
# índice i se refere à (3 + i / 100)
# ou a fórmula equivalente: (300 + i) / 100 ou então 2 * (300 + i) / 200
# Como o valor máximo é 6.00, o maior índice é 300
# Note que esse cálculo se refere à passagem inteira,
# para a meia, vamos dividir por 2, ou seja: 1 * (300 + i) / 200
# para passagem gratuita: o valor será 0
# Assim, veja que (passagem * (300 + i) / 200) é o valor desejado,
# indicamos passagem=2 para a inteira, passagem=1 para a meia e passagem=0 para a gratuita.
inteira_termo = lambda n, passagem=2: '%.2f' % (passagem*(300 + n)/200)
centavos = lambda n, passagem=2: passagem*(300 + n)/2

def incrementar_inteira(evento=None):
    '''
        Aumenta o preço da inteira para o próximo valor decimal válido que possui 0 na casa da centena:
        3.60 -> 3.70
        3.61 -> 3.70
        3.62 -> 3.70
        3.69 -> 3.70
        3.70 -> 3.80
        Caso especial:
        6.00 -> 3.00 (por causa de monitoradas.indice_inteira %= 310)
    '''
    atualizar_inteira()
    monitoradas.indice_inteira += 10 - monitoradas.indice_inteira % 10
    monitoradas.indice_inteira %= 310    # indice_maximo + incremento --> constantes
    inteira = monitoradas.inteira
    inteira.set(inteira_termo(monitoradas.indice_inteira))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'

def decrementar_inteira(evento=None):
    '''
        Diminui o preço da inteira para o próximo valor decimal válido que possui 0 na casa da centena:
        3.60 -> 3.50
        3.59 -> 3.50
        3.58 -> 3.50
        3.57 -> 3.50
        3.50 -> 3.40
        Caso especial:
        3.00 -> 6.00 (por causa de monitoradas.indice_inteira %= 310)
    '''
    atualizar_inteira()
    monitoradas.indice_inteira -= 10 - (-monitoradas.indice_inteira) % 10
    monitoradas.indice_inteira %= 310
    inteira = monitoradas.inteira
    inteira.set(inteira_termo(monitoradas.indice_inteira))
    # o valor de retorno sinaliza ao sistema de eventos que a propagação desse evento deve parar aqui
    return 'break'

def atualizar_inteira(evento=None):
    '''
        Valida o texto digitado pelo usuário no campo "inteira".
        - Se o texto é um preço válido (número de 3.00 a 6.00), o valor do widget é alterado para o preço digitado.
        - Caso contrário, ignoramos o texto digitado pelo usuário e voltamos ao texto anterior,
        utilizando o índice salvo em monitoradas.indice_inteira.
    '''
    inteira = monitoradas.inteira
    chave = 'inteira_invalida'
    try:
        inteira_nova = float(inteira.get())
        if 3 <= inteira_nova <= 6:
            # o valor digitado pelo usuário é válido!
            # vamos alterar então o valor do índice monitorado
            # essa transformação é a função inversa de inteira_termo
            # já que temos um preço e queremos saber qual índice se refere a esse preço
            # por exemplo,
            # preço 3.00 -> índice 0
            # preço 3.01 -> índice 1
            monitoradas.indice_inteira = round((inteira_nova - 3)*100)
            chave = None
    except ValueError:
        pass
    inteira.set(inteira_termo(monitoradas.indice_inteira))
    return chave
