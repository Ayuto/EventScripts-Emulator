import es
import cmdlib

import re
import random

cond = {'=' : '==', '==' : '==', 'equalto' : '==', 'in' : 'in', '!=' : '!=', '!==' : '!=', '<' : '<', 'lessthan' : '<', '>' : '>', 'greaterthan' : '>', '<=' : '<=', '=<' : '<=', 'notgreaterthan' : '<=', '>=' : '>=', '=>' : '>=', 'notlessthan' : '>='}

srcdsargs = []

funccmds = []

def func_rand(args):
    return str(random.randint(int(args[0]), int(args[1])))

def func_mathparse(args):
    es.server.cmd('es_xset _tempcore 0; es_xmathparse _tempcore ' + str(args[0]))
    return es.server_var['_tempcore']

def func_keyval(args):
    temp = '0'
    exec('temp = es.keygetvalue(' + pythonargs(args, 3) + ')')
    return str(temp)

def func_exists(args):
    temp = '0'
    exec('temp = es.exists(' + pythonargs(args, 4) + ')')
    return str(temp)

def func_ins(args):
    if str(args[0]) == '0':
        return str(args[1])
    elif str(args[0]) == '1':
        return str(args[2])
    else:
        return '0'

def func_isnull(args):
    es.server.cmd('es_xset _tempcore 0; isnull _tempcore ' + str(args[0]))
    return es.server_var['_tempcore']

def func_event_var(args):
    temp = '0'
    temp = str(es.event_var[args[0]])
    return temp

def func_cond(args):
    global cond
    if str(args[1]) in cond:
        temp = '0'
        exec('if "' + str(args[0]) + '" ' + cond[str(args[1])] + ' "' + str(args[2]) + '":\n    temp = \'1\'')
        return temp
    elif args[1] == 'notin':
        temp = '0'
        exec('if not ' + str(args[0]) + ' in ' + str(args[2]) + '\:\ntemp = \'1\'')
        return temp
    else:
        return '0'

def func_ev(args):
    temp = '0'
    temp = str(es.event_var[args[0]])
    return temp

def func_eq(args):
    return '"' + ''.join(args).replace('"', '') + '"'

def func_randplayer(args):
    es.server.cmd('es_xset _tempcore 0; getrandplayer _tempcore ' + str(args[0]))
    return es.server_var['_tempcore']

def func_strlen(args):
    return str(len(args[0]))

def func_playerinfo(args):
    es.server.cmd('es_xset _tempcore 0; getplayerinfo _tempcore ' + str(args[0]))
    return es.server_var['_tempcore']

def func_isbot(args):
    temp = '0'
    temp = str(es.isbot(args[0]))
    return temp

def func_server_var(args):
    temp = '0'
    temp = str(es.server_var[args[0]])
    return temp

def func_nq(args):
    return ''.join(args).replace('"', '')

def func_math(args):
    args2 = list(args)
    del args2[0]
    es.server.cmd('es_xset _tempcore 0; es_xset _tempcore "' + args[0] + '"; es_xmath _tempcore ' + srcdsstring(args2))
    return es.server_var['_tempcore']

def func_define(args):
    if len(args) > 1:
        es.set(args[0], args[1])
    else:
        es.set(args[0], '0')
    return args[0]

def func_username(args):
    temp = '0'
    temp = str(es.getplayername(args[0]))
    return temp

def func_steamid(args):
    temp = '0'
    temp = str(es.getplayersteamid(args[0]))
    return temp

def func_playerprop(args):
    temp = '0'
    exec('temp = es.getplayerprop(' + pythonargs(args, 2) + ')')
    return temp

def func_string(args):
    args2 = list(args)
    del args2[0]
    es.server.cmd('es_xset _tempcore 0; es_xset _tempcore "' + args[0] + '"; es_xstring _tempcore ' + srcdsstring(args2))
    return es.server_var['_tempcore']

def func_textlib(args):
    args2 = list(args)
    del args2[0]
    es.server.cmd('es_xset _tempcore 0; textlib "' + args[0] + '" _tempcore ' + srcdsstring(args2))
    return es.server_var['_tempcore']

def func_playerxloc(args):
    temp = '0'
    temp = str(es.getplayerlocation(args[0])[0])
    return temp

def func_uniqueid(args):
    es.server.cmd('es_xset _tempcore 0; uniqueid _tempcore ' + srcdsstring(str(args[0])))
    return es.server_var['_tempcore']

