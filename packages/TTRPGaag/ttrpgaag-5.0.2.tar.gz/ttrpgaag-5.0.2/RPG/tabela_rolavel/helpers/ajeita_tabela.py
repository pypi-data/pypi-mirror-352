def ordena_dicionario(tabela: dict):
    numeros = sorted(tabela)
    return {chave: tabela[chave] for chave in numeros}


def ajeita_tabela(tabela: list[tuple, str]) -> list[tuple, str]:
    """
    Pega uma _tabela que tenha itens com apenas um rolamento e coloca na tupla como valor mínimo e máximo
    :param tabela: a tabela a ser arrumada
    :return: lista
    """
    nova_tabela = []

    for item in tabela:
        alcance_rolamento = item[0]
        resultado_rolamento = item[1]

        if type(alcance_rolamento) is not tuple:
            alcance_rolamento = (int(alcance_rolamento), int(alcance_rolamento))
        else:
            alcance_rolamento = (int(alcance_rolamento[0]), alcance_rolamento[1])

        linha = (alcance_rolamento, resultado_rolamento)
        nova_tabela.append(linha)


    return nova_tabela


def converte_lista_para_dicionario(tabela):
    tabela = ajeita_tabela(tabela)
    dicionario = {}
    for linha in tabela:
        dicionario[linha[0][1]] = linha[1]

    return dicionario