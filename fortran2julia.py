#!/usr/bin/env python
# coding: utf-8
# ---------------------------------------------------

from os.path import dirname
import sys
sys.path.append('/home/yunlong/Dropbox/First_Principle_Calculations/codes/fortran2julia/')

# ---------------------------------------------------

import re
import os
import json
from collections import deque

# you should verify "md5sum PatternCollection.py" and get exactly the following
# 40d4cba4e1b7211163eb7920470cd303  PatternCollection.py
import PatternCollection as PC
import Utinity as UT
import ParseFMT
import ParseLit


# ---------------------------------------------------
#
# rules and pattern matching
#
# ---------------------------------------------------


def is_blah(s, blah):
    return (blah.search(s) is not None)


def APPLY_RULES(S,RULE):
    S2 = S[:]
    for rf,rj in RULE:
        S2 = S2.replace(rf,rj)
    #end #for
    return S2


def SUB_RULES(S,RULE):
    S2 = S[:]
    for rf,rj in RULE:
        S2 = re.sub(rf,rj,S2)
    #end #for
    return S2


# ---------------------------------------------------
#
# comments
#
# ---------------------------------------------------


def is_julia_comment(s):
    return (s.strip()[0]=='#')


def is_fortran_comment(s):
    return (s.lstrip()[0]=='!')


def separate__comments(s, sep):
    for i in range(len(s)):
        if s[i]==sep and (not UT.inside_quote(s,i)):
            return s[:i],s[i:]
    return (s,'')


def separate_julia_comments(s):
    return separate__comments(s,'#')


def separate_fortran_comments(s):
    return separate__comments(s,'!')


def correct_tail_fortran_comments(s):
    if is_fortran_comment(s) or is_julia_comment(s):
        return s
    else:
        p = separate_fortran_comments(s)
        if len(p)==2:
            return p[0] + ((" #" + p[1]) if len((p[1].strip()))>0 else '')
        else:
            return s


def commenting_out(s):
    s2 = s.strip()
    for c,p in zip(PC.comm_list, PC.comm_patt):
        if is_blah(s2,p) and s2.startswith(c):
            return "#FORTRAN_CONTROL " + s2

    for c,p in zip(PC.comm_list_select, PC.comm_patt_select):
        if is_blah(s2,p) and s2.startswith(c):
            return "#FORTRAN_SELECT " + s2

    if is_blah(s2, PC.if_deallo_patt):
        return "#FORTRAN_CONTROL " + s2

    if is_blah(s2, PC.if_allo_patt):
        return "#FORTRAN_CONTROL " + s2

    return s2


def is_FORTRAN_CONTROL(s):
    return is_blah(s, PC.FORTRAN_CONTROL_patt)


def unpack_FORTRAN_CONTROL(s):
    if not is_FORTRAN_CONTROL(s):
        return [None, None, None]
    else:
        L = PC.FORTRAN_CONTROL_patt.split(s)
        assert len(L)>1
        L1, Comm = separate_julia_comments(L[1])
        return [L[0], L1.strip().lower(), Comm]


def process_fortran_comments(s):
    return APPLY_RULES(s, PC.comment_repl_rule)


# ---------------------------------------------------
#
# quotes and // concat
#
# ---------------------------------------------------


def replace_string_concat_simple(x):
    special_ch = [(r"\$",'\\$'), (r"\\",'\\\\'), (r"\"",'\\\"')]  # TOUCHE PAS !!!
    pieces = x.split("//")  # //
    combined = []
    for y in pieces:
        s = y.strip()
        # replace the outer-most ' ... ' by " ... "
        if s.startswith("'") and s.endswith("'") and is_blah(s, PC.single_quote_string_patt):
            s = '"' + SUB_RULES(s[1:-1],special_ch) + '"'
            combined.append(s)
        else:
            combined.append(y)
        #end #if
    #end #for
    return " * ".join(combined)


# ---------------------------------------------------
#
# call func(...)
#
# ---------------------------------------------------


def correct_function_calls(s):
    if (is_julia_comment(s) or is_fortran_comment(s)):
        return s

    NQ = UT.non_quote(s)
    m0 = [str(x.group(0)) for x in PC.func_patt_no_bra.finditer(NQ)]
    m = [str(x.group(0)) for x in PC.func_patt_simple.finditer(NQ)]

    if len(m0) == len(m):
        if len(m) == 0:
            return s
        else:
            assert m[0] in s
            function_head = m[0].strip()[4:-1].strip()
            sl, sr = s.split(m[0])
            srX, srCOMM = separate_julia_comments(sr)
            if srX.strip().endswith(')'):
                params = UT.split_on_toplevel_comma(srX.strip()[:-1])
                srX = ", ".join( [replace_string_concat_simple(p) for p in params] )
                ret = sl + " " + function_head + "( " + srX + " )  " + srCOMM
                return ret
            elif srX.strip().endswith('end'):
                srX1 = srX.strip()[:-3]
                if srX1.strip().endswith(')'):
                    params = UT.split_on_toplevel_comma(srX1.strip()[:-1])
                    srX1 = ", ".join( [replace_string_concat_simple(p) for p in params] )
                    ret = sl + " " + function_head + "( " + srX1 + " )  end " + srCOMM
                    return ret
                else:
                    print("[WARNING:CORRECT_FUNC_NAME]  " + s)
                    return s
            else:
                print("[WARNING:CORRECT_FUNC_NAME]  " + s)
                return s  # failed
            #end #if
        #end #if
    elif len(m0) > len(m):
        assert len(m) == 0
        assert len(m0) == 1
        assert m0[0] in s
        function_head = m0[0].strip()[4:].strip()
        sl, sr = s.split(m0[0])
        srX, srCOMM = separate_julia_comments(sr)
        if srX.strip().endswith('end'):
            srX1 = srX.strip()[:-3]
            if len(srX1.strip()) > 0:
                print("[WARNING:CORRECT_FUNC_NAME]  " + s)
                return s
            else:
                ret = sl + " " + function_head + "()  end " + srCOMM
                return ret
        else:
            print("[WARNING:CORRECT_FUNC_NAME]  " + s)
            return s  # failed
        #end #if
    else:
        print("[WARNING:CORRECT_FUNC_NAME]  " + s)
        return s
    #end #if


