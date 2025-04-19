# ./addons/eventscripts/corelib/escinject/escinject.py
# ported to Python by Hunter
# original command by Wonder

import es
import cmdlib

replacements = {
    'regex': [('\\', '\\\\'), ('^', '\\^'), ('$', '\\$'), ('*', '\\*'), ('+', '\\+'), ('?', '\\?'), ('.', '\\.'), ('|', '\\|'), ('[', '\\['), (']', '\\]'), ('(', '\\('), (')', '\\)'), ('{', '\\{'), ('}', '\\}')],
    'url': [('%', '%25'), (' ', '%20'), ('#', '%23'), ('$', '%24'), ('&', '%26'), ('+', '%2B'), (',', '%2C'), ('/', '%2F'), (':', '%3A'), (';', '%3B'), ('<', '%3C'), ('=', '%3D'), ('>', '%3E'), ('?', '%3F'), ('@', '%40'), ('[', '%5B'), ('\\', '%5C'), (']', '%5D'), ('^', '%5E'), ('`', '%60'), ('{', '%7B'), ('|', '%7C'), ('}', '%7D'), ('~', '%7E')],
    'sql': [('\'', '\'\'')]
}

def load():
    cmdlib.registerServerCommand('escinject', escinject_cmd, 'Escapes certain characters dependant on command. Syntax: escinject <command> <var> <string>')

    for line in (
        'testcase qcreate corelib escinjecttest "Tests escinject"',
        'testcase addtest escinjecttest escinjecttest corelib/escinject/testcase "Escinject Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('escinject')

def escinject_cmd(args):
    if len(args) > 2:
        subcmd = args[0]
        if subcmd in replacements:
            text = args[2]
            for replace in replacements[subcmd]:
                text = text.replace(replace[0], replace[1])
            es.ServerVar(args[1]).set(text)
        elif subcmd.endswith('b') and subcmd[:-1] in replacements:
            text = args[2]
            for replace in replacements[subcmd[:-1]]:
                text = text.replace(replace[1], replace[0])
            es.ServerVar(args[1]).set(text)
        else:
            es.dbgmsg(0, 'escinject: Invalid command to escinject. Valid commands: regex url sql regexb urlb sqlb')
    else:
        es.dbgmsg(0, 'escinject: Not enough arguments to escinject. Syntax: escinject <command> <var> <string>')

def testcase():
    for line in (
        'profile begin escinject_test',
        'profile begin escinject_regex',
        'testlib begin escinject_regex "escinject regex"',
        'es_xset _ei_t1 "\\^$*+?.|[](){}"',
        'es_xset _ei_t2 0',
        'es escinject regex _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "\\\\\\^\\$\\*\\+\\?\\.\\|\\[\\]\\(\\)\\{\\}"',
        'testlib end',
        'profile end escinject_regex',
        'profile begin escinject_url',
        'testlib begin escinject_url "escinject url"',
        'es_xset _ei_t1 "% #$&+,/:;<=>?@[\\]^`{|}~"',
        'es_xset _ei_t2 0',
        'es escinject url _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "%25%20%23%24%26%2B%2C%2F%3A%3B%3C%3D%3E%3F%40%5B%5C%5D%5E%60%7B%7C%7D%7E"',
        'testlib end',
        'profile end escinject_url',
        'profile begin escinject_sql',
        'testlib begin escinject_sql "escinject sql"',
        'es_xset _ei_t1 "\'"',
        'es_xset _ei_t2 0',
        'es escinject sql _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "\'\'"',
        'testlib end',
        'profile end escinject_sql',
        'profile begin escinject_regexb',
        'testlib begin escinject_regexb "escinject regexb"',
        'es_xset _ei_t1 "\\\\\\^\\$\\*\\+\\?\\.\\|\\[\\]\\(\\)\\{\\}"',
        'es_xset _ei_t2 0',
        'es escinject regexb _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "\\^$*+?.|[](){}"',
        'testlib end',
        'profile end escinject_regexb',
        'profile begin escinject_urlb',
        'testlib begin escinject_urlb "escinject urlb"',
        'es_xset _ei_t1 "%25%20%23%24%26%2B%2C%2F%3A%3B%3C%3D%3E%3F%40%5B%5C%5D%5E%60%7B%7C%7D%7E"',
        'es_xset _ei_t2 0',
        'es escinject urlb _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "% #$&+,/:;<=>?@[\\]^`{|}~"',
        'testlib end',
        'profile end escinject_urlb',
        'profile begin escinject_sqlb',
        'testlib begin escinject_sqlb "escinject sqlb"',
        'es_xset _ei_t1 "\'\'"',
        'es_xset _ei_t2 0',
        'es escinject sqlb _ei_t2 server_var(_ei_t1)',
        'testlib fail_unless _ei_t2 equalto "\'"',
        'testlib end',
        'profile end escinject_sqlb',
        'profile end escinject_test'):
        es.server.cmd(line)
