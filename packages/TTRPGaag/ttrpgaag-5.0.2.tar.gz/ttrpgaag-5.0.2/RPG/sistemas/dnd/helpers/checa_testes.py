from ..data.mecanicas import resultado_rolagem_teste, resultado_rolagem_ataque


def checa_teste(rolagem_total, dc):
    resultado = rolagem_total >= dc
    return resultado_rolagem_teste[resultado]


def checa_ataque(rolagem_dado, rolagem_total, ac):
    resultado = rolagem_total >= ac
    resultado = 2 if rolagem_dado == 20 else resultado
    return resultado_rolagem_ataque[resultado]