#sss = "    if (not_scannable  &&  nfermi != 1)  io_error( 'the berry_task(s) you chose require that you specify a single '  * 'fermi energy: scanning the fermi energy is not implemented')  end #if"
#sss = "if(write_vdw_data .and. disentanglement .and. num_valence_bands.le.0)  call io_error('If writing vdw data and disentangling' // ' then num_valence_bands must be defined') "
#correct_io_error(sss)


# ---------------------------------------------------
#
# one-line if
#
# ---------------------------------------------------


def is_fortran_one_line_if(s0):
    if is_fortran_comment(s0) or is_julia_comment(s0):
        return False
    s = s0.lstrip()
    return ( s.startswith('if') and ( 'then' not in UT.non_quote(separate_julia_comments(s)[0]) ) )


#sss = "if(write_vdw_data .and. disentanglement .and. num_valence_bands.le.0) call io_error('If writing vdw data and disentangling then num_valence_bands must be defined') "
#is_fortran_one_line_if(sss)


def complete_fortran_one_line_if(s):
    XX, comm = separate_julia_comments(s)
    return XX + '  end #if   ' + comm


def bracket_conditions(s):
    if is_julia_comment(s) or is_fortran_comment(s):
        return s
    else:
        ss, comm = separate_julia_comments(s.strip())
        ss = ss.strip()
        comm = ("  "+comm if len(comm)>0 else comm)
        if str(ss[0:2])==str("if") and str(ss[-4:])==str("then"):
            ss = ss[2:-4].strip()
            if not (ss[0] == '(' and ss[-1] == ')'):
                ss = '(' + ss.strip() + ')'
            elif (ss[0] == '(' and ss[-1] == ')'):
                ss = '(' + ss[1:-1].strip() + ')'
            else:
                pass
            #end #if
            return 'if ' + ss + ' then' + comm
        else:
            # maybe one-line-if
            return s
        #end #if
    #end #if


#bracket_conditions("if        x==2 && ( k   )                  then")


# ---------------------------------------------------
#
# simple replace
#
# ---------------------------------------------------


def fortran_logic_julia(s):
    return APPLY_RULES(s, PC.logic_rules)


def fortran_number_julia(s):
    return APPLY_RULES(s, PC.number_rules)


def fortran_eq_julia(s):
    return SUB_RULES(s, PC.eq_rules)


def fortran_control_julia(s):
    return SUB_RULES(s, PC.control_rules)


def fortran_misc_julia(s):
    return SUB_RULES(s, PC.misc_rules)


def fortran_to_julia_replace(s):
    s2 = str(s.strip())
    if len(s2) == 0:
        return ''
    elif is_fortran_comment(s2):
        return s2
    elif is_ifdef_label(s2):
        return s2.replace('#endif','#end #ifdef')
    else:
        s2 = s2.replace('! ','# ')  # comments at the end of line
        # control
        s2 = fortran_control_julia(s2)
        # =
        s2 = fortran_eq_julia(s2)
        # logic
        s2 = fortran_logic_julia(s2)
        # numbers
        s2 = fortran_number_julia(s2)
        # other
        s2 = fortran_misc_julia(s2)
        return s2
    #end #if


# ---------------------------------------------------
#
# correct array notations only in assignment
#
# ---------------------------------------------------


def is_assignment(s0):
    if is_fortran_comment(s0) or is_julia_comment(s0):
        return False
    s = s0.strip()
    if any((s.startswith(e)) for e in PC.excluded_arrayhead) or any((k in s) for k in PC.fortran_kwords) or ('=' not in s):
        #print("rejected: "+s)
        return False
    else:
        #print("accepted: "+s)
        qs = PC.ass_patt.search(s)
        qr = PC.array_patt.search(s)
        return (qr is not None) and (qs is not None)
    #end #if


#sss = "dos_k(loop_f,1)=dos_k(loop_f,1)+rdum * r_num_elec_per_state"
#is_assignment(sss)


def split_assignment(s):
    return (s.split(PC.eq_sign_patt.search(s).group(0)) \
            if (('=' in s) and ('==' not in s)) \
            else [s,''])


#sss = "$@%$==          324115$%@#^%TC@G"
#split_assignment(sss)


def ARRfortran2julia(s):
    conf = [x for x in PC.array_patt.finditer(s)]
    assert len(conf)==1 and conf[0].group(0) == s
    arrayhead = s.split('(')[0]
    if (arrayhead in PC.excluded_arrayhead) or (arrayhead in PC.fortran_kwords):
        return s
    else:
        arrayind = s.replace(arrayhead,'')
        assert len(arrayind)>2
        assert arrayind[0]=='(' and arrayind[-1]==')'
        return arrayhead + '[' + arrayind[1:-1] + ']'
    #end #if


def rewrite_fortran_array_to_julia(s):
    if is_assignment(s):
        SPList = split_assignment(s)
        for (i,sp) in enumerate(SPList):
            sp_expr = PC.array_patt.finditer(sp)
            for x in sp_expr:
                arr_fortr = str(x.group(0))
                assert (arr_fortr in s)
                arr_julia = ARRfortran2julia(arr_fortr)
                SPList[i] = SPList[i].replace(arr_fortr, arr_julia)
            #end #for
        return " = ".join(SPList)
    else:
        return s
    #end #if




def process_array_colon_expr(s0):
    if is_julia_comment(s0.strip()) or (':' not in s0):
        return s0

    array_exprs = set([str(x.group(0)) for x in PC.array_colon_expr_patt.finditer(s0)])
    if len(array_exprs)==0:
        return s0

    s = s0[:]
    for a in array_exprs:
        assert a in s0
        new_a = a.replace('(','[').replace(')',']')
        s = s.replace(a,new_a)
    #end #for

    return s


