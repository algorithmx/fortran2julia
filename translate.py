import os
import sys
import json
from collections import deque
import time

from os.path import dirname
sys.path.append('/home/yunlong/Dropbox/First_Principle_Calculations/codes/fortran2julia/')

import Utinity as UT
import ParseLit as PL
import PatternCollection as PC
import fortran2julia as FJ


def first_run(fn):

    if os.path.isfile(fn) and (('.F90' in fn) or ('.f90' in fn)):
        with open(fn) as f:
            lines_fortran = f.readlines()

        lines_julia = []
        JUMP_LINE = []
        OK_LAB = []

        i = 0
        while i<len(lines_fortran):
            if i % 10 == 0:
                # keeping track of the original file
                lines_julia.append("#FORTRAN_LINE "+str(i)+"  #XXX")
            #end #if

            l = lines_fortran[i].strip().lower()
            i += 1

            # prevent all comments from being procesed
            #NOTE comment line won't break !!!
            if len(l)==0:
                continue
            elif FJ.is_fortran_comment(l):
                lines_julia.append(FJ.process_fortran_comments(l))
                continue
            else:
                comms = []
                ll, comm = FJ.separate_fortran_comments(l)
                ll = ll.strip()
                comm = comm.strip(' !')
                if len(comm) > 0:
                    comms.append(comm)
                if ll.endswith('&'):
                    l = ll.rstrip(' &')
                    while i < len(lines_fortran):
                        l2 = lines_fortran[i].strip().lower()
                        i += 1
                        ll2, comm2 = FJ.separate_fortran_comments(l2)
                        ll2 = ll2.strip()
                        comm2 = comm2.strip(' !')
                        if len(comm2) > 0:
                            comms.append(comm2)

                        l += ' ' + ll2.strip('& ')
                        if (len(ll2.strip('& ')) == 0):
                            continue
                        elif (ll2[-1] != '&'):
                            break
                    #end #while
                #end #if
                #l = l + ' ! ' + (" # ".join(comms))

            l = FJ.correct_tail_fortran_comments(l)

            #multiline
            is_multi_bool, L = FJ.is_multi_line(l)
            if is_multi_bool:
                for li in L:
                    ltmp = li[:].strip()
                    if len(ltmp)>0:
                        ltmp = FJ.commenting_out(ltmp)
                        if FJ.is_julia_comment(ltmp):
                            lines_julia.append(FJ.process_fortran_comments(ltmp))
                            continue

                        #if is_fortran_one_line_if(ltmp):
                        #    ltmp = complete_fortran_one_line_if(ltmp)
                        #else:
                        #    ltmp = bracket_conditions(ltmp)

                        #ltmp = FJ.correct_io_error(ltmp)
                        ltmp = FJ.correct_function_calls(ltmp)

                        #ltmp = process_for(ltmp, OK_LAB, JUMP_LINE)
                        #ltmp = search_for_ok_label(ltmp, OK_LAB)
                        #ltmp = process_jump_line(ltmp, JUMP_LINE)

                        res1 = FJ.fortran_to_julia_replace(ltmp)
                        res2 = FJ.rewrite_fortran_array_to_julia(res1)
                        lines_julia.append(res2)
                    #end #if
                #end #for
            else:
                assert len(L)==1
                ltmp = L[0].strip()
                if len(ltmp)>0:
                    ltmp = FJ.commenting_out(ltmp)
                    if FJ.is_julia_comment(ltmp):
                        lines_julia.append(FJ.process_fortran_comments(ltmp))
                        continue

                    if FJ.is_fortran_one_line_if(ltmp):
                        ltmp = FJ.complete_fortran_one_line_if(ltmp)
                    else:
                        ltmp = FJ.bracket_conditions(ltmp)

                    #ltmp = FJ.correct_io_error(ltmp)
                    ltmp = FJ.correct_function_calls(ltmp)

                    ltmp = FJ.process_for(ltmp, OK_LAB, JUMP_LINE)
                    ltmp = FJ.search_for_ok_label(ltmp, OK_LAB)
                    ltmp = FJ.process_jump_line(ltmp, JUMP_LINE)

                    res1 = FJ.fortran_to_julia_replace(ltmp)
                    res2 = FJ.rewrite_fortran_array_to_julia(res1)
                    lines_julia.append(res2)
                #end #if

        #end #while

        return "\n".join(lines_julia)
    else:
        return ''
    #end #if


