import click


@click.command()
@click.argument('numero', type=float)
def main(numero):
    """Calcula o número passado mais 3000"""
    resultado = numero + 3000
    click.echo(f"O resultado de {numero} + 3000 é: {resultado}")


if __name__ == '__main__':
    main()
