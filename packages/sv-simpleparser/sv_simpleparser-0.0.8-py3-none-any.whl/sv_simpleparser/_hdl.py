"""
    pygments.lexers.hdl
    ~~~~~~~~~~~~~~~~~~~

    Lexers for hardware descriptor languages.

    :copyright: Copyright 2006-2024 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, ExtendedRegexLexer, bygroups, include, words

from ._token import Module, Port

from pygments.token import Token, Comment, Operator, Keyword, Name, String, Number, \
    Punctuation, Whitespace, _TokenType

import re


__all__ = ['SystemVerilogLexer']

punctuation = (r'[()\[\],.;\'$]', Punctuation)

keywords = (words((
    'accept_on', 'alias', 'always', 'always_comb', 'always_ff',
    'always_latch', 'and', 'assert', 'assign', 'assume', 'automatic',
    'before', 'begin', 'bind', 'bins', 'binsof', 'break', 'buf',
    'bufif0', 'bufif1', 'case', 'casex', 'casez', 'cell',
    'checker', 'clocking', 'cmos', 'config',
    'constraint', 'context', 'continue', 'cover', 'covergroup',
    'coverpoint', 'cross', 'deassign', 'default', 'defparam', 'design',
    'disable', 'do', 'edge', 'else', 'end', 'endcase',
    'endchecker', 'endclocking', 'endconfig', 'endfunction',
    'endgenerate', 'endgroup', 'endinterface', 'endmodule', 'endpackage',
    'endprimitive', 'endprogram', 'endproperty', 'endsequence',
    'endspecify', 'endtable', 'endtask', 'enum', 'eventually',
    'expect', 'export', 'extern', 'final', 'first_match',
    'for', 'force', 'foreach', 'forever', 'fork', 'forkjoin', 'function',
    'generate', 'genvar', 'global', 'highz0', 'highz1', 'if', 'iff',
    'ifnone', 'ignore_bins', 'illegal_bins', 'implies', 'implements', 'import',
    'incdir', 'include', 'initial', 'inout', 'input',
    'instance', 'interconnect', 'interface', 'intersect', 'join',
    'join_any', 'join_none', 'large', 'let', 'liblist', 'library',
    'local', 'localparam', 'macromodule', 'matches',
    'medium', 'modport', 'module', 'nand', 'negedge', 'nettype', 'new', 'nexttime',
    'nmos', 'nor', 'noshowcancelled', 'not', 'notif0', 'notif1', 'null',
    'or', 'output', 'package', 'packed', 'parameter', 'pmos', 'posedge',
    'primitive', 'priority', 'program', 'property', 'protected', 'pull0',
    'pull1', 'pulldown', 'pullup', 'pulsestyle_ondetect',
    'pulsestyle_onevent', 'pure', 'rand', 'randc', 'randcase',
    'randsequence', 'rcmos', 'ref',
    'reject_on', 'release', 'repeat', 'restrict', 'return', 'rnmos',
    'rpmos', 'rtran', 'rtranif0', 'rtranif1', 's_always', 's_eventually',
    's_nexttime', 's_until', 's_until_with', 'scalared', 'sequence',
    'showcancelled', 'small', 'soft', 'solve',
    'specify', 'specparam', 'static', 'strong', 'strong0',
    'strong1', 'struct', 'super', 'sync_accept_on',
    'sync_reject_on', 'table', 'tagged', 'task', 'this', 'throughout',
    'timeprecision', 'timeunit', 'tran', 'tranif0', 'tranif1',
    'typedef', 'union', 'unique', 'unique0', 'until',
    'until_with', 'untyped', 'use', 'vectored',
    'virtual', 'wait', 'wait_order', 'weak', 'weak0',
    'weak1', 'while', 'wildcard', 'with', 'within',
    'xnor', 'xor'),
    suffix=r'\b'),
    Keyword)

builtin = (words((
    # Simulation control tasks (20.2)
    '$exit', '$finish', '$stop',
    # Simulation time functions (20.3)
    '$realtime', '$stime', '$time',
    # Timescale tasks (20.4)
    '$printtimescale', '$timeformat',
    # Conversion functions
    '$bitstoreal', '$bitstoshortreal', '$cast', '$itor',
    '$realtobits', '$rtoi', '$shortrealtobits', '$signed',
    '$unsigned',
    # Data query functions (20.6)
    '$bits', '$isunbounded', '$typename',
    # Array query functions (20.7)
    '$dimensions', '$high', '$increment', '$left', '$low', '$right',
    '$size', '$unpacked_dimensions',
    # Math functions (20.8)
    '$acos', '$acosh', '$asin', '$asinh', '$atan', '$atan2',
    '$atanh', '$ceil', '$clog2', '$cos', '$cosh', '$exp', '$floor',
    '$hypot', '$ln', '$log10', '$pow', '$sin', '$sinh', '$sqrt',
    '$tan', '$tanh',
    # Bit vector system functions (20.9)
    '$countbits', '$countones', '$isunknown', '$onehot', '$onehot0',
    # Severity tasks (20.10)
    '$info', '$error', '$fatal', '$warning',
    # Assertion control tasks (20.12)
    '$assertcontrol', '$assertfailoff', '$assertfailon',
    '$assertkill', '$assertnonvacuouson', '$assertoff', '$asserton',
    '$assertpassoff', '$assertpasson', '$assertvacuousoff',
    # Sampled value system functions (20.13)
    '$changed', '$changed_gclk', '$changing_gclk', '$falling_gclk',
    '$fell', '$fell_gclk', '$future_gclk', '$past', '$past_gclk',
    '$rising_gclk', '$rose', '$rose_gclk', '$sampled', '$stable',
    '$stable_gclk', '$steady_gclk',
    # Coverage control functions (20.14)
    '$coverage_control', '$coverage_get', '$coverage_get_max',
    '$coverage_merge', '$coverage_save', '$get_coverage',
    '$load_coverage_db', '$set_coverage_db_name',
    # Probabilistic distribution functions (20.15)
    '$dist_chi_square', '$dist_erlang', '$dist_exponential',
    '$dist_normal', '$dist_poisson', '$dist_t', '$dist_uniform',
    '$random',
    # Stochastic analysis tasks and functions (20.16)
    '$q_add', '$q_exam', '$q_full', '$q_initialize', '$q_remove',
    # PLA modeling tasks (20.17)
    '$async$and$array', '$async$and$plane', '$async$nand$array',
    '$async$nand$plane', '$async$nor$array', '$async$nor$plane',
    '$async$or$array', '$async$or$plane', '$sync$and$array',
    '$sync$and$plane', '$sync$nand$array', '$sync$nand$plane',
    '$sync$nor$array', '$sync$nor$plane', '$sync$or$array',
    '$sync$or$plane',
    # Miscellaneous tasks and functions (20.18)
    '$system',
    # Display tasks (21.2)
    '$display', '$displayb', '$displayh', '$displayo', '$monitor',
    '$monitorb', '$monitorh', '$monitoro', '$monitoroff',
    '$monitoron', '$strobe', '$strobeb', '$strobeh', '$strobeo',
    '$write', '$writeb', '$writeh', '$writeo',
    # File I/O tasks and functions (21.3)
    '$fclose', '$fdisplay', '$fdisplayb', '$fdisplayh',
    '$fdisplayo', '$feof', '$ferror', '$fflush', '$fgetc', '$fgets',
    '$fmonitor', '$fmonitorb', '$fmonitorh', '$fmonitoro', '$fopen',
    '$fread', '$fscanf', '$fseek', '$fstrobe', '$fstrobeb',
    '$fstrobeh', '$fstrobeo', '$ftell', '$fwrite', '$fwriteb',
    '$fwriteh', '$fwriteo', '$rewind', '$sformat', '$sformatf',
    '$sscanf', '$swrite', '$swriteb', '$swriteh', '$swriteo',
    '$ungetc',
    # Memory load tasks (21.4)
    '$readmemb', '$readmemh',
    # Memory dump tasks (21.5)
    '$writememb', '$writememh',
    # Command line input (21.6)
    '$test$plusargs', '$value$plusargs',
    # VCD tasks (21.7)
    '$dumpall', '$dumpfile', '$dumpflush', '$dumplimit', '$dumpoff',
    '$dumpon', '$dumpports', '$dumpportsall', '$dumpportsflush',
    '$dumpportslimit', '$dumpportsoff', '$dumpportson', '$dumpvars',), suffix=r'\b'),
    Name.Builtin)

variable_types = (words((
    # Variable types
    'bit', 'byte', 'chandle', 'const', 'event', 'int', 'integer',
    'logic', 'longint', 'real', 'realtime', 'reg', 'shortint',
    'shortreal', 'signed', 'string', 'time', 'type', 'unsigned',
    'var', 'void',
    # Net types
    'supply0', 'supply1', 'tri', 'triand', 'trior', 'trireg',
    'tri0', 'tri1', 'uwire', 'wand', 'wire', 'wor'),
    suffix=r'\b'),
    Keyword.Type)


class SystemVerilogLexer(RegexLexer):
    """
    Extends verilog lexer to recognise all SystemVerilog keywords from IEEE
    1800-2009 standard.
    """
    name = 'systemverilog'
    aliases = ['systemverilog', 'sv']
    filenames = ['*.sv', '*.svh']
    mimetypes = ['text/x-systemverilog']
    url = 'https://en.wikipedia.org/wiki/SystemVerilog'
    version_added = '1.5'
    flags = re.DOTALL

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'

    tokens = {
        'root': [
            (r'^(\s*)(`define)', bygroups(Whitespace, Comment.Preproc), 'macro'),
            (r'^(\s*)(package)(\s+)', bygroups(Whitespace, Keyword.Namespace, Whitespace)),
            (r'^(\s*)(import)(\s+)', bygroups(Whitespace, Keyword.Namespace, Whitespace), 'import'),
            (r'\s+', Whitespace),
            (r'(\\)(\n)', bygroups(String.Escape, Whitespace)),  # line continuation
            (r'/(\\\n)?/(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'[{}#@]', Punctuation),
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),

            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[lL]?', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),

            (r'([1-9][_0-9]*)?\s*\'[sS]?[bB]\s*[xXzZ?01][_xXzZ?01]*',
             Number.Bin),
            (r'([1-9][_0-9]*)?\s*\'[sS]?[oO]\s*[xXzZ?0-7][_xXzZ?0-7]*',
             Number.Oct),
            (r'([1-9][_0-9]*)?\s*\'[sS]?[dD]\s*[xXzZ?0-9][_xXzZ?0-9]*',
             Number.Integer),
            (r'([1-9][_0-9]*)?\s*\'[sS]?[hH]\s*[xXzZ?0-9a-fA-F][_xXzZ?0-9a-fA-F]*',
             Number.Hex),

            (r'\'[01xXzZ]', Number),
            (r'[0-9][_0-9]*', Number.Integer),

            (r'[~!%^&*+=|?:<>/-]', Operator),
            (words(('inside', 'dist'), suffix=r'\b'), Operator.Word),

            (r'[()\[\],.;\'$]', Punctuation),
            (r'`[a-zA-Z_]\w*', Name.Constant),

            (r'\bmodule\b', Module.ModuleStart, ('module_body', 'module_name')),
            keywords,
            builtin,

            (r'(class)(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword.Declaration, Whitespace, Name.Class)),
            (r'(extends)(\s+)([a-zA-Z_]\w*)',
             bygroups(Keyword.Declaration, Whitespace, Name.Class)),
            (r'(endclass\b)(?:(\s*)(:)(\s*)([a-zA-Z_]\w*))?',
             bygroups(Keyword.Declaration, Whitespace, Punctuation, Whitespace, Name.Class)),
            variable_types,
            (words((
                '`__FILE__', '`__LINE__', '`begin_keywords', '`celldefine',
                '`default_nettype', '`define', '`else', '`elsif', '`end_keywords',
                '`endcelldefine', '`endif', '`ifdef', '`ifndef', '`include',
                '`line', '`nounconnected_drive', '`pragma', '`resetall',
                '`timescale', '`unconnected_drive', '`undef', '`undefineall'),
                suffix=r'\b'),
             Comment.Preproc),
            (r'[a-zA-Z_]\w*:(?!:)', Name.Label),
            (r'\$?[a-zA-Z_]\w*', Name),
            (r'\\(\S+)', Name),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'(\\)(\n)', bygroups(String.Escape, Whitespace)),  # line continuation
            (r'\\', String),  # stray backslash
        ],
        'macro': [
            (r'[^/\n]+', Comment.Preproc),
            (r'/[*](.|\n)*?[*]/', Comment.Multiline),
            (r'//.*?$', Comment.Single, '#pop'),
            (r'/', Comment.Preproc),
            (r'(?<=\\)\n', Comment.Preproc),
            (r'\n', Whitespace, '#pop'),
        ],
        'import': [
            (r'[\w:]+\*?', Name.Namespace, '#pop')
        ],

        'module_body': [
            (r'\bendmodule\b', Module.ModuleEnd, '#pop'),
            (words(('input', 'output', 'inout'), prefix=r'\b', suffix=r'\b'), Port.PortDirection, 'port_declaration'),
            (r'\bparameter\b', Module.Param, 'param_declaration'),
            (r'\bbegin\b', Token.Begin, 'begin'),
            keywords,
            builtin,
            (r'(\w+)\s*(?:#\(.*?\))?\s+(\w+)\s*\((.*?)\)\s*;', bygroups(Module.Body.Instance.Module,
                                                                        Module.Body.Instance.Name,
                                                                        Module.Body.Instance.Connections)),
            include('root'),
        ],

        'begin': [
            (r'\bend\b', Token.End, '#pop'),
        ],

        'module_name': [
            (r'\$?[a-zA-Z_]\w*', Module.ModuleName, ('#pop', 'module_header')),
            include('root'),
        ],

        'module_header': [
            (words(('input', 'output', 'inout'), prefix=r'\b', suffix=r'\b'), Port.PortDirection, 'port_declaration'),
            (r'\bparameter\b', Module.Param, 'param_declaration'),
            (r';', Module.ModuleHeaderEnd, '#pop'),
            (r'\)\s*;', Module.ModuleHeaderEnd, '#pop'),
            include('comments'),
            punctuation,
        ],

        'port_declaration': [
            (r'/(\\\n)?/(\n|(.|\n)*?[^\\]\n)', Port.Comment),  # indetify comments. Copied from another state
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Port.Comment),  # indetify comments. Copied from another state
            (words((
                # Variable types
                'bit', 'byte', 'chandle', 'const', 'event', 'int', 'integer',
                'logic', 'longint', 'real', 'realtime', 'reg', 'shortint',
                'shortreal', 'signed', 'string', 'time', 'type', 'unsigned',
                'var', 'void',
                # Net types
                'supply0', 'supply1', 'tri', 'triand', 'trior', 'trireg',
                'tri0', 'tri1', 'uwire', 'wand', 'wire', 'wor'),
                suffix=r'\b'),  # get the type of the port
             Port.PortType),
            # Match one or more brackets, indicating the port width
            (r'((\[[^]]+\])+)', Port.PortWidth),

            # port declaration ends with a ;, a ); or with the start of another port declaration
            (words(('input', 'output', 'inout'), suffix=r'\b', prefix=r'\b'), Port.PortDirection, ('#pop', 'port_declaration')),
            (r'\)\s*;', Module.HeaderEnd, '#pop:2'),
            (r';', Punctuation, '#pop'),
            (r'\$?[a-zA-Z_]\w*', Port.PortName),
            include('comments'),
            punctuation,
        ],

        'param_declaration': [
            (r'/(\\\n)?/(\n|(.|\n)*?[^\\]\n)', Module.Param.Comment),  # indetify comments. Copied from another state
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Module.Param.Comment),  # indetify comments. Copied from another state
            (words((
                # Variable types
                'bit', 'byte', 'chandle', 'const', 'event', 'int', 'integer',
                'logic', 'longint', 'real', 'realtime', 'reg', 'shortint',
                'shortreal', 'signed', 'string', 'time', 'type', 'unsigned',
                'var', 'void',
                # Net types
                'supply0', 'supply1', 'tri', 'triand', 'trior', 'trireg',
                'tri0', 'tri1', 'uwire', 'wand', 'wire', 'wor'),
                suffix=r'\b'), # get the type of the port
             Module.Param.ParamType),
            # Match one or more brackets, indicating the param width
            (r'((\[[^]]+\])+)', Module.Param.ParamWidth),
            (r';', Punctuation, '#pop'),
            # param declaration ends with a ;, a ); or with the start of another port declaration
            (r'\bparameter\b', Module.Param, ('#pop', 'param_declaration')),
            (r'\blocalparam\b', Keyword, '#pop'),
            (words(('input', 'output', 'inout'), prefix=r'\b', suffix=r'\b'), Port.PortDirection, ('#pop', 'port_declaration')),
            (r'=\s*([\d\'hHbBdxXzZ?_][\w\'hHbBdxXzZ]*|"[^"]*")', Punctuation),  # Filter parameter values
            (r'\$?[a-zA-Z_]\w*', Module.Param.ParamName),
            include('comments'),
            punctuation,
        ],

        'comments': [
            (r'\s+', Whitespace),
            (r'(\\)(\n)', bygroups(String.Escape, Whitespace)),  # line continuation
            (r'/(\\\n)?/(\n|(.|\n)*?[^\\]\n)', Comment.Single),
            (r'/(\\\n)?[*](.|\n)*?[*](\\\n)?/', Comment.Multiline),
            (r'[{}#@]', Punctuation),
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
        ],
    }


#    def get_tokens_unprocessed(self, text, stack=('root',)):
#        """
#        Split ``text`` into (tokentype, text) pairs.
#
#        ``stack`` is the initial stack (default: ``['root']``)
#        """
#        pos = 0
#        tokendefs = self._tokens
#        statestack = list(stack)
#        statetokens = tokendefs[statestack[-1]]
#        while 1:
#            for rexmatch, action, new_state in statetokens:
#                m = rexmatch(text, pos)
#                if m:
#                    if action is not None:
#                        if type(action) is _TokenType:
#                            yield pos, action, m.group()
#                        else:
#                            yield from action(self, m)
#                    pos = m.end()
#                    if new_state is not None:
#                        # state transition
#                        if isinstance(new_state, tuple):
#                            for state in new_state:
#                                if state == '#pop':
#                                    if len(statestack) > 1:
#                                        statestack.pop()
#                                        print(statestack)
#                                elif state == '#push':
#                                    statestack.append(statestack[-1])
#                                    print(statestack)
#                                else:
#                                    statestack.append(state)
#                                    print(statestack)
#                        elif isinstance(new_state, int):
#                            # pop, but keep at least one state on the stack
#                            # (random code leading to unexpected pops should
#                            # not allow exceptions)
#                            if abs(new_state) >= len(statestack):
#                                del statestack[1:]
#                                print(statestack)
#                            else:
#                                del statestack[new_state:]
#                                print(statestack)
#                        elif new_state == '#push':
#                            statestack.append(statestack[-1])
#                            print(statestack)
#                        else:
#                            assert False, f"wrong state def: {new_state!r}"
#                        statetokens = tokendefs[statestack[-1]]
#                    break
#            else:
#                # We are here only if all state tokens have been considered
#                # and there was not a match on any of them.
#                try:
#                    if text[pos] == '\n':
#                        # at EOL, reset state to "root"
#                        #statestack = ['root']
#                        #statetokens = tokendefs['root']
#                        #yield pos, Whitespace, '\n'
#                        pos += 1
#                        continue
#                    #yield pos, Error, text[pos]
#                    pos += 1
#                except IndexError:
#                    break