def second_run(res1):

    lines = [l.strip() for l in res1.split('\n') if len(l)>0]
    fmt_lines = {}
    for i,l0 in enumerate(lines):
        if FJ.is_format_line(l0):
            tmp = FJ.update_format_lines(l0,fmt_lines)
            fmt_lines = tmp[0]
            m = tmp[1]
            lines[i] = l0.replace(m, "#" + m, 1)
        #end #if
    #end #for
    print("[INFO:FMT_2nd] " + str(fmt_lines))

    line_inden_level = 0
    func_names = []
    loop = deque()
    for i,l0 in enumerate(lines):
        l = l0.strip()
        if FJ.is_ifdef_label(l):
            lines[i] = l.strip()
            continue
        elif l.startswith("#JUMP_LINE"):
            lines[i] = l
            continue
        elif FJ.is_julia_comment(l):
            lines[i] = ("    " * line_inden_level) + l
            continue
        elif FJ.is_write(l):
            lines[i] = ("    " * line_inden_level) + FJ.fortran_write_julia(l, fmt_lines)
            continue
        else:
            X, comm = FJ.separate_julia_comments(l)
            if X.startswith('for'):
                if X.startswith('for while'):
                    loop.append( ('while', i) )
                    lines[i] = ( "    " * line_inden_level ) + l.replace('for while','while',1)
                    line_inden_level += 1
                    continue
                else:
                    loop.append( ('for',i) )
                    lines[i] = ("    " * line_inden_level) + l
                    line_inden_level += 1
                    continue
                #end #if
            elif l.startswith("while true"):
                loop.append( ("while true",i) )
                lines[i] = ("    " * line_inden_level) + l
                line_inden_level += 1
                continue
            elif l.startswith('if'):
                if X.strip().endswith('end') and ("#if" in comm.strip()):
                    lines[i] = ("    " * line_inden_level) + l
                    continue
                else:
                    loop.append(('if',i))
                    lines[i] = ("    " * line_inden_level) + l
                    line_inden_level += 1
                    continue
                #end #if
            elif l.startswith('elseif') and (loop[-1][0]=='if'):
                lines[i] = ("    " * (line_inden_level-1)) + l
                continue
            elif l.startswith('else') and (loop[-1][0]=='if'):
                lines[i] = ("    " * (line_inden_level-1)) + l
                continue
            elif l.startswith('function'):
                func_names.append(FJ.get_func_name(l))
                loop.append(('function',i))
                lines[i] = ("    " * line_inden_level) + l
                line_inden_level += 1
                continue
            elif (X.strip().endswith('end') and ("#if" in comm.strip()) ) and (loop[-1][0] in ['if','elseif']):
                line_inden_level -= 1
                loop.pop()
                lines[i] = ("    " * line_inden_level) + l
                continue
            elif (X.strip().endswith('end') and ("#for" in comm.strip()) ):
                if loop[-1][0]=="for":
                    line_inden_level -= 1
                    loop.pop()
                    lines[i] = ("    " * line_inden_level) + l
                    continue
                elif loop[-1][0]=="while":
                    line_inden_level -= 1
                    loop.pop()
                    lines[i] = ("    " * line_inden_level) + X + comm.replace('#for', ' #while', 1)
                    continue
                elif loop[-1][0]=="while true":
                    line_inden_level -= 1
                    loop.pop()
                    lines[i] = ("    " * line_inden_level) +  X + comm.replace('#for', ' #while true', 1)
                    continue
                #end #if
            elif (X.strip().endswith('end') and ("#function" in comm.strip()) ) and (loop[-1][0]=='function'):
                line_inden_level -= 1
                loop.pop()
                lines[i] = ("    " * line_inden_level) + l
                continue
            else:
                lines[i] = ("    " * line_inden_level) + l
                continue
            #end #if
        #end #if
    #end #for

    return "\n".join(lines)




def third_run(res2):  # process_array_colon_expr

    lines = [FJ.process_array_colon_expr(l) for l in res2.split('\n') if len(l)>0]

    lines2 = [  FJ.replace_string_concat_simple( PL.process_dp(l)).\
                replace("https: * ",  "https://").replace("http: * ",  "http://")\
                for l in lines ]

    return "\n".join(lines2)




