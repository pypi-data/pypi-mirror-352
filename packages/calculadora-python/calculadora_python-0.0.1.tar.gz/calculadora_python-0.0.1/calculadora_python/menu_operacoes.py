from operacoes import somar, subtrair, multiplicar, dividir, porcentagem

def obter_numeros():
    numeros = input("Digite os números separados por espaço: ")
    try:
        return [float(numero) for numero in numeros.strip().split()]
    except ValueError:
        print("Inválida! Por favor, digite apenas números.")
        return obter_numeros()

def menu():
    menu_operacoes = """\n
========== CALCULADORA ==========

[so] Somar
[su] Subtrair
[m] Multiplicar
[d] Dividir
[p] Porcentagem
[s] Sair

=> """
    return input(menu_operacoes)

def main():
    while True:
        opcao = menu()

        if opcao == "s":
            break
        
        elif opcao == "so":
            numeros = obter_numeros()
            if len(numeros) < 2:
                print("Por favor, digite pelo menos dois números.")
                continue
            resultado = somar(numeros)
            print(f"Resultado: {resultado}")

        elif opcao == "su":
            numeros = obter_numeros()
            if len(numeros) < 2:
                print("Por favor, digite pelo menos dois números.")
                continue
            resultado = subtrair(numeros)
            print(f"Resultado: {resultado}")

        elif opcao == "m":
            numeros = obter_numeros()
            if len(numeros) < 2:
                print("Por favor, digite pelo menos dois números.")
                continue
            resultado = multiplicar(numeros)
            print(f"Resultado: {resultado}")

        elif opcao == "d":
            numeros = obter_numeros()
            if len(numeros) < 2:
                print("Por favor, digite pelo menos dois números.")
                continue
            resultado = dividir(numeros)
            print(f"Resultado: {resultado}")

        elif opcao == "p":
            numeros = obter_numeros()
            if len(numeros) != 2:
                print("Para porcentagem, você precisa digitar exatamente dois números (valor e percentual).")
                continue
            resultado = porcentagem(numeros)
            print(f"Resultado: {resultado}")

        else:
            print("Operação inválida, por favor selecione a operação desejada novamente.")

main()