#sss = "s(:,:) = (y(:)+s(:,:)*2)"
#process_array_colon_expr(sss)

#ST = "pw90common_fourier_R_to_k_new(kpt,HH_R,OO = HH,OO_dx = delHH(:,:,1),OO_dy = delHH(:,:,2),OO_dz = delHH(:,:,3))"
#ST = "orig(i) = real(istart(1)-1,dp)*dgrid(1)*real_lattice(1,i)/moda(1) + real(istart(2)-1,dp)*dgrid(2)*real_lattice(2,i)/moda(2) + real(istart(3)-1,dp)*dgrid(3)*real_lattice(3,i)/moda(3)"
#sss = "dos_k(loop_f,1)=dos_k(loop_f,1)+rdum * r_num_elec_per_state"
#is_assignment(sss)
#rewrite_fortran_array_to_julia(sss)


# ---------------------------------------------------
#
# format string and format line
#
# ---------------------------------------------------


def unroll_fmt(s):
    s0 = s[:]
    brkts = UT.find_brackets(s)
    for i in range(len(s)):
        if i in brkts:
            if i!=0:
                pos_comma = -1
                for j in range(i-1,-1,-1):
                    if (s[j]==',' or s[j]=='('):
                        pos_comma = j
                        break
                    #end #if
                #end #for
                rep = int(s[pos_comma+1:i]) if (pos_comma+1<i) else 1
                s0 = s0.replace(s[pos_comma+1:brkts[i]+1],','.join([s[i+1:brkts[i]]] * rep))
            #end #if
        #end #if

    return s0


#NOTE
#sss = "702 format('set xtics (',:20('"',A3,'" ',F8.5,','))"
# colon ":" removed manually

# ss = '2((4E16.8),1x) '
# ss = '(1x,a9,10(1x,4x),(f10.4,1x)) '
# parse_fmt(unroll_fmt(ss))
# find_complemetary_ket(ss,1)
# ## is_...


def translate_fmt(s):
    return ParseFMT.parse_fmt(unroll_fmt(s.strip().strip("\'").strip()))


def is_format_line(s0):
    return is_blah(s0.strip('& '), PC.fmt_line_header_patt)


def update_format_lines(s0,format_lines):
    s = s0.strip()
    m = re.findall(r"\d{2}\d+",s)[0]
    s = s0.split(m)[1].strip()
    if (re.search(r"[Ff][Oo][Rr][Mm][Aa][Tt]\s*\(",s) is not None) and s.endswith(")"):
        #sf = parse_fmt(s.replace("format","")) #BUG
        #BUG previous version missed unroll_fmt
        sf = ParseFMT.parse_fmt( unroll_fmt(re.sub(r"[Ff][Oo][Rr][Mm][Aa][Tt]\s*",'',s)) )
        format_lines[m] = sf
    #end #if
    return (format_lines,m)

#NOTE
#sss = "702 format('set xtics (',:20('"',A3,'" ',F8.5,','))"
# colon ":" removed manually


# ---------------------------------------------------
#
# for sentence
#
# ---------------------------------------------------


def is_for(s):
    return (is_blah(s, PC.do_patt) or (s.strip()=="do"))


def is_end_for(s):
    return is_blah(s, PC.enddo_patt) and (not is_for(s))


def is_ok_do(s):
    return is_blah(s, PC.ok_do_patt)


def is_do_jump(s):
    return is_blah(s, PC.do_jump_patt)


def is_do_while(s):
    return is_blah(s, PC.do_while_patt)


def process_for(s0, OK_LABEL, JUMP):
    # ref = http://www.personal.psu.edu/jhm/f90/lectures/15.html
    if is_fortran_comment(s0) or is_julia_comment(s0):
        return s0

    if is_do_while(s0):
        return s0

    s, original_tail_comment = separate_julia_comments(s0)
    additional_tail = ''

    if s.strip()=="do":
        #empty for line
        return "while true" + original_tail_comment
    else:
        if is_ok_do(s.strip()):
            ok_do_str = re.search(r"\s*\w+\s*\:\s*do\s+", s).group(0)
            ok_do_label = ok_do_str.split(':')[0].strip()
            OK_LABEL.append(ok_do_label)
            additional_tail += ("  #DO OK #DO_OK_LABEL " + ok_do_label)
            s1 = re.sub(r"\s*\w+\s*\:\s*do\s+", '', s.strip())
        elif is_for(s.strip()):
            ok_do_str = re.search(r"\s*do\s+", s).group(0)
            ok_do_label = ''
            #OK_LABEL
            #additional_tail
            s1 = re.sub(r"\s*do\s+",'', s)
        else:
            return s + original_tail_comment
        #end #if

        if is_do_jump(s1):
            print( "[--- WARNING ---]  DO JUMP loop :  " + s )
            jump_to = re.search(r"\d+",s1).group(0)
            JUMP.append(jump_to)
            s1 = s1.replace(jump_to,'',1)
            additional_tail += (" #DO JUMP #JUMP_TO  " + jump_to)
        #end #if

        LLL = UT.split_on_toplevel_comma(s1.strip())

        if len(LLL) == 2:
            # for a,b
            return "for " + LLL[0].strip()+" : " + LLL[1].strip() + "  " + original_tail_comment + additional_tail
        elif len(LLL) == 3:
            return "for " + LLL[0].strip()+" : " + LLL[2].strip() + " : " + LLL[1].strip() + "  " + original_tail_comment + additional_tail
        elif len(LLL) > 3:
            print("[--- FAILED : process_for() ---]  " + s0)
            return s0
        #end #if
    #end #if



#sss =  "    do "
#sss = "dos_k(loop_f,1)=dos_k(loop_f,1)+rdum * r_num_elec_per_state"
#sss = "do i = 1 , 10 "
#is_for(sss)