def fourth_run(res3):

    lines = [l for l in res3.split('\n') if len(l) > 0]

    funcs = set( FJ.get_func_name(l) for (i, l) in enumerate(lines) if FJ.is_func(l))

    for (i, l) in enumerate(lines):
        if FJ.is_func(l):
            if not FJ.is_julia_comment(l):
                lines[i] = FJ.correct_func_name(l, funcs)
            #end #if
        #end #if
    #end #for

    arrs = []
    for (i, l) in enumerate(lines):
        for a in FJ.extract_array_names(l):
            arrs.append(a)
        #end #for
    #end #for

    arrs = set(arrs)

    for (i,l) in enumerate(lines):
        if not FJ.is_julia_comment(l):
            lines[i] = FJ.correct_array_brackets(l,arrs,funcs)
        #end #if
    #end #for

    for i,l0 in enumerate(lines):
        if (len(l0)>0 and (not FJ.is_julia_comment(l0)) and FJ.is_end_func(l0)):
            lines[i] = l0 + "\n#-\n#-\n#-"
        else:
            pass
        #end #if
    #end #for
    return "\n".join(lines)








#NOTE https://docs.julialang.org/en/v1/manual/variables-and-scoping/index.html
#NOTE principles of translation modules
#NOTE see also test2.jl
# translating modules

#NOTE lines are NOT altered
def fifth_run(res, fname, allo_lines_fn, allo_json_fn, allo_log_fn, func_log_fn, modu_log_fn, pubv_log_fn):

    FN = fname.replace('.F90', '') if ('.F90' in fname) else fname.replace('.f90', '')
    lines = [x for x in res.split("\n") if len(x)>0]
    allocatables_FN = {}
    allocates_FN = {}
    allo_lines_record_FN = {}
    pub_vars_FN = {}

    modus = {FJ.get_module_name(l):(i, -1) for (i, l) in enumerate(lines) \
                                            if FJ.is_module(l.strip()) }
    for (i,l) in enumerate(lines):
        if FJ.is_program(l.strip()):
            modus[FJ.get_program_name(l)] = (i, -1)

    if len(modus)>0:
        for (i,l) in enumerate(lines):
            if FJ.is_end_module(l):
                n = FJ.get_module_name(l)
                b,e = modus[n]
                modus[n] = (b,i)
            elif FJ.is_end_program(l):
                n = FJ.get_program_name(l)
                b,e = modus[n]
                modus[n] = (b,i)
            #end #if
        #end #for
        modus[FN+"_outside_all_modules"] = (-1,-1)
    else:
        modus[FN+"_no_module"] = (0,len(lines)-1)
    #end #if

    funcs = {FJ.get_func_name(l):(i,-1) for (i,l) in enumerate(lines) if FJ.is_func(l)}
    if len(funcs)>0:
        for (i,l) in enumerate(lines):
            if FJ.is_end_func(l):  # not commented out
                n = FJ.get_func_name(l)
                if len(n)>0:
                    b,e = funcs[n]
                    funcs[n] = (b,i)
                else:
                    for j in range(i-1,-1,-1):
                        if FJ.is_func(lines[j]):
                            n = FJ.get_func_name(lines[j])
                            b,e = funcs[n]
                            assert b==j
                            funcs[n] = (b,i)
                            break
                    #end #for
                #end #if
        #end #for
    else:
        funcs[FN+"_no_function"] = (-1,-1)
    #end #if

    # for each line search for allocatables and assign
    for i, l0 in enumerate(lines):
        if FJ.is_FORTRAN_CONTROL(l0):
            L = PC.FORTRAN_CONTROL_patt.split(l0)
            L1, COMM = FJ.separate_julia_comments(L[1])
            L1 = L1.lower().strip()
            if 'allocatable' in L1:
                AL = FJ.find_allocatable(L1)
                if len(AL) > 0:
                    allo_lines_record_FN[i] = l0
                    mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
                    for (name, typ, naxes, is_save, is_pub) in AL:
                        allocatables_FN[name] = { 'declaredAT': i, \
                                                   'is_public': is_pub, 'is_save': is_save, \
                                                   'type': typ, 'Naxes': naxes }

    for i, l0 in enumerate(lines):
        if FJ.is_FORTRAN_CONTROL(l0):
            L = PC.FORTRAN_CONTROL_patt.split(l0)
            L1, COMM = FJ.separate_julia_comments(L[1])
            L1 = L1.lower().strip()
            if FJ.is_allocate(L1):
                allo_lines_record_FN[i] = l0
                mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
                for (name, shape, Naxes) in FJ.allocate_who(L1):
                    allocates_FN[name] = {}
                    allocates_FN[name]['allocAT'] = i
                    allocates_FN[name]['shape'] = shape
                    allocates_FN[name]['Naxes'] = Naxes
            elif FJ.is_deallocate(L1):
                allo_lines_record_FN[i] = l0
                mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
                for name in FJ.deallocate_who(L1):
                    allocates_FN[name] = {}
                    allocates_FN[name]['deallocAT'] = i
            elif FJ.is_public_export(L1) and FJ.is_contain_save(L1):
                mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
                for (name, typ, is_save, is_pub) in FJ.Ndeclare_who(L1):
                    pub_vars_FN[name[0]] = { 'is_public': is_pub, 'is_save': is_save, \
                                          'declaredAT': i,  'type': typ }
            else:
                pass

    UT.update_json_file(allo_lines_fn, FN, allo_lines_record_FN)
    UT.update_json_file(allo_json_fn, FN, allocatables_FN)
    UT.update_json_file(allo_log_fn, FN, allocates_FN)
    UT.update_json_file(func_log_fn, FN, funcs)
    UT.update_json_file(modu_log_fn, FN, modus)
    UT.update_json_file(pubv_log_fn, FN, pub_vars_FN)
    return "\n".join(lines)




