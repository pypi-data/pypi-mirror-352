from .calculos import soma, subtracao, multiplicacao, divisao, potencia, raiz_quadrada, limpa_terminal
import time

def menu():
    while True:
        escolha = int()
        try:
            print('(1) - Adição')
            print('(2) - Subtração')
            print('(3) - Multiplicação')
            print('(4) - Divisão')
            print('(5) - Potência')
            print('(6) - Raiz Quadrada')
            print('(7) - Sair')
            escolha = int(input('Digite a Opção que deseja realizar: '))
        except ValueError:
            print('É aceito apenas Números!')

        limpa_terminal()

        try:
            if escolha == 7:
                break
            if escolha == 1:
                x = int(input('Digite o Primeiro Número: '))
                y = int(input('Digite o Segundo Número: '))
                print('\n')
                print(f'O Resultado da Soma é {soma(x, y)}')
                time.sleep(2)
                limpa_terminal()
            if escolha == 2:
                x = int(input('Digite o Primeiro Número: '))
                y = int(input('Digite o Segundo Número: '))
                print('\n')
                print(f'O Resultado da Subtração é {subtracao(x, y)}')
                time.sleep(2)
                limpa_terminal()
            if escolha == 3:
                x = int(input('Digite o Primeiro Número: '))
                y = int(input('Digite o Segundo Número: '))
                print('\n')
                print(f'O Resultado da Multiplicação é {multiplicacao(x, y)}')
                time.sleep(2)
                limpa_terminal()
            if escolha == 4:
                x = int(input('Digite o Primeiro Número: '))
                y = int(input('Digite o Segundo Número: '))
                print('\n')
                print(f'O Resultado da Soma é {divisao(x, y)}')
                time.sleep(2)
                limpa_terminal()
            if escolha == 5:
                x = int(input('Digite o Número que Deseja ser para ser a base: '))
                y = int(input('Digite o Número para ser a potência: '))
                print('\n')
                print(f'O Resultado da Potência é {potencia(x, y)}')
                time.sleep(2)
                limpa_terminal()
            if escolha == 6:
                x = int(input('Digite o Número que Deseja saber a raiz quadrada: '))
                print('\n')
                print(f'O Resultado da Potência é {raiz_quadrada(x)}')
                time.sleep(2)
                limpa_terminal()
        except ValueError:
            print('É aceito apenas Números!')
            limpa_terminal()
        
if __name__ == '__main__':
    menu()