#sss = "do    "
#sss = " O1:do i=0,(berry_curv_adpt_kmesh-1),100 # ORIGINAL COMMENT"
#sss = "OK: do 100 l=1,PRODUCT(dos_kmesh)-1,2"
#ok = []
#jp = []
#process_for(sss,ok,jp)

#sss = " 'the berry_task(s) you chose require that you specify a single '  * 'fermi energy: scanning the fermi energy is not implemented' "
#print(replace_string_concat_simple(sss))


def is_jump_line(s0):
    return (not is_format_line(s0)) and is_blah(s0[:6], PC.jump_line_header_patt)


def search_for_ok_label(s0, OK_LAB):
    s = s0[:].strip()
    for ok in OK_LAB:
        if ok in s:
            if ("cycle" in s):
                p = s.split("cycle")
                if len(p)>1:
                    p1 = "".join(p[1:])
                    if ok in p1:
                        p1 = p1.replace(ok,'',1)
                        return p[0] + "continue " + p1 + "#CYCLE OK #DO_OK_LABEL " + ok
            elif("exit" in s):
                p = s.split("exit")
                if len(p)>1:
                    p1 = "".join(p[1:])
                    if ok in p1:
                        p1 = p1.replace(ok,'',1)
                        return p[0] + "break " + p1 + "#EXIT OK #DO_OK_LABEL " + ok
            elif is_end_for(s):
                p = s.split("end")
                if len(p)>1:
                    p1 = "".join(p[1:])
                    if ok in p1:
                        p1 = p1.replace('do','',1).replace(ok,'',1)
                        return p[0] + "end #for" + p1 + "#END OK #DO_OK_LABEL " + ok
            else:
                pass
            #end #if
        #end #if
    #end #for
    return s0


#sss = "enddo ok"
#search_for_ok_label(sss,['ok'])


def process_jump_line(s0, JUMP_LINE):
    if is_julia_comment(s0):
        return s0
    elif is_jump_line(s0):
        s = s0.strip()
        header = PC.jump_line_header_patt.search(s).group(0).strip()
        if header not in JUMP_LINE:
            JUMP_LINE.append(header)
        #end #if
        return "#JUMP_LINE[" + header + "]  \"" + s.replace(header,'',1).strip() + "\""
    else:
        return s0
    #edn #if


#sss = "101 exit()"
#process_jump_line(sss,[])


# ---------------------------------------------------
#
# xxx
#
# ---------------------------------------------------


def is_ifdef_label(s):
    return (is_blah(s, PC.ifdef_patt) or is_blah(s, PC.else_patt) or is_blah(s, PC.endif_patt))


def is_multi_line(s0):
    s = s0.strip()
    pos_semicolon = []
    if not is_fortran_comment(s):
        for i in range(len(s)):
            if s[i]==';' and (not UT.inside_quote(s,i)):
                pos_semicolon.append(i)
            #end #if
        #end #for
    #end #if
    return (len(pos_semicolon)>0, UT.split_indx(s,pos_semicolon))


#sss = "  sfd=1,d=1;d*2"
#print(is_multi_line(sss))


# ---------------------------------------------------
#
# the write(...) command # TOUCHE PAS !!!
#
# ---------------------------------------------------


def replace_string_concat(x):  # used exclusively in write()
    special_ch = [(r"\$",'\\$'), (r"\\",'\\\\'), (r"\"",'\\\"')]  # DO NOT TOUCH, otherwise see you in HELL
    pieces = x.split("//")  # //
    combined = []
    for y in pieces:
        s = y.strip()
        # replace the outer-most ' ... ' by " ... "
        if s.startswith("'") and s.endswith("'") and is_blah(s, PC.single_quote_string_patt):
            s = '"' + SUB_RULES(s[1:-1],special_ch) + '"'
            combined.append(s)
        elif s.startswith('"') and s.endswith('"'):
            s = '"' + SUB_RULES(s[1:-1],special_ch) + '"'
            combined.append(s)
        else:
            if not ( ("'" not in s) and ('"' not in s) ):
                print("[WARNING '''']  " + x)
            combined.append(s)
        #end #if
    #end #for
    ret = ( "("+(" * ".join(combined))+")" )
    return ret


def process_literal_0(s0,sep,bracketing=False):  # used exclusively in write()
    slist = UT.split_on_toplevel_comma(s0.strip())
    ret = []
    for x in slist:
        tmp = replace_string_concat(x)
        ret.append(("string("+tmp+")" if bracketing else tmp))
    #end #for
    ret = sep.join(ret)
    if len(ret)==0:
        ret = ' " " '

    return ret


def process_literal_star(s0,bracketing=False):  # used exclusively in fortran_write_julia()
    return process_literal_0(s0," * ",bracketing=bracketing)


def process_literals(s0,bracketing=False):  # used exclusively in fortran_write_julia()
    return process_literal_0(s0,"  ",bracketing=bracketing)


def is_write(s0):
    s = s0.lstrip()
    return ( s[:5]=="write" and is_blah(s[:9], PC.write_crit_patt) )


