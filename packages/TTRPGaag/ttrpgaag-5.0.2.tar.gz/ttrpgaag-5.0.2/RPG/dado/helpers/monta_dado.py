def monta_dado(string_dado: str) -> dict:
    separando_elementos = string_dado.lower().split("d")
    separando_elementos[0] = separando_elementos[0] if separando_elementos[0] else '1'

    quantidade, faces = map(int, separando_elementos)

    return {"quantidade": quantidade, "faces": faces}