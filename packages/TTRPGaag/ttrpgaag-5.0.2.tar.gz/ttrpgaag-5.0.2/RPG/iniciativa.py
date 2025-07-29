def ordena_iniciativa(iniciativas: dict[str:int:float|str], maior_ganha: bool = True) -> list[str]:
    """
    :param iniciativas: dicionário com nome do personagem e o valor rolado
    :param maior_ganha: True por padrão, determina se quem vence a iniciativa é o maior valor
    :return: lista dos nomes ordenadas por quem vence a iniciativa
    """
    iniciativas = sorted(iniciativas.items(), key=lambda x: x[1], reverse=maior_ganha)
    return [personagem[0] for personagem in iniciativas]


if __name__ == '__main__':
    from dado.dados import d20

    iniciativa = {
        'PC 1': d20() + 2.5,
        'PC 2': d20() + 1,
        'PC 3': d20() + 3,
        'NPC 1': d20() - 1,
        'NPC 2': d20() + 5
    }

    print(iniciativa)
    print(ordena_iniciativa(iniciativa))
    print(ordena_iniciativa({'nome': 2, 'nome 2': 10}))
