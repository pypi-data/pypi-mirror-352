from jinja2 import Environment, FileSystemLoader
from importlib.resources import files
template_path = files('sv_simpleparser.Templates')


def gen_instance(module_obj):

    module_name = module_obj.name
    port_lst = [port.name for port in module_obj.port_lst]
    param_lst = [param.name for param in module_obj.param_lst]
    param_lst = [param.name for param in module_obj.param_lst]

    environment = Environment(loader=FileSystemLoader(template_path))

    if param_lst:
        inst_temp = environment.get_template("instance_with_param_template")

        instance_file = inst_temp.render(module_name=module_name,
                                         param_list=param_lst,
                                         port_list=port_lst)
    else:
        inst_temp = environment.get_template("instance_template")

        instance_file = inst_temp.render(module_name=module_name,
                                         port_list=port_lst)

    return instance_file


def remove_slashes_and_newlines(input_string):
    # Replace '//' with an empty string
    result = input_string.replace('//', '')
    # Replace '\n' with an empty string
    result = result.replace('\n', '')
    return result.strip()


def gen_markdown_table(module_obj):

    port_lst = [port.name for port in module_obj.port_lst]
    width_lst = [rf'{port.width[:-1]}]' if port.width is not None else '1' for port in module_obj.port_lst]
    comment_lst = [remove_slashes_and_newlines(port.comment[0]) if port.comment is not None else '' for port in module_obj.port_lst]
    direction_lst = [port.direction for port in module_obj.port_lst]

    environment = Environment(loader=FileSystemLoader(template_path))

    inst_temp = environment.get_template("markdown_table_template")

    instance_file = inst_temp.render(port_lst=port_lst,
                                     direction_lst=direction_lst,
                                     comment_lst=comment_lst,
                                     width_lst=width_lst)

    return instance_file
