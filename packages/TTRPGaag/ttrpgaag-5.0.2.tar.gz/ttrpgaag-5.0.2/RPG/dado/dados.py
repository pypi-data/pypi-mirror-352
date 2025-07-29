from .dado import Dado


# ==================================================================
# Funções para rolamento de _dados padrão, mas já retornando o total
# ==================================================================
def d4(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d4** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 4).total


def d6(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d6** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 6).total


def d8(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d8** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 8).total


def d10(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d10** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 10).total


def d12(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d12** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 12).total


def d20(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d20** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 20).total


def d66():
    """
    Rola um d66 e retorna o resultado somado. O d66 é gerado jogando dois d6 separadamente, um para a dezena e outro
    para a unidade
    :return: valor total do rolamento
    """
    dezena = d6() * 10
    unidade = d6()
    total = dezena + unidade

    return total


def d100(qtd: int = 1) -> int:
    """
    Rola uma quantidade de **d100** e retorna a soma deles
    :param qtd: a quantidade de dados, 1 por padrão
    :return: valor total do rolamento
    """
    return Dado(qtd, 100).total
