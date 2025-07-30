import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
def gen_sv_instance(file_path):
    '''Parses an SystemVerilog file and returns a instance of the module'''

    from ._sv_parser import parse_sv
    from ._gen_templates import gen_instance

    mod_lst = parse_sv(file_path)

    for mod_obj in mod_lst:
        instance = gen_instance(mod_obj)
        print(instance)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
def gen_io_table(file_path):
    '''Generates an I/O table from an SV file'''

    from ._sv_parser import parse_sv
    from ._gen_templates import gen_markdown_table

    mod_lst = parse_sv(file_path)

    for mod_obj in mod_lst:
        table = gen_markdown_table(mod_obj)
        print(table)