def func_playeryloc(args):
    temp = '0'
    temp = str(es.getplayerlocation(args[0])[1])
    return temp

def func_average(args):
    es.server.cmd('es_xset _tempcore 0; average _tempcore ' + srcdsstring(args))
    return es.server_var['_tempcore']

def func_userid(args):
    temp = '0'
    temp = str(es.getuserid(args[0]))
    return temp

def func_sv(args):
    temp = '0'
    temp = str(es.server_var[args[0]])
    return temp

def func_indexprop(args):
    temp = '0'
    exec('temp = es.getindexprop(' + pythonargs(args, 2) + ')')
    return temp

def func_playerzloc(args):
    temp = '0'
    temp = str(es.getplayerlocation(args[0])[2])
    return temp

def func_entityindex(args):
    temp = '0'
    temp = str(es.getentityindex(args[0]))
    return temp

def func_isnumerical(args):
    es.server.cmd('es_xset _tempcore 0; isnumerical _tempcore ' + srcdsstring(args))
    return es.server_var['_tempcore']

def func_token(args):
    es.server.cmd('es_xset _tempcore 0; es_xtoken _tempcore ' + srcdsstring(args))
    return es.server_var['_tempcore']

def func_playervar(args):
    es.server.cmd('es_xset _tempcore 0; playervar get _tempcore ' + srcdsstring(args))
    return es.server_var['_tempcore']

def func_playerget(args):
    args2 = list(args)
    del args2[0]
    es.server.cmd('es_xset _tempcore 0; playerget "' + args[0] + '" _tempcore ' + srcdsstring(args2))
    return es.server_var['_tempcore']

def func_botname(args):
    es.server.cmd('es_xset _tempcore 0; botname _tempcore ' + srcdsstring(str(args[0])))
    return es.server_var['_tempcore']

uxpfuncs = []

funcs = {}

funcs['nq'] = {'function' : func_nq, 'minargs' : 1}
funcs['eq'] = {'function' : func_eq, 'minargs' : 1}
funcs['server_var'] = {'function' : func_server_var, 'minargs' : 1}
funcs['event_var'] = {'function' : func_event_var, 'minargs' : 1}
funcs['sv'] = {'function' : func_sv, 'minargs' : 1}
funcs['ev'] = {'function' : func_ev, 'minargs' : 1}
funcs['cond'] = {'function' : func_cond, 'minargs' : 3}
funcs['average'] = {'function' : func_average, 'minargs' : 1}
funcs['botname'] = {'function' : func_botname, 'minargs' : 1}
funcs['define'] = {'function' : func_define, 'minargs' : 1}
funcs['entityindex'] = {'function' : func_entityindex, 'minargs' : 1}
funcs['exists'] = {'function' : func_exists, 'minargs' : 2}
funcs['indexprop'] = {'function' : func_indexprop, 'minargs' : 2}
funcs['ins'] = {'function' : func_ins, 'minargs' : 3}
funcs['isbot'] = {'function' : func_isbot, 'minargs' : 1}
funcs['isnumerical'] = {'function' : func_isnumerical, 'minargs' : 1}
funcs['isnull'] = {'function' : func_isnull, 'minargs' : 1}
funcs['keyval'] = {'function' : func_keyval, 'minargs' : 2}
funcs['math'] = {'function' : func_math, 'minargs' : 2}
funcs['mathparse'] = {'function' : func_mathparse, 'minargs' : 1}
funcs['playerinfo'] = {'function' : func_playerinfo, 'minargs' : 1}
funcs['playerget'] = {'function' : func_playerget, 'minargs' : 2}
funcs['playerprop'] = {'function' : func_playerprop, 'minargs' : 2}
funcs['playervar'] = {'function' : func_playervar, 'minargs' : 2}
funcs['playerxloc'] = {'function' : func_playerxloc, 'minargs' : 1}
funcs['playeryloc'] = {'function' : func_playeryloc, 'minargs' : 1}
funcs['playerzloc'] = {'function' : func_playerzloc, 'minargs' : 1}
funcs['rand'] = {'function' : func_rand, 'minargs' : 2}
funcs['randplayer'] = {'function' : func_randplayer, 'minargs' : 1}
funcs['steamid'] = {'function' : func_steamid, 'minargs' : 1}
funcs['string'] = {'function' : func_string, 'minargs' : 3}
funcs['strlen'] = {'function' : func_strlen, 'minargs' : 1}
funcs['textlib'] = {'function' : func_textlib, 'minargs' : 3}
funcs['token'] = {'function' : func_token, 'minargs' : 2}
funcs['uniqueid'] = {'function' : func_uniqueid, 'minargs' : 1}
funcs['userid'] = {'function' : func_userid, 'minargs' : 1}
funcs['username'] = {'function' : func_username, 'minargs' : 1}