def fortran_write_julia(s0,fmt_dict):
    line_plus_comm = separate_julia_comments(s0.strip())
    s = line_plus_comm[0]
    shead = s0.split("write")[0]

    search1 = PC.write_patt_adv.finditer(s)
    search2 = PC.write_patt_no_adv.finditer(s)
    search3n = PC.write_three_number_patt.finditer(s)
    search3no = PC.write_three_number_patt_no_adv.finditer(s)
    searchst = PC.write_star_patt.finditer(s)
    searchsto = PC.write_star_out_patt.finditer(s)
    searcha = PC.write_a_patt.finditer(s)
    searchnofmt = PC.write_no_fmt_patt.finditer(s)
    search_fmt = PC.write_FMT_patt_adv.finditer(s)

    for x in searchnofmt:
        write_bracket = x.group(0)
        out_name0 = re.sub(r"\s*write\s*\(\s*",'',write_bracket.strip())
        out_name = out_name0.strip(' )')
        res = shead + "@printf  " + out_name + "  \"%s\\n\"" +\
                    "  " + process_literal_star(s.replace(write_bracket,' '),bracketing=True) +\
                    line_plus_comm[1]
        return res

    for x in searcha:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].strip(" ,)").strip(" ,)")
        assert ('a' in fmt_fortran) or ('A' in fmt_fortran)
        res = shead + "@printf  " + out_name + "  \"%s\\n\"" +\
                    "  " + process_literal_star(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in search1:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].strip(" ,)").strip(" ,)")
        fmt_julia = '\"' + translate_fmt(fmt_fortran) + '\\n\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia +\
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in searchsto:
        write_bracket = x.group(0)
        out_name = ''
        fmt_fortran = write_bracket.split('*')[1].strip(' ,)')
        fmt_julia = '\"' + translate_fmt(fmt_fortran) + '\\n\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia +\
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in search_fmt:
        write_bracket = re.sub(r"[Ff][Mm][Tt]\s*\=", '', x.group(0))
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].strip(" ,)").strip(" ,)")
        fmt_julia = '\"' + translate_fmt(fmt_fortran) + '\\n\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia +\
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in search2:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].split('advance')[0].strip(" ,)").strip(" ,)")
        fmt_julia = '\"' + translate_fmt(fmt_fortran) + '\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia +\
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in search3n:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].strip(" ,)").strip(" ,)")
        fmt_julia = '\"'+fmt_dict[fmt_fortran]+'\\n\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia +\
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in search3no:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].split('advance')[0].strip(" ,)").strip(" ,)")
        fmt_julia = '\"'+fmt_dict[fmt_fortran]+'\"'
        res = shead + "@printf  " + out_name + "  " + fmt_julia + \
                    "  " + process_literals(s.replace(write_bracket,' ')) +\
                    line_plus_comm[1]
        return res

    for x in searchst:
        write_bracket = x.group(0)
        out_name0 = str(PC.write_head_firstarg_patt.match(write_bracket).group(0))
        out_name = re.sub(r"\s*write\s*\(\s*",'',out_name0.strip(" ,"))
        fmt_fortran = write_bracket.split(out_name)[1].strip(" ,)").strip(" ,)")
        assert fmt_fortran=='*'
        res = shead + "@printf  " + out_name + "  \"%s\\n\"" +\
                        "  " + process_literal_star(s.replace(write_bracket,' ')) +\
                        line_plus_comm[1]
        return res

    print("[FAIL:fortran_write_julia()]\n[FAIL]  " + s0)
    return s0


#sss = "write(*,'(4(F12.6,1x)) ') fermi_energy_list(if),sum(ahc_list(:,1,if)),[sum(ahc_list(:,2,if))],sum(ahc_list(:,3,if))"
#sss = "write(stdut,'(4(F12.6,1x)) ') fermi_energy_list(if),sum(ahc_list(:,1,if)),[sum(ahc_list(:,2,if))],sum(ahc_list(:,3,if))"
#sss = "write(bnddataunit(n),'(3E16.8)') kpt_x,kpt_y,eig(n)"
#sss = "write(bnddataunit) kpt_x,kpt_y,eig(n)"
#print(fortran_write_julia(sss,{}))



# ---------------------------------------------------
#
# xxx
#
# ---------------------------------------------------


def is_end_func(s):
    return is_blah(s, PC.end_func_patt)


def is_func(s):
    if is_julia_comment(s) or ('"' in s) or ("'" in s) or is_end_func(s):
        return False
    else:
        return is_blah(s, PC.func_patt)


def get_func_name(s):
    if is_func(s):
        parts = s.strip().split("function ")
        if (len(parts)>2) and any(('#' in k) for k in parts[1:]):
            part2,comm = separate_julia_comments( ("".join(parts[1:])).strip() )
        part2, comm = separate_julia_comments( parts[1].strip() )
        if ('(' in part2) and (')' in part2):
            return (part2.split('(')[0].strip())
        elif ('[' in part2) and (']' in part2):
            return (part2.split('[')[0].strip())
        else:
            return part2.strip()
        #end #if
    elif is_end_func(s):
        parts = s.strip().split("function ")
        assert ('#' in parts[0]) and (len(parts)==2)
        return parts[1].strip()
    else:
        return ''
    #end #if


#sss = "  function s() #([l])"
#get_func_name(sss)


def correct_func_name(s,FUNCS):
    if (is_julia_comment(s.strip()) or is_fortran_comment(s.strip())):
        return s

    if is_func(s):
        fn = get_func_name(s)
        if len(fn)>0:
            parts = s.split(fn)
            if not parts[1].strip().startswith('('):
                return parts[0]+fn+"() "+("".join(parts[1:]))
            else:
                return parts[0] + fn + (parts[1].strip()) + " " + ("".join(parts[2:]))
            #end #if
        else:
            return s
        #end #if
    else:
        s1 = s[:]
        for fn in FUNCS:
            if fn not in PC.fortran_kwords:
                s2 = s1[:]
                matched = set([m.start() for m in re.finditer(fn, s1)])
                while True:
                    if len(matched)==0:
                        break
                    else:
                        matched1 = set(list(matched))
                        for k in matched1:
                            b = k-1+len(fn)+1
                            if b<len(s1):
                                if s1[b]=='(':  # with a bra
                                    matched.remove(k)
                                elif s1[b]=='[':
                                    matched.remove(k)
                                else:  # without a bra
                                    s2 = s1[:b]+"()"+s1[b:]
                                    matched.remove(k)
                                    break
                                #end #if
                            #end #if b<len(s1):
                        #end #for
                    #end #if
                #end #while
                s1 = s2[:]
            #end #if fn not in fortran_kwords:
        #end #for

        return s1
    #end #if


#sss = "if (f1 [3]==2) = f2 () + f3(l)"
#FFF = ['f1']
#correct_func_name(sss,FFF)


# ---------------------------------------------------
#
# xxx
#
# ---------------------------------------------------


