# 🧮 calculadora_python

Uma calculadora simples desenvolvida em Python, com funcionalidades básicas como soma, subtração, multiplicação, divisão e porcentagem. Inclui também um menu interativo de terminal para facilitar o uso.

---

## 📦 Instalação

Você pode instalar o pacote diretamente do PyPI com:

```bash
pip install calculadora-python
```

## 🚀 Funcionalidades
### O pacote calculadora_python oferece:

somar(a, b) — Soma dois números

subtrair(a, b) — Subtrai o segundo número do primeiro

multiplicar(a, b) — Multiplica dois números

dividir(a, b) — Divide o primeiro número pelo segundo

porcentagem(valor, percentual) — Retorna o valor percentual

main() — Inicia o menu interativo no terminal

## 💻 Exemplo de uso
from calculadora_python import somar, dividir, main

print(somar(10, 5))      # 15
print(dividir(20, 4))    # 5.0

Inicia a interface de menu no terminal
main()

## 📁 Organização do pacote
calculadora_python/<br>
├── __init__.py<br>
├── operacoes.py<br>
└── menu_operacoes.py<br>

operacoes.py: Contém as funções matemáticas.<br>

menu_operacoes.py: Contém a lógica de entrada de dados e o menu interativo.<br>

__init__.py: Reexporta as funções principais para facilitar o uso do pacote.


## 🐍 Requisitos
Python >= 3.8

## 👤 Autor
Juan da Mata<br>
📧 juandamata200@hotmail.com<br>
[🔗 GitHub - JuanDaMata](https://github.com/JuanDaMata/)

## 📝License
[MIT](https://opensource.org/licenses/MIT)