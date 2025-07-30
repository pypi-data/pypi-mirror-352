def clientes_inadimplentes(lista_devedores):
    lista_inadimplentes = []
    for devedores in lista_devedores:
        cpf, valor, dias = devedores
        if valor >= 1000 and dias > 20:
            lista_inadimplentes.append(cpf)
    
    return lista_inadimplentes
