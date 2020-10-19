# BusRiding

Para iniciar o programa, execute o script do arquivo `main.py`, usando Python 3 (de preferência a última versão). 

À primeira execução do programa, serão carregados dados persistentes ilustrativos.

![Dados ilustrativos](https://imgur.com/download/S3OJ09n/)

Entretanto, caso o usuário deseje uma execução "limpa", sem nenhuma informação pré-cadastrada; pode especificar um arquivo vazio como argumento do script (EX: `$ python3 main.py .`); ou até mesmo um outro arquivo `.busridingdata` produzido ao final da execução de alguma sessão anterior.

![Execução limpa](https://imgur.com/download/hGxtUme/)
***
## HOTKEYS

* **CTRL** - Segurar permite selecionar múltiplos itens.
* **SHIFT** - Permite a seleção de todos os itens entre um item previamente selecionado e o item atualmente selecionado.
* **CTRL+Z** - Desfaz uma ação (se essa ação suporta undo).
* **CTRL+SHIFT+Z** - Refaz uma ação desfeita com CTRL+Z.
* **DELETE** - Deleta os itens selecionados.
* **SORTING** - Em diversas planilhas, as entradas podem ser ordenadas clicando na coluna pela qual se deseja ordenar as informações.
Para inverter a ordem, basta pressionar novamente a coluna. Não é recomendado a ordenação quando o número de entradas é muito grande (superior aos 10.000), visto que o tempo de espera pode se tornar um incômodo. Podem ser desfeitas e refeitas (salvas no histórico).

![Ordenar entradas](https://imgur.com/download/vE1zkAR/)
***
## ABA LINHAS

Para cadastrar uma linha digite ou escolha entradas nos campos de informação e pressione o botão `[Adicionar]`.

Ônibus com esses atributos, dentro do intervalo de datas de partida válidas, são adicionados automaticamente como instâncias dessa linha (podem ser visualizados clicando no dropdown).

> O intervalo de datas de partida válidas, do horário atual do sistema até os próximos 15 dias, é atualizado ao completar de cada minuto. Ônibus que saíram desse intervalo são deletados da planilha, de forma que o usuário é impedido de fazer qualquer reserva neles (possíveis reservas em ônibus partidos ainda podem ser visualizadas na aba **Reservas**); ônibus que agora fazem parte do intervalo, são adicionados, com todos os assentos disponíveis.  

![Adicionar linha](https://imgur.com/download/B7yODZr/)

Os campos correspondem, respectivamente, ao destino da linha, horário de partida, máximo de assentos livres (metade da capacidade total, devido à pandemia; isto é, se uma linha possui **60** assentos livres, seus ônibus têm **120** lugares) e preço da passagem inteira.
Caso entrada inválida seja entrada, um popup será exibido explicando o motivo da invalidez e dando instruções ao usuário.

![Entradas inválidas](https://imgur.com/download/SHIcTaA/)

A entrada do campo dos destinos é inválida apenas se for espaço em branco. Todo texto digitado nele, ao perder o foco (clicando fora da caixinha ou tab, por exemplo) é formatado automaticante para Title Case. Hífens e vírgulas são trocados por espaços, visto que a separação das informações nas ids (códigos) das linhas e no arquivo exportado (.csv) é feita com esses símbolos.

![Formatação destino](https://imgur.com/download/0kY85qM/)

Os destinos registrados podem ser consultados e selecionados clicando no dropdown (setinha para baixo), contêm por padrão todos os campi da UFC.
Novos destinos podem ser adicionados escrevendo textos válidos e clicando no botão `[+]`.
Para remover um destino registrado, selecione-o e pressione o botão `[-]`.
Removidos todos os destinos, o botão `[-]` não produz nenhum efeito.
Um novo destino válido é registrado automaticamente ao se adicionar linha que o possua.
Ao clicar Enter, se o texto não estiver registrado (usando o botão `[+]` ou adicionando linha com esse destino) a entrada anterior do campo é restaurada.
Os destinos registrados são informação persistente.

O spinbox das horas e minutos pode receber horários direto do teclado, desde que siga o formato **HH:MM** e seja hora válida (horas em `[0, 23]` e minutos em `[0, 59]`). Espaços em branco em torno da entrada são ignorados e removidos. Se a entrada não seguir o formato especificado, é revertida para a anterior.
As setinhas incrementam ou decrementam o tempo exibido em 1 minuto.

O spinbox dos assentos livres, que representa o número máximo de passageiros em distanciamento social, como o das horas, permite que se digite a entrada; aceita apenas inteiros entre 2 e 60; esse intervalo é obtido pelo número máximo de fileiras dos ônibus (30 por padrão).
Cada fileira possui 4 assentos, em virtude da pandemia apenas 2 são utilizáveis. Admitindo que um ônibus não pode ter menos que 1 fileira, obtemos a sequência de possíveis assentos livres `{2, 4, 6, 8, ..., 56, 58, 60}`. Entradas ímpares no intervalo `[3, 59]` são arredondadas para o próximo par (53 --> 54).
Entradas não numéricas ou fora do intervalo `[2, 60]` são ignoradas e a entrada anterior é restaurada.

O spinbox que representa o preço da passagem inteira aceita entrada digitada e deve ser float em `[3.00, 6.00]`. O passo das setinhas por padrão é de 10 centavos (.1), e arredonda a entrada prévia para o próximo (ou anterior) múltiplo de .1 (EX: inc: 3.59 --> 3.60; dec: 3.59 -- > 3.50).
Entradas inválidas são revertidas para a anterior.

O botão `[Remover]` desabilita a visualização (não os descadastra) de itens (linhas ou ônibus).
Caso nenhum item seja selecionado, o primeiro da planilha é desabilitado.
Quando pressionado continuamente, após um delay de milisegundos, ele remove consecutivamente as entradas do topo até ser soltado (released). 
Caso haja itens selecionados, eles serão desabilitados.

![Remoções consecutivas](https://imgur.com/download/cFenUYU/)

Pressionar a tecla **DELETE** tem efeito parecido, entretanto, apenas itens selecionados são desabilitados.
Nada acontece quando a seleção é vazia ou se a tecla for segurada.

Devido o registro de eventos em um histórico, certas ações podem ser desfeitas.
A desfeitura da remoção de itens pressionando **CTRL+Z** é uma das maneiras de reabilitá-los.
Ações também podem ser refeitas pressionando **CTRL+SHIFT+Z**.

Diferentemente da remoção, que apenas desabilita a visualização de itens (eles continuam armazenados internamente) a desfeitura de um cadastro (feito na adição ou geração de linhas), de fato descadastra a(s) linha(s), permitindo que qualquer uma destas, talvez com assentos e inteira diferentes, seja recadastrada.

Vale mencionar que o identificador de uma linha (seu código) é determinado apenas pelo destino e hora de partida (medida que se fez necessária pelo recurso de ler reservas de arquivos). Isso significa que linhas idênticas exceto pelos assentos e inteira não podem coexistir.

O botão `[Editar]` altera os atributos de uma única linha selecionada que não possui reservas.
Caso seleção seja vazia, maior que 1 ou ônibus, popup de alerta é exibido.
Caso linha possua reservas, diferente popup de alerta é exibido.

Caso novos atributos resultem numa linha já existente:

    caso esta seja a própria linha selecionada:
        caso atributos sejam idênticos:
            nada acontece
        senão:
            linha é atualizada com novos atributos
    senão:
        caso linha com novos atributos esteja desabilitada:
            é ofererecida ao usuário a opção de reabilitar a linha e descadastrar a linha selecionada.
        senão:
            popup de alerta é exibido
senão:

    linha selecionada é deletada e linha com novos atributos é cadastrada no mesmo índice e selecionada.

O botão `[Adicionar]`, como já mencionado, cadastra linha com atributos dos campos (caso válidos).
Seja nova_linha a linha a ser adicionada.

Caso nova_linha já exista:
    
    caso nova_linha seja visível (não removida):
        o foco é direcionado para essa linha.
    senão:
        é ofererecida ao usuário a opção de reabilitar a linha.
senão:
    
    nova_linha é adicionada.

O botão `[Relatório]` abre uma janela com informações sobre as linhas, com informações distribuídas em 3 seções:

### SEÇÃO ARRECADAÇÃO
* Total arrecadado (entre todas as linhas)
* Valor arrecadado por linha

### SEÇÃO DISTRIBUIÇÃO DE PASSAGENS
* Total de passageiros (entre todas as linhas)
* Porcentagem de passageiros utilizando passagem **INTEIRA**
* Porcentagem de passageiros utilizando passagem **MEIA**
* Porcentagem de passageiros utilizando passagem **GRATUITA**

### SEÇÃO OCUPAÇÃO
Ocupação média é o percentual da quantidade de assentos utilizados sobre o total de assentos disponíveis.
* Ocupação média entre todas as linhas
* Ocupação média por dia da semana por linha (estilo matriz)

Existem quatro checkboxes (caixinhas de marcar) nessa janela, o primeiro, o checkbox mestre, controla todos os demais, que por sua vez correspondem a cada seção de informações.

As seções selecionadas são exibidas e suas informações incluídas no arquivo de texto (.txt) exportado.
Caso uma seção seja desselecionada, ela é minimizada.
Caso nenhuma seção esteja selecionada, o botão exportar é desabilitado, visto que não faz sentido exportar um relatório vazio.

O botão `[Exportar]` na janela Relatório permite a seleção, pelo usuário, de um caminho para onde exportar os dados do relatório (como arquivo .txt).

![Exportar relatório](https://imgur.com/download/hpjerIC/)

O botão `[Importar]` (na aba Linhas) permite a seleção, pelo usuário, de um caminho de onde importar dados sobre linhas (arquivo .csv).
As informações lidas de cada linha seguem o seguinte formato:
`Destino, Horário (hora:minuto), Assentos Disponíveis (total), Valor Inteira`

Exemplo de uma linha válida (caso não haja sido cadastrada):
`Sobral, 09:57, 48, 4.87`

Ao final, é gerado um relatório com explicações sobre linhas inválidas, além da quantidade de linhas adicionadas. Esse relatório pode ser exportado, contém as linhas inválidas brutas, na ordem em que foram lidas, cada uma seguida de `, --> <motivo invalidez>'`.
Exemplo:
`Sobral, 29:57, 48, 4.87, --> horário não segue formato previsto: 13:18`

O botão `[Exportar]` (na aba Linhas) permite a escolha, pelo usuário, de um caminho para onde exportar os dados sobre linhas selecionadas (como arquivo .csv). Caso nenhuma linha tenha sido selecionada, todas elas são exportadas. Caso ônibus tenham sido selecionados, as linhas das quais fazem parte são exportadas. Seguem o mesmo formato dos arquivos importados e podem ser lidos através do botão importar.


O botão `[Gerar]` abre uma janela que permite a geração de linhas aleatórias.
Pelo usuário, é possível escolher:
* A quantidade de linhas a serem geradas aleatoriamente, um valor em `[1, quantidade de linhas possíveis]`, inicialmente 50.
> A quantidade de linhas possíveis é obtida pelo produto entre a quantidade de destinos cadastrados e 1440 (quantidade de horários possíveis, minutos num dia) subtraído pela quantidade de linhas cadastradas.
* Se as linhas devem ser ocupadas aleatoriamente ou não.
Caso o usuário escolha gerar linhas ocupadas, são atribuídos pesos aos tipos de passagem:
    * Inteira: peso 3
    * Meia: peso 2
    * Gratuita: peso 1
    
De modo que o valor esperado de passagens inteiras aleatoriamente reservadas é 3/6 do total de passagens reservadas por esse processo de geração,
e o valor esperado da porcentagem de passagens meias e gratuitas são respectivamente 2/6 e 1/6, para que a distribuição pareça mais natural.

![Gerar linhas](https://imgur.com/download/C8CjaYv/)

O botão `[Reservar]` permite realizar reservas no ônibus selecionado.
Caso seleção não possua apenas um único ônibus, um popup de alerta é exibido.
Caso contrário, é criada a janela "Reservar Assento", que exibe os assentos do ônibus.
    * Assentos verdes são livres
    * Assentos vermelhos foram reservados com passagem **INTEIRA**
    * Assentos laranjas foram reservados com passagem **MEIA**
    * Assentos azuis foram reservados com passagem **GRATUITA**

Assentos não visíveis não são selecionáveis por causa das restrições da pandemia.
O usuário tem a opção de escolher qual número de assento e qual tipo de passagem deseja reservar
Apenas assentos livres são selecionáveis.

Caso nenhum assento do ônibus selecionado tenha sido reservado, todos os assentos (dobro do total de passageiros) serão oferecidos para a livre escolha da primeira reserva. A partir do primeiro assento reservado, são bloqueados assentos nas diagonais complementares às paralelas à do assento reservado, de forma a assegurar o distânciamento social:

![Primeira reserva](https://imgur.com/download/8gfduqa/)

***
## ABA RESERVAS

O botão `[Devolver]` permite a devolução das reservas selecionadas. É a operação inversa de `[Reservar]`.

O botão `[Importar]` permite a importação dos dados sobre as reservas no caminho especificado pelo usuário.
O arquivo importado possui extensão .csv e cada linha representa uma reserva. Seguem o formato:
`Destino, Partida (dia/mês/ano hora:minuto), Assento, Passagem (inteira, meia ou gratuita)`
O campo da passagem é opcional, sendo por padrão inteira.

Exemplo de formato válido:
```
Sobral, 20/10/20 09:57, 22, meia
Benfica, 29/10/20 02:16, 14
```

Após a importação, é exibido um relatório com informações sobre linhas inválidas, explicando o motivo pelo qual não foi possível realizar a reserva para cada reserva inválida. Pode ser exportado, como o das linhas importadas.

O botão `[Exportar]` permite a exportação dos dados sobre as reservas selecionadas no caminho especificado pelo usuário.
Caso nenhuma reserva tenha sido selecionada, todas são exportadas.
O arquivo exportado possui extensão `.csv` e cada linha representa uma reserva. Segue a mesma forma dos arquivos de reservas importadas e podem ser usados para carregar reservas.