funcsregex = '|'.join(funcs)

regex1 = re.compile(funcsregex)

def load():
    cmdlib.registerServerCommand('exp', exp, 'Inline expansion of ES funtions for ESS')
    cmdlib.registerServerCommand('uxp', exp, 'Inline expansion of ES funtions for ESS')
    cmdlib.registerServerCommand('exp_reg', exp_reg, 'Inline expansion of ES funtions for ESS')
    cmdlib.registerServerCommand('uxp_reg', uxp_reg, 'Inline expansion of ES funtions for ESS')
    cmdlib.registerServerCommand('_exp_eval', evaluate, 'Inline expansion of ES funtions for ESS')

    for line in (
        'testcase qcreate corelib exptest "Tests exp"',
        'testcase addtest exptest exptest corelib/exp/test_exp "Exp Corelib Command Test"',
        'testcase addtest exptest uxptest corelib/exp/test_uxp "Uxp Corelib Command Test"'):
        es.server.queuecmd(line)

def unload():
    cmdlib.unregisterServerCommand('exp')
    cmdlib.unregisterServerCommand('uxp')
    cmdlib.unregisterServerCommand('exp_reg')
    cmdlib.unregisterServerCommand('uxp_reg')
    cmdlib.unregisterServerCommand('_exp_eval')

def exp(args_dummy):
    args = es.getargs()
    if ('\(' in args) or ('\)' in args):
        args = args.replace('\(', '%left%').replace('\)', '%right%').replace('\"', '%quote%')
    if args and ('(' in args) and (')' in args):
        global funcs
        global uxpfuncs
        global regex1
        global srcdsargs
        if args.count('"') % 2:
            args += '"'
        infuncs = regex1.findall(''.join(re.findall('"[^"]*"|([^"]+)', args)))
        if infuncs:
            regex2 = re.compile('(' + '|'.join(infuncs) + ')\\((("[^\\(\\)"]*"|[^\\(\\)"]+)*)\\)')
            temp = True
            count = 10
            while temp:
                count -= 1
                if not count:
                    temp = 0
                regex = regex2.search(args)
                if regex:
                    regex = regex.groups()
                    func = regex[0]
                    val = regex[1]
                    es.msg(func + '(' + val + ')')
                    if func in funcs:
                        if not func in ('nq', 'eq'):
                            es.server.cmd('_exp_eval ' + val)
                        else:
                            srcdsargs = val
                        if len(srcdsargs) >= funcs[func]['minargs']:
                            if func in uxpfuncs:
                                uxp_eval(func, srcdsargs)
                                result = es.server_var['_uxp_result']
                            else:
                                funcpointer = funcs[func]['function']
                                result = funcpointer(srcdsargs)
                            if not func in ('nq', 'eq'):
                                result = '"' + result + '"'
                        else:
                            result = '0'
                        args = args.replace(func + '(' + val + ')', result)
                else:
                    temp = False
    args = args.replace('%left%', '(').replace('%right%', '(').replace('%quote%', '"')
    es.server.cmd(args)

def uxp_reg(args_dummy):
    argc = es.getargc()
    if argc > 2:
        global uxpfuncs
        global funcs
        global regex1
        subcmd = es.getargv(1)
        if subcmd == 'create':
            if argc > 3:
                func = es.getargv(2)
                cmdstring = es.getargv(3)
                if func in funcs:
                    es.dbgmsg(0, 'uxp_reg : function already registered')
                elif not '%var' in cmdstring:
                    es.dbgmsg(0, 'uxp_reg : %var MUST be included in command string')
                else:
                    uxpfuncs.append(func)
                    funcs[func] = {'uxp' : cmdstring, 'minargs' : 0}
                    funcsregex = '|'.join(funcs)
                    regex1 = re.compile(funcsregex)
            else:
                es.dbgmsg(0, 'Syntax : uxp_reg create <function> <commandstring>')
        elif subcmd == 'delete':
            func = es.getargv(2)
            if func in uxpfuncs:
                del uxpfuncs[func]
                del funcs[func]
                funcsregex = '|'.join(funcs)
                regex1 = re.compile(funcsregex)
        elif subcmd == 'status':
            if argc > 3:
                var = es.getargv(2)
                func = es.getargv(3)
                if func in uxpfuncs:
                    es.set(var, '1')
                else:
                    es.set(var, '0')
            else:
                es.dbgmsg(0, 'Syntax : uxp_reg status <variable> <function>')
        else:
            es.dbgmsg(0, 'uxp_reg : invalid subcommand (create|delete|status)')
    else:
        es.dbgmsg(0, 'Syntax : uxp_reg <subcmd> <args>')
    
    