def extract_array_names(s0):
    array_names = []
    s = s0[:]
    array_all = [str(x.group(0)) for x in PC.array_head_patt.finditer(s)]
    for y in array_all:
        if y[:-1] not in PC.fortran_kwords:
            array_names.append(y[:-1])
        #end #if
    #end #for
    return array_names


def correct_array_brackets(s, ARRN, FUNCS):

    if is_func(s.strip()) or is_julia_comment(s.strip()) or is_fortran_comment(s.strip()):
        return s

    s1 = s[:]
    brkts = UT.find_brackets(s1)
    s1tmp = s1[:]

    for an in ARRN:
        if ((an not in FUNCS) and (an not in PC.fortran_kwords)) and (an+'(' in s1tmp):
            starts = [m.start() for m in re.finditer(an, s1)]
            for k in starts:
                b = k-1+len(an)+1
                if b<len(s1) and (not UT.inside_quote(s1,b)):
                    if s1[b]=='(':  # incorrect bracket
                        b_end = brkts[b]
                        assert s1[b_end]==')'
                        s1 = s1[:b]+'['+s1[b+1:]
                        s1 = s1[:b_end]+']'+(s1[b_end+1:] if (b_end+1 < len(s1)) else '')
                    else:
                        pass
                    #end #if
                #end #if
            #end #for
        else:
            pass
        #end #if
    #end #for

    brkts2 = UT.find_brackets(s1, bleft='[', bright=']')
    s1tmp = s1[:]
    for an in ARRN:
        if ((an in FUNCS) or (an in PC.fortran_kwords)) and (an+'[' in s1tmp):
            starts = [m.start() for m in re.finditer(an, s1)]
            for k in starts:
                b = k-1+len(an)+1
                if b<len(s1) and (not UT.inside_quote(s1,b)):
                    if s1[b]=='[':  # incorrect bracket
                        b_end = brkts2[b]
                        assert s1[b_end]==']'
                        s1 = s1[:b]+'('+s1[b+1:]
                        s1 = s1[:b_end]+')'+(s1[b_end+1:] if (b_end+1<len(s1)) else '')
                    else:
                        pass
                    #end #if
                #end #if
            #end #for
        else:
            pass
        #end #if
    #end #for
    brkts3 = UT.find_brackets(s1, bleft='[', bright=']')
    s1tmp = s1[:]
    for an in FUNCS:
        if (an+'[' in s1tmp):
            starts = [m.start() for m in re.finditer(an, s1)]
            for k in starts:
                b = k-1+len(an)+1
                if b < len(s1) and (not UT.inside_quote(s1, b)):
                    if s1[b] == '[':
                        #incorrect bracket
                        b_end = brkts3[b]
                        assert s1[b_end]==']'
                        s1 = s1[:b]+'('+s1[b+1:]
                        s1 = s1[:b_end]+')'+(s1[b_end+1:] if (b_end+1<len(s1)) else '')
                    else:
                        pass
                    #end #if
                #end #if
            #end #for
        #end #if
    #end #for
    return s1


#sss = "    write(chk_unit) (wannier_spreads(i),i=1,num_wann)"
#FFF = ['f1','f2','f3','wannier_spreads']
#sss = "f1(3) = f3(2) + f2(l) + f3[1]"
#sss = "function f1()"
#AAA = ['f1','a2','a3']
#FFF = ['f2','f']
#correct_array_brackets(sss,AAA,FFF)


#sss = "  complex(kind=dp), public, save, allocatable ::  HH_R(:,:,:) #  <0n|r|Rm>"
#allocatable_patt.split(sss)



# ---------------------------------------------------
#
# detect modules
#
# ---------------------------------------------------


def is_end_module(s):
    if not is_FORTRAN_CONTROL(s):
        return False
    else:
        return is_blah(s, PC.end_module_patt)


def is_module(s):
    if not is_FORTRAN_CONTROL(s):
        return False
    else:
        return (is_blah(s, PC.module_patt) and (not is_blah(s, PC.module_procedure_patt)) and (not is_end_module(s)))


def get_module_name(s):
    return s.split("module")[1].strip()


# ---------------------------------------------------
#
# declare, allocate, deallocate
#
# ---------------------------------------------------


def is_public(s,vn):
    assert is_julia_comment(s.strip()) and (vn in s)
    return is_blah(s, PC.public_patt)


#sss = "#FORTRAN_CONTROL logical,           public, save :: disentanglement"
#is_public(sss,"disentanglement1")


def is_save(s,vn):
    assert is_julia_comment(s.strip()) and (vn in s)
    return is_blah(s, PC.save_patt)


#sss = "#FORTRAN_CONTROL logical,           public, save :: disentanglement"
#is_save(sss,"disentanglement")


def is_public_export(s):
    return is_blah(s.lower(), PC.public_vars_patt) and (not is_blah(s, PC.allocatable_patt))


def is_DIRECT_public_export(s):
    return is_blah(s.lower(), PC.DIRECT_public_patt)


def is_contain_save(s):
    return is_blah(s.lower(), PC.save_vars_patt) and (not is_blah(s, PC.allocatable_patt))


def is_deallocate(s):
    return is_blah(s.lower(), PC.deallocate_array_patt) and (not is_blah(s.lower(), PC.if_err_patt))


def is_allocate(s):
    return (is_blah(s.lower(), PC.allocate_array_patt) \
            and (not is_blah(s.lower(), PC.deallocate_array_patt)))\
            and (not is_blah(s.lower(), PC.if_err_patt))


# lower:upper to specify both lower and upper bounds (i.e. lower ≤ expr ≤ upper)
def is_iter(itr):
    return is_blah(itr, PC.iter_patt)


def len_iter(itr0):
    return "length(" + itr0.strip() + ")"



