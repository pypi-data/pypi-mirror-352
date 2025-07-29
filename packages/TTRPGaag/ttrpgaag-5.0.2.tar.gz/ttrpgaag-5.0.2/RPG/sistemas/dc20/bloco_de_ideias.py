from rolamentos import Rolamento, RolamentoAtaque


def checa_critico(dado_rolado: int):
    # 1 sucesso crítico
    # -1 falha crítica
    if dado_rolado == 20:
        return 1
    
    if dado_rolado == 1:
        return -1

    return None


def checa_teste(dado_rolado: int, modificador: int, dc: int = 15):
    rolamento = dado_rolado + modificador


teste = (6, 1, 1, 0, 0, 1)

alcance = teste[0:3]
print(alcance, sum(alcance))

# ! AQUI



# ! TESTE
teste = Rolamento(4, 14, 1)
ataque = RolamentoAtaque()