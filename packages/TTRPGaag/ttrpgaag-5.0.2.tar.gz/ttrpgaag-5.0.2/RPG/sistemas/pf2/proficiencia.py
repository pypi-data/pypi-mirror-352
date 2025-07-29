from .data import Data


def calcula_proficiencia(proficiencia: str, nivel: int = 1, sem_nivel: bool = False) -> int:
    """
    Calcula o modificador da proficiência baseado no nível da proficiência
    :param proficiencia: qual a proficiência
    :param nivel: qual o nível do personagem
    :param sem_nivel: se utiliza a regra de proficiency without level
    :return: o valor final da proficiência
    """
    proficiencia = proficiencia.lower()
    nivel = nivel if not sem_nivel else 0

    if proficiencia == 'untrained':
        return 0

    return Data.proficiency[proficiencia] + nivel


def aumenta_proficiencia(atual: str = 'untrained') -> str:
    lista = list(Data.proficiency.keys())
    indice_atual = lista.index(atual) + 1
    indice_atual = indice_atual if indice_atual < len(lista) - 1 else -1

    return lista[indice_atual]