def find_allocatable(s):
    if PC.allocatable_patt.search(s) is not None:
        is_sav0 = ("save" in s)
        is_pub0 = ("public" in s)
        XXX = s.strip().split("::")
        allo = XXX[0]
        vars,comment = separate_fortran_comments("".join(XXX[1:]))
        typ = [PC.var_types[reg] for reg in PC.var_types.keys() if reg.search(allo) is not None]
        assert len(typ)==1
        typ = typ[0]
        Naxes = PC.dim_patt.search(allo)
        if Naxes is not None:
            assert PC.allo_vars_patt.search(vars) is None
            Var_list = [x.strip() for x in vars.split(',')]
            # number of colons ':'
            Naxes = Naxes.group(0).count(':')
            Naxes_list = [Naxes for x in Var_list]
            Type_list = [typ for x in Var_list]
        else:
            var_list0 = [str(v.group(0)).strip() for v in PC.allo_vars_patt.finditer(vars)]
            Naxes_list = [v.count(':') for v in var_list0]
            Var_list = [PC.bracket_colon_patt.sub('',v).strip() for v in var_list0]
            Type_list = [typ for x in Var_list]
        #end #if
        SAV = [is_sav0 for x in Var_list]
        PUB = [is_pub0 for x in Var_list]
        # name, typ, naxes, is_save, is_pub
        return list(zip(Var_list,Type_list,Naxes_list, SAV, PUB))
    else:
        return []
    #end #if


#sss = "       real(DP),allocatable,public :: wdist_wssc_frac(:,:,:,:), irdist_real(:,:,:,:,:)"
#sss = "    real(kind = dp), allocatable :: singv(:,:,:), singvv(:,:)"
#sss = "  real(kind=dp),    allocatable  :: rnkb (:,:,:)   "
#find_allocatable(sss)

#split_on_toplevel_comma("a(x,y,z),b(:,:)")
#allocate_array_patt.split("if()allocate(c)")

def allocate_who(s):
    #NOTE no comments in s
    #a = allocate_array_patt.sub('(',stat_patt.sub('',s.lower().strip())).strip()
    al, ar = PC.allocate_array_patt.split( s.lower().strip() )
    a0 = '(' + PC.stat_patt.sub('',ar).strip()
    a = a0[:-3].strip() if a0.endswith("end") else a0
    if not (a[0]=='(' and a[-1]==')'):
        print("[ERROR:allocate_who] " + a0)
        assert False
    who = []
    for arr in UT.split_on_toplevel_comma(a[1:-1]):
        nam = PC.allo_name_patt.search(arr.replace(' ','')).group(0).rstrip(' (')
        shp0 = PC.allo_shape_patt.search(arr.replace(' ','')).group(0).strip().replace(' ','')
        assert shp0[0]=='(' and shp0[-1]==')'
        shp = UT.split_on_toplevel_comma(shp0[1:-1])
        for i,sp in enumerate(shp):
            if is_iter(sp):
                shp[i] = len_iter(sp)
            #end #if
        #end #for
        # name, shape_str, Naxes
        who.append( ( nam.replace(' ',''), "("+(",".join(shp))+")", len(shp) ) )
    #end #for
    return who


#sss = "    ALLOCATE(irdist_real(3,ndegenx,num_wann,  num_wann,nrpts))"
#sss = "       allocate(nncell_tmp(3,num_kpts,nntot) )"
#allocate_array_patt.sub('(',stat_patt.sub('',sss.lstrip()))
#allocate_who(sss)


def deallocate_who(s):
    #print("[deallocate_who] "+s)
    #a = deallocate_array_patt.sub('(',stat_patt.sub('',s.lstrip())).strip()
    al, ar = PC.deallocate_array_patt.split( s.lower().strip() )
    a0 = '(' + PC.stat_patt.sub('',ar).strip()
    a = a0[:-3].strip() if a0.endswith("end") else a0
    if not ( a[0]=='(' and a[-1]==')' ):
        print("[ERROR:deallocate_who]  " + a0)
        assert False
    return [ x.strip().replace(' ','') for x in UT.split_on_toplevel_comma(a[1:-1]) ]


def Ndeclare_who(s):
    #name, typ, is_save, is_pub
    if (PC.allocatable_patt.search(s) is None):
        is_pub0 = is_public_export(s)
        is_sav0 = is_contain_save(s)
        XXX = s.strip().split("::")
        allo = XXX[0]
        vars,comment = separate_fortran_comments("".join(XXX[1:]))
        typ = [PC.var_types[reg] for reg in PC.var_types.keys() if reg.search(allo) is not None]
        assert len(typ)==1
        typ = typ[0]
        Var_list0 = [x.strip().split('=') for x in vars.split(',')]
        Var_list = [((x[0],None) if len(x)==1 else (x[0],x[1])) for x in Var_list0]
        Type_list = [typ for x in Var_list0]
        SAV = [is_sav0 for x in Var_list0]
        PUB = [is_pub0 for x in Var_list0]
        # name, typ, naxes, is_save, is_pub
        return list(zip(Var_list,Type_list, SAV, PUB))
    else:
        return []


def process_allocate(name, typ, shape):
    return ( "@allocate " + "  ".join([name, typ, shape]) )


def process_deallocate(deallo_name):
    return ( "@deallocate  " + deallo_name )


def process_declare(name, typ, naxes):
    return "@declare  " + (" ".join([name, typ, str(naxes)]))


def process_Ndeclare(name, value, typ):
    if value is None:
        #macro Ndeclare(A, T)
        return "@Ndeclare  " + (" ".join([name, typ]))
    else:
        #macro Ninit(A, T, V)
        return "@Ninit  " + (" ".join([name, typ, ParseLit.parse_number(value)]))


def write_export(sraw):
    if not is_julia_comment(sraw):
        print("[WARNING]  should have been commented out --> " + sraw)
        return sraw

    shead, L1, COMM = unpack_FORTRAN_CONTROL(sraw)
    L1 = "".join(L1.split("::")[1:])

    return shead + "export " + (", ".join( [v.strip() for v in L1.split(',')] )) + COMM