def sixth_run(res, fname, allo_json_fn, allo_log_fn, func_log_fn, modu_log_fn):
    FN = fname.replace('.F90', '') if ('.F90' in fname) else fname.replace('.f90', '')

    with open(allo_json_fn,'r') as h:
        read_data = h.read()
    allocatables = json.loads(read_data)
    allo_FN = allocatables[FN]

    with open(func_log_fn,'r') as X:
        reads = X.read()
    func_log = json.loads(reads)
    funcs = func_log[FN]

    with open(modu_log_fn,'r') as X:
        reads = X.read()
    modu_log = json.loads(reads)
    modus = modu_log[FN]

    lines = res.split("\n")
    # for each line search for allocatables and assign
    for i, l0 in enumerate(lines):
        if FJ.is_FORTRAN_CONTROL(l0):
            mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
            L = PC.FORTRAN_CONTROL_patt.split(l0)
            L1, COMM = FJ.separate_julia_comments(L[1])
            L1 = L1.lower().strip()
            if 'allocatable' in L1:
                # already consider "public" discriptor
                AL = FJ.find_allocatable(L1)
                if len(AL) > 0:
                    is_in_f = False
                    mod_n, func_n = FJ.where_is_the_line(i, funcs, modus)
                    # the scope of an allocatable declaration should ALWAYS be inside a module
                    if (func_n is None):  # inside module but outside a function
                        is_in_f = False
                    elif ("_no_function" in func_n):
                        print( "[WARNING:DECLARE] there is no function in the file \"" + FN + "\"" )
                        is_in_f = False
                    else:
                        # inside a function
                        is_in_f = True

                    lines[i] = FJ.write_declare(l0, AL, allo_FN, is_inside_func=is_in_f)
            # understand the type of declarations, if it is not "allocatable"
            elif FJ.is_allocate(L1):
                # allocate(eigval_opt(num_bands,num_kpts),stat=ierr)
                lines[i] = FJ.write_allocate(l0, FJ.allocate_who(L1), allocatables, FN)
            elif FJ.is_deallocate(L1):
                # deallocate(eigval_opt,stat=ierr)
                lines[i] = FJ.write_deallocate(l0, FJ.deallocate_who(L1))
            elif FJ.is_public_export(L1) and FJ.is_contain_save(L1):
                # do not contain 'allocatable' but contain both 'public' and 'save'
                lines[i] = FJ.write_Ndeclare(l0, FJ.Ndeclare_who(L1))
            elif FJ.is_DIRECT_public_export(L1):
                # something like "public :: ..."
                lines[i] = FJ.write_export(l0)
            elif FJ.is_contain_save(L1):
                # http://www.fortran.com/fortran/books/t90_82.html
                # https://stackoverflow.com/questions/2893097/fortran-save-statement
                pass  # TODO
            elif FJ.is_bare_declare(L1):
                # if is a declare but not is_DIRECT_public_export and not contain save
                # example:
                lines[i] = FJ.write_bare_declare(l0)
            elif FJ.is_use(L1):
                pass
            elif FJ.is_contain_parameter(L1):
                pass
            else:
                if ('io_error' not in L1) and \
                   ('implicit none' not in L1) and \
                   ('contains' not in L1) and \
                   ('module' not in L1):
                    print("[INFO:DECLARE] UNPROCESSED : " + L1)

    for i, l in enumerate(lines):
        if FJ.is_module(l) or FJ.is_end_module(l):
            lines[i] = FJ.remove_FORTRAN_CONTROL_label(l)

    return "\n".join(lines)
