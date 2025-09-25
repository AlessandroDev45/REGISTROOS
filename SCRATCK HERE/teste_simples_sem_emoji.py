#!/usr/bin/env python3
"""
Teste simples sem emojis para verificar se o subprocess funciona
"""

import sys

def main():
    if len(sys.argv) > 1:
        numero_os = sys.argv[1]
        print(f"Testando OS: {numero_os}")
        print("Script funcionando sem emojis")
        print("Resultado: [{'OS': '000020203', 'CLIENTE': 'TESTE', 'DESCRIÇÃO': 'TESTE MOTOR'}]")
    else:
        print("Nenhum argumento fornecido")

if __name__ == "__main__":
    main()