def write_deallocate(sraw, WHO):
    if not is_julia_comment(sraw):
        print("[WARNING]  should have been commented out --> " + sraw)
        return sraw
    elif len(WHO)==0:
        print("[WARNING]  nothing to deallocate --> " + sraw)
        return sraw

    output_lines = []
    is_oneline_if = False
    shead, L1, COMM = unpack_FORTRAN_CONTROL(sraw)

    if L1.startswith("if") and L1.endswith("end"):
        is_oneline_if = True
        L1_if_head = L1.split("deallocate")[0].strip()
        output_lines.append(shead + fortran_to_julia_replace(L1_if_head))
        shead = "    " + shead

    for name in WHO:
        assert name in L1
        output_lines.append(shead + process_deallocate(name) + " " + ("" if is_oneline_if else COMM) )

    if is_oneline_if:
        output_lines.append(shead[4:] + "end " + COMM)

    ret = "\n".join(output_lines)

    return ret


def write_allocate(sraw, WHO, all_allo_dict, FN):
    if not is_julia_comment(sraw):
        #print("[WARNING]  should have been commented out --> " + sraw)
        return sraw
    elif len(WHO)==0:
        #print("[WARNING]  nothing to allocate --> " + sraw)
        return sraw

    output_lines = []
    is_oneline_if = False
    shead, L1, COMM = unpack_FORTRAN_CONTROL(sraw)

    if L1.startswith("if") and L1.endswith("end"):
        is_oneline_if = True
        L1_if_head = L1.split("allocate")[0].strip()
        output_lines.append(shead + fortran_to_julia_replace(L1_if_head))
        shead = "    " + shead

    for (name,shape,naxes) in WHO:
        is_locally_declared = True
        FN2 = ''
        assert name in L1
        if name not in all_allo_dict[FN].keys():
            is_locally_declared = False
            for fn_i in all_allo_dict.keys():
                if name in all_allo_dict[fn_i].keys():
                    FN2 = fn_i
                    break
        if (not is_locally_declared) and FN2 == '':
            print("[ERROR:write_allocate] KeyError for name = " + name + " in file " + FN)
            return sraw

        type = all_allo_dict[FN][name]['type'] if is_locally_declared else all_allo_dict[FN2][name]['type']
        output_lines.append(shead + process_allocate(name, type, shape) + ("" if is_oneline_if else " "+COMM))

    if is_oneline_if:
        output_lines.append(shead[4:] + "end " + COMM)

    ret = "\n".join(output_lines)

    return ret


def write_declare(sraw, WHO, allo_dict):
    if not is_julia_comment(sraw):
        #print("[WARNING]  should have been commented out --> " + sraw)
        return sraw
    elif len(WHO)==0:
        #print("[WARNING]  nothing to declare --> " + sraw)
        return sraw

    public_vars = []
    output_lines = []
    shead, L1, COMM = unpack_FORTRAN_CONTROL(sraw)

    for (name, typ, naxes, is_save, is_pub) in WHO:
        output_lines.append( shead + process_declare(name, typ, naxes) +"  "+ COMM)
        if is_pub:
            public_vars.append(name)
        if is_save:
            pass  #TODO what does save mean in fortran ?

    pub_line = "" if len(public_vars)==0 else (shead + "export  " + ", ".join(public_vars) +"  "+ COMM + "\n")
    ret = pub_line + ("\n".join(output_lines))

    return ret


def write_Ndeclare(sraw, WHO):
    if not is_julia_comment(sraw):
        #print("[WARNING]  should have been commented out --> " + sraw)
        return sraw
    elif len(WHO)==0:
        #print("[WARNING]  nothing to declare --> " + sraw)
        return sraw
    output_lines = []
    PV = []
    shead, L1, COMM = unpack_FORTRAN_CONTROL(sraw)
    for (name_value, typ, is_save, is_pub) in WHO:
        name, value = name_value
        if is_pub:
            PV.append(name)
        output_lines.append( shead + process_Ndeclare(name, value, typ) +"  "+ COMM)

    pub_line = "" if len(PV)==0 else (shead + "export  " + ", ".join(PV) +"  "+ COMM + "\n")
    ret = pub_line + ("\n".join(output_lines))

    return ret


def where_is_the_line(i, fdic, mdic):
    inside_any_module = False
    inside_any_function = False
    ret_m = None
    ret_f = None
    for m in mdic.keys():
        (bm, em) = mdic[m]
        if bm < i and em > i:
            inside_any_module = True
            ret_m = m
            break
        else:
            continue

    if not inside_any_module:
        ret_m = ([m for m in mdic.keys() if ("_outside_all_modules" in m)])[0]

    for f in fdic.keys():
        (bf, ef) = fdic[f]
        if "_no_function" in f:
            inside_any_function = True
            ret_f = f
            break
        elif bf < i and ef > i:
            inside_any_function = True
            ret_f = f
            break

    if not inside_any_function:
        ret_f = None

    return ret_m, ret_f




'''
def correct_io_error(s):
    if (is_julia_comment(s) or is_fortran_comment(s)):
        return s

    m = [str(x.group(0)) for x in PC.io_error_patt_simple.finditer(s)]

    if len(m) == 0:
        return s
    else:
        assert m[0] in s
        sl, sr = s.split(m[0])
        srX, srCOMM = separate_julia_comments(sr)
        if srX.strip().endswith(')'):
            params = UT.split_on_toplevel_comma(srX.strip()[:-1])
            srX = ", ".join( [replace_string_concat_simple(p) for p in params] )
            ret = sl + "io_error( " + srX + " )  " + srCOMM
            return ret
        elif srX.strip().endswith('end'):
            srX1 = srX.strip()[:-3]
            if srX1.strip().endswith(')'):
                params = UT.split_on_toplevel_comma(srX1.strip()[:-1])
                srX1 = ", ".join( [replace_string_concat_simple(p) for p in params] )
                ret = sl + "io_error( " + srX1 + " )  end " + srCOMM
                return ret
            else:
                return s

        else:
            return s  # failed

'''
