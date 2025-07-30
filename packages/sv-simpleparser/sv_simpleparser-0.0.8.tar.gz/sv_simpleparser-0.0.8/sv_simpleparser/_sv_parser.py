import pathlib
from ._hdl import SystemVerilogLexer
from dataclasses import dataclass
import logging
from pygments.token import Token, Comment, Operator, Keyword, Name, String, Number, \
    Punctuation, Whitespace
from ._token import Module
from typing import List, Dict, Optional, Union

__all__ = ["parse_sv", "print_token"]

logging.basicConfig(
    level=logging.DEBUG,  # or INFO to reduce output
    format='%(levelname)s:%(name)s:%(message)s'
)


@dataclass
class Port:
    """Represents a port in a SystemVerilog module.

    Attributes:
        direction: Port direction ('input', 'output', 'inout')
        ptype: Port type ('wire', 'reg', 'logic', etc.)
        name: Name of the port
        width: Bus width specification (e.g., '[7:0]')
        comment: List of associated comments
    """
    direction: str
    ptype: Optional[str] = None
    name: Optional[str] = None
    width: Optional[str] = None
    comment: Optional[List[str]] = None


@dataclass
class Param:
    """Represents a parameter in a SystemVerilog module.

    Attributes:
        ptype: Parameter type ('integer', 'real', 'string', etc.)
        name: Name of the parameter
        width: Bus width specification if applicable
        comment: List of associated comments
    """
    ptype: Optional[str] = None
    name: Optional[str] = None
    width: Optional[str] = None
    comment: Optional[List[str]] = None


@dataclass
class ModInstance:
    """Represents an instance of a module within another module.

    Attributes:
        name: Instance name
        module: Name of the module being instantiated
        connections: List of port connections in order of declaration
    """
    name: Optional[str] = None
    module: Optional[str] = None
    connections: Optional[List[str]] = None

    def proc_tokens(self, token, string):

        if token == Module.Body.Instance.Name:
            self.name = string
        elif token == Module.Body.Instance.Connections:
            self.connections = string


@dataclass
class PortDeclaration:
    """Represents a port declaration block in SystemVerilog.

    Attributes:
        direction: Port direction ('input', 'output', 'inout')
        ptype: Port type ('wire', 'reg', 'logic', etc.)
        name: List of port names in this declaration
        width: Bus width specification if applicable
        comment: List of associated comments
    """
    direction: str
    ptype: Optional[str] = None
    name: Optional[List[str]] = None
    width: Optional[str] = None
    comment: Optional[List[str]] = None

    def proc_tokens(self, token, string):
        '''Processes Module.Port tokens and extract data'''
        if token == Module.Port.PortDirection:
            self.direction = string
        elif token == Module.Port.PortType:
            self.ptype = string
        elif token == Module.Port.PortName:
            if self.name is None:
                self.name = [string]
            else:
                self.name.append(string)
        elif token == Module.Port.PortWidth:
            self.width = string
        elif token == Module.Port.Comment:
            if self.comment is None:
                self.comment = [string]
            else:
                self.comment.append(string)


@dataclass
class ParamDeclaration:
    """Represents a parameter declaration block in SystemVerilog.

    Attributes:
        ptype: Parameter type ('integer', 'real', etc.)
        name: List of parameter names in this declaration
        width: Bus width specification if applicable
        comment: List of associated comments
    """
    ptype: Optional[str] = None
    name: Optional[List[str]] = None
    width: Optional[str] = None
    comment: Optional[List[str]] = None

    def proc_tokens(self, token, string):
        '''Processes Module.Param tokens and extract data'''
        if token == Module.Param.ParamType:
            self.ptype = string
        elif token == Module.Param.ParamName:
            if self.name is None:
                self.name = [string]
            else:
                self.name.append(string)
        elif token == Module.Param.ParamWidth:
            self.width = string
        elif token == Module.Param.Comment:
            if self.comment is None:
                self.comment = [string]
            else:
                self.comment.append(string)


