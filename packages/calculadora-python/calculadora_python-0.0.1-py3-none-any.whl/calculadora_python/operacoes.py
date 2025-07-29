def somar(numeros):
    return sum(numeros)

def subtrair(numeros):
    resultado = numeros[0]
    for numero in numeros[1:]:
        resultado -= numero
    return resultado

def multiplicar(numeros):
    resultado = 1
    for numero in numeros:
        resultado *= numero
    return resultado

def dividir(numeros):
    resultado = numeros[0]
    for numero in numeros[1:]:
        if numero == 0:
            return "Não pode ser realizada a divisão por zero!"
        resultado /= numero
    return resultado

def porcentagem(numeros):
    if len(numeros) != 2:
        return "A porcentagem precisa de exatamente 2 números (valor e % que quer tirar do valor)."
    valor, percentual = numeros
    return (valor * percentual) / 100
