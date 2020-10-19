'''
    Define funções responsáveis pelo controle interno da aplicação (ações, por exemplo)
'''

import datetime as dt
import monitoradas
import constantes as cte
import mount


def update_action(app, action=None):
    '''
        Atualiza o texto que indica a ação sendo realizada pela aplicação ('Edição', 'Remoção', etc.).
        Esse texto aparece no canto inferior direito e é removido após 1 segundo se não forem
        realizadas outras ações.
    '''
    current_time = dt.datetime.today()
    if action is None:
        if current_time - monitoradas.last_call >= dt.timedelta(seconds=1):
            monitoradas.cur_action.set('')
        return
    monitoradas.last_call = current_time
    monitoradas.cur_action.set(cte.ACTIONS.get(action, action))
    # Após 1 segundo, rechamaremos essa função sem especificar uma action no argumento
    # o que fará o texto sumir caso nenhuma outra ação tenha ocorrido durante esse 1 segundo.
    app.root.after(1000, lambda *_: update_action(app))
