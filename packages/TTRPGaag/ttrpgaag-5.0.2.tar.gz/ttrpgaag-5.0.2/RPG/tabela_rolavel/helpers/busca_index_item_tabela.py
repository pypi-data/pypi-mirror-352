def busca_index_item_tabela(tabela, valor) -> int:
    for index, linha in enumerate(tabela):
        if linha[0][0] <= valor <= linha[0][1]:
            return index

    return None