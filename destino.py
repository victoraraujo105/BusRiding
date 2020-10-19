import estado
import formatar as fm
import monitoradas


def atualizar_destino(evento=None):
    chave = None
    destino = monitoradas.destino
    nova_entrada = fm.form_destino(destino.get())
    if nova_entrada == '':
        chave = 'destino_invalido'
    destino.set(nova_entrada)
    return chave


def validar_destino(evento=None):
    '''
        Valida o texto digitado pelo usuário no campo "destino".
        Atualmente é utilizado quando o usuário altera o campo destino e pressiona ENTER.
        - Se o texto é um destino válido (somos lenientes com a escrita, então "PICI", "   PicI"
        são interpretados como "Pici"), o valor do widget é alterado para o destino digitado.
        - Caso contrário, ignoramos o texto digitado pelo usuário e voltamos ao texto anterior.
    '''
    destino = monitoradas.destino
    # iremos transformar "    palAVra " em "Palavra"
    # para aceitar várias strings que representam o mesmo destino mas que foram escritas pelo usuário
    # de maneira um pouco diferente.
    entrada = fm.form_destino(destino.get())
    if entrada in estado.destinos:
        # atualmente, destino possui o texto digitado pelo usuário, mas queremos padronizar conforme nossa formatação
        # então, iremos alterar o texto do widget para o valor formatado
        destino.set(entrada)
        monitoradas.texto_anterior = entrada
        return
    # aqui, a entrada não é válida! ignoramos o valor que o usuário digitou no widget e voltemos ao texto anterior
    destino.set(monitoradas.texto_anterior)


def add_destino(app, evento=None):
    texto = monitoradas.destino.get()
    if texto != '' and texto not in estado.destinos:
        estado.destinos.append(texto)
        estado.linhas_possiveis.update({(texto, t) for t in range(1440)})
        estado.destinos.sort()
        app.entrada_destino['values'] = estado.destinos


def rmv_destino(app, evento=None):
    destino = monitoradas.destino
    texto = destino.get()
    if texto in estado.destinos:
        i = estado.destinos.index(texto)
        del estado.destinos[i]
        estado.linhas_possiveis.difference_update(
            {(texto, t) for t in range(1440)})
        app.entrada_destino['values'] = estado.destinos
    if estado.destinos == []:
        destino.set('')
    else:
        destino.set(estado.destinos[0])
    monitoradas.texto_anterior = destino.get()