def uxp_eval(func, args):
    global funcs
    cmdstring = funcs[func]['uxp']
    for num in range(1,10):
        if '%' + str(num) in cmdstring:
            cmdstring = cmdstring.replace('%' + str(num), args[num-1])
        if '%args' in cmdstring:
            cmdstring = cmdstring.replace('%args', '"' + '" "'.join(args) + '"')
        if '%argv' in cmdstring:
            cmdstring = cmdstring.replace('%' + str(num), len(args))
    cmdstring = cmdstring.replace('%var', '_uxp_result')
    es.set('_uxp_result', '0')
    es.server.cmd(cmdstring)


def evaluate(args_dummy):
    global srcdsargs
    srcdsargs = []
    for arg in range(1, es.getargc()):
        srcdsargs.append(es.getargv(arg))
    srcdsargs = tuple(srcdsargs)

def srcdsstring(args):
    return '"' + '" "'.join(args) + '"'

def pythonargs(args, argc):
    temp = len(args)
    if temp < argc:
         argc = temp
    count = 0
    string = ''
    string += ('"' + str(args[count]) + '"')
    argc -= 1
    while argc > 0:
        argc -= 1
        count += 1
        string += (', "' + str(args[count]) + '"')
    return string

def exp_reg(args_dummy):
    argc = es.getargc()
    if argc > 3:
        global funcs
        global funcsregex
        global regex1
        block = es.getargv(2)
        func = es.getargv(1)
        minargs = es.getargv(3)
        if not func in funcs:
            if re.match('^.+/.+(/.+)?$', block):
                if es.exists('block', block):
                    if argc > 4:
                        global funccmds
                        userfunc = '_exp_userfunc' + str(len(funccmds) + 1)
                        es.regcmd(userfunc, block, 'exp user function')
                        funcs[func] = {}
                        funccmds.append(userfunc)
                        funcs[func]['function'] = userfunc
                        funcs[func]['minargs'] = int(minargs)
                        funcs[func]['var'] = es.getargv(4)
                        funcsregex = '|'.join(funcs)
                        regex1 = re.compile(funcsregex)
                    else:
                        es.dbgmsg(0, 'exp_reg : input variable name must be given for function block')
                else:
                    es.dbgmsg(0, 'exp_reg : invalid block given')
            elif  re.match('^.+\\..+(\\..+)?$', block):
                temp = block.split('.')
                
                exec('temp = callable(' + block + ')')
                if temp:
                    exec('funcs[func][\'function\'] = ' + block)
                    funcs[func]['minargs'] = minargs
                    funcsregex = '|'.join(funcs)
                    regex1 = re.compile(funcsregex)
                else:
                    es.dbgmsg(0, 'exp_reg : invalid function given')
            else:
                es.dbgmsg(0, 'exp_reg : invalid block/function given')
        else:
            es.dbgmsg(0, 'exp_reg : function already registered')
    else:
        es.dbgmsg(0, 'Syntax : exp_reg <function-name> <function/block> <min-args> [var]')