class SvModule:
    """Represents a complete SystemVerilog module with all its components.

    Attributes:
        name: Name of the module
        port_lst: List of Port objects
        param_lst: List of Param objects
        inst_dict: Dictionary of module instances (instance name -> module)
        port_decl: List of PortDeclaration objects
        param_decl: List of ParamDeclaration objects
        inst_decl: List of instance declarations
    """

    def __init__(self):
        self.name: Optional[str] = None
        self.port_lst: List[Port] = []
        self.param_lst: List[Param] = []
        self.inst_dict: Dict[str, str] = {}

        self.port_decl: List[PortDeclaration] = []
        self.param_decl: List[ParamDeclaration] = []
        self.inst_decl: List[ModInstance] = []


    def _gen_port_lst(self):
        for decl in self.port_decl:
            for name in decl.name:
                port = Port(name=name, direction=decl.direction, ptype=decl.ptype,
                            width=decl.width, comment=decl.comment)
                self.port_lst.append(port)

    def _gen_param_lst(self):
        for decl in self.param_decl:
            for name in decl.name:
                param = Param(name=name, ptype=decl.ptype, width=decl.width,
                              comment=decl.comment)
                self.param_lst.append(param)

    def _gen_inst_dict(self):
        for decl in self.inst_decl:
            self.inst_dict[decl.name] = decl.module

    def proc_tokens(self, token, string):

        # Capture a new port declaration object if input/output keywords are found
        if token[:2] == ('Module', 'Port'):
            if token[-1] == ('PortDirection'):
                self.port_decl.append(PortDeclaration(direction=string))
            else:
                self.port_decl[-1].proc_tokens(token, string)

        # Capture parameters, when Module.Param tokens are found
        elif token[:2] == ('Module', 'Param'):
            if token is Module.Param:
                self.param_decl.append(ParamDeclaration())
            else:
                self.param_decl[-1].proc_tokens(token, string)

        # Capture Modules
        elif token[:2] == ('Module', 'ModuleName'):
            self.name = string

        # Capture instances
        elif token[:3] == ('Module', 'Body', 'Instance'):
            if token == Module.Body.Instance.Module:
                self.inst_decl.append(ModInstance(module=string))
            else:
                self.inst_decl[-1].proc_tokens(token, string)

    def __str__(self):
        output = []

        # Module name
        output.append(f"Module: {self.name}\n")

        # Parameters
        if self.param_lst:
            output.append("Parameters:")
            for param in self.param_lst:
                param_info = [
                    f"  {param.name}",
                    f"type={param.ptype}" if param.ptype else "",
                    f"width={param.width}" if param.width else "",
                    f"comment={param.comment}" if param.comment else ""
                ]
                output.append(" ".join(filter(None, param_info)))
            output.append("")

        # Parameter Declarations
        if self.param_decl:
            output.append("Parameter Declarations:")
            for decl in self.param_decl:
                decl_info = [
                    f"  {', '.join(decl.name)}",
                    f"type={decl.ptype}" if decl.ptype else "",
                    f"width={decl.width}" if decl.width else "",
                    f"comment={decl.comment}" if decl.comment else ""
                ]
                output.append(" ".join(filter(None, decl_info)))
            output.append("")

        # Ports
        if self.port_lst:
            output.append("Ports:")
            for port in self.port_lst:
                port_info = [
                    f"  {port.direction} {port.name}",
                    f"type={port.ptype}" if port.ptype else "",
                    f"width={port.width}" if port.width else "",
                    f"comment={port.comment}" if port.comment else ""
                ]
                output.append(" ".join(filter(None, port_info)))
            output.append("")

        # Port Declarations
        if self.port_decl:
            output.append("Port Declarations:")
            for decl in self.port_decl:
                decl_info = [
                    f"  {decl.direction} {', '.join(decl.name)}",
                    f"type={decl.ptype}" if decl.ptype else "",
                    f"width={decl.width}" if decl.width else "",
                    f"comment={decl.comment}" if decl.comment else ""
                ]
                output.append(" ".join(filter(None, decl_info)))
            output.append("")

        # Instances
        if self.inst_dict:
            output.append("Instances:")
            for inst_name, inst in self.inst_dict.items():
                output.append(f"  {inst_name} ({inst.module})")
                if inst.connections:
                    output.append("    Connections:")
                    for conn in inst.connections:
                        output.append(f"      {conn}")
            output.append("")

        return "\n".join(output)


def parse_sv(file_path: pathlib.Path):
    '''Parse SystemVerilog

    Parses a SystemVerilog file and returns a list of objects of SvModule class

    Parameters
    ----------

    file_path: Union[str, pathlib.Path]
        Path to the SystemVerilog file.
    '''

    if not isinstance(file_path, pathlib.Path):
        file_path = pathlib.Path(file_path)

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    with file_path.open(mode='r') as fid:
        file_content = fid.read()

    lexer = SystemVerilogLexer()
    module_lst = []
    for token, string in lexer.get_tokens(file_content):

        # New module was found
        if token == Module.ModuleStart:
            module_lst.append(SvModule())
        elif 'Module' in token[:]:
            module_lst[-1].proc_tokens(token, string)

    for mod in module_lst:
        mod._gen_port_lst()
        mod._gen_param_lst()
        mod._gen_inst_dict()

    return module_lst


def print_token(file_path: pathlib.Path):
    '''Parse SystemVerilog

    Parses a SystemVerilog file and returns a list of objects of SvModule class

    Parameters
    ----------

    file_path: Union[str, pathlib.Path]
        Path to the SystemVerilog file.
    '''

    if not isinstance(file_path, pathlib.Path):
        file_path = pathlib.Path(file_path)

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    with file_path.open(mode='r') as fid:
        file_content = fid.read()

    lexer = SystemVerilogLexer()
    mod_lst = []
    for token, string in lexer.get_tokens(file_content):

        print(token, string)

        # New module was found
        if token == Module.ModuleStart:
            mod_lst.append(SvModule())
        elif 'Module' in token[:]:
            mod_lst[-1].proc_tokens(token, string)

    for mod in mod_lst:
        mod._gen_port_lst()
        mod._gen_param_lst()

    import pprint
    for mod in mod_lst:
        print(f'Module name: {mod.name}')
        pprint.pprint(mod.port_lst)
        pprint.pprint(mod.param_lst)
        pprint.pprint(mod.inst_decl)


if __name__ == '__main__':
    import pprint

    file_path = pathlib.Path('../tests/svfiles_examples/adder.sv')

    mod_lst = parse_sv(file_path)

    for mod in mod_lst:
        print(f'Module name: {mod.name}')
        pprint.pprint(mod.port_lst)
        pprint.pprint(mod.param_lst)
