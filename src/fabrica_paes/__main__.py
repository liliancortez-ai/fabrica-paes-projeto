"""Ponto de entrada para ``python -m fabrica_paes``.

O módulo delega à mesma CLI registrada como comando instalado; argumentos e
códigos de saída são, portanto, os mesmos nas duas formas de execução.
"""

from fabrica_paes.cli import main


if __name__ == "__main__":
    main()
