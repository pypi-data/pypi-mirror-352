import os
import math

def limpa_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def soma(x, y):
    return x + y

def subtracao(x, y):
    return x - y

def multiplicacao(x, y):
    return x * y

def divisao(x, y):
    return x / y

def potencia(x, y):
    return math.pow(x, y)

def raiz_quadrada(x):
    return math.sqrt(x)