def test_exp():
    for line in (
        'profile begin exp_test',
        'testlib begin exp1 "exp test 1 - server_var()"',
        'es_xset _exp_testvar 3',
        'exp es_xif(server_var(_exp_testvar) = 3) then es_xset _exp_testvar 7',
        'testlib fail_unless _exp_testvar equalto 7',
        'testlib end',
        'testlib begin exp2 "exp test 2 - sv()"',
        'es_xset _exp_testvar 2',
        'exp es_xif(sv(_exp_testvar) = 2) then es_xset _exp_testvar 8',
        'testlib fail_unless _exp_testvar equalto 8',
        'testlib end',
        'testlib begin exp3 "exp test 3 - server_var(server_var())"',
        'es_xset _exp_testvar _exp_testvar2',
        'es_xset _exp_testvar2 6',
        'exp es_xif(server_var(server_var(_exp_testvar)) = 6) then es_xset _exp_testvar 9',
        'testlib fail_unless _exp_testvar equalto 9',
        'testlib end',
        'testlib begin exp4 "exp test 4 - nq()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar nq("hello world my name is chun")',
        'testlib fail_unless _exp_testvar equalto hello',
        'testlib end',
        'testlib begin exp5 "exp test 5 - eq()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar eq("hello" "world")',
        'testlib fail_unless _exp_testvar equalto "hello world"',
        'testlib end',
        'testlib begin exp6 "exp test 6 - cond()"',
        'es_xset _exp_testvar 0',
        'exp es_xset _exp_testvar cond(hello = hello)',
        'testlib fail_unless _exp_testvar equalto 1',
        'testlib end',
        'testlib begin exp7 "exp test 7 - ins()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar ins(1 hello world)',
        'testlib fail_unless _exp_testvar equalto world',
        'testlib end',
        'testlib begin exp8 "exp test 8 - define()"',
        'exp define(_this_var_is_unlikely_to_be_used 7)',
        'testlib fail_unless _this_var_is_unlikely_to_be_used equalto 7',
        'testlib end',
        'testlib begin exp9 "exp test 9 - rand()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar rand(1 2)',
        'testlib fail_unless _exp_testvar notequalto 0',
        'testlib end',
        'testlib begin exp10 "exp test 10 - strlen()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar strlen("hello world")',
        'testlib fail_unless _exp_testvar equalto 11',
        'testlib end',
        'testlib begin exp11 "exp test 11 - token()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar token("hello world I am Chun" 2)',
        'testlib fail_unless _exp_testvar equalto world',
        'testlib end',
        'testlib begin exp12 "exp test 12 - string()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar string("hello world" replace o)',
        'testlib fail_unless _exp_testvar equalto "hell wrld"',
        'testlib end',
        'testlib begin exp13 "exp test 13 - keyval()"',
        'es_xkeycreate _exptest',
        'es_xkeysetvalue _exptest val 5',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar keyval(_exptest val)',
        'es_xkeydelete _exptest',
        'testlib fail_unless _exp_testvar equalto 5',
        'testlib end',
        'testlib begin exp14 "exp test 14 - math()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar math(5 + 2)',
        'testlib fail_unless _exp_testvar equalto 7',
        'testlib end',
        'testlib begin exp15 "exp test 15 - mathparse()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar mathparse("5+2")',
        'testlib fail_unless _exp_testvar equalto 7',
        'testlib end',
        'testlib begin exp16 "exp test 16 - exists()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar exists(variable _tempcore)',
        'testlib fail_unless _exp_testvar equalto 1',
        'testlib end',
        'testlib begin exp17 "exp test 17 - isnumerical()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar isnumerical(125)',
        'testlib fail_unless _exp_testvar equalto 1',
        'testlib end',
        'testlib begin exp18 "exp test 18 - isnull()"',
        'es_xset _exp_testvar a',
        'es_xstring _exp_testvar replace a',
        'exp es_xsetinfo _exp_testvar isnull(_exp_testvar)',
        'testlib fail_unless _exp_testvar equalto 1',
        'testlib end',
        'testlib begin exp19 "exp test 19 - textlib()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar textlib(tokencount aaaa a)',
        'testlib fail_unless _exp_testvar equalto 4',
        'testlib end',
        'testlib begin exp20 "exp test 20 - average()"',
        'es_xset _exp_testvar 0',
        'exp es_xsetinfo _exp_testvar average(5 7 9)',
        'testlib fail_unless _exp_testvar equalto 7',
        'testlib end',
        'profile end exp_test'):
        es.server.cmd(line)

def test_uxp():
    for line in (
        'profile begin uxp_test',         
        'testlib begin uxp1 "uxp test 1 - strlen()"',
        'uxp es_xset _uxp_testvar strlen(helloworld)',
        'testlib fail_unless _uxp_testvar equalto 10',
        'testlib end',
        'testlib begin uxp2 "uxp test 2 - testcasefunc()"',
        'uxp_reg create testcasefunc "es_xset %var %1"',
        'uxp es_xset _uxp_testvar testcasefunc(17)',
        'testlib fail_unless _uxp_testvar equalto 17',
        'testlib end',
        'profile end uxp_test'):
        es.server.cmd(line)
