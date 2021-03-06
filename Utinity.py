
import os
import re
import json
from collections import deque


def split_indx(s, indx):
    if len(indx) == 0:
        return [s]
    else:
        assert all(i < len(s) for i in indx)
        res = []
        c = 0
        for i in indx:
            res.append(s[c:i])
            c = i+1
        #end #for
        if c < len(s):
            res.append(s[c:])
        #end #if
        return res
    #end #if


def inside_quote(s, i):
    double_quote_count = 0
    single_quote_count = 0
    for k in range(i):
        if s[k] == '"':
            if k == 0:
                double_quote_count += 1
            elif s[k-1] != '\\':
                double_quote_count += 1
            else:
                pass
            #end #if
        elif s[k] == "'":
            if k == 0:
                single_quote_count += 1
            elif double_quote_count % 2 == 0:
                #outside " ... "
                single_quote_count += 1
            else:
                pass
            #end #if
        #end #if
    #end #for
    return not (double_quote_count % 2 == 0 and single_quote_count % 2 == 0)




#sss = "'#    components of the TDF for the spin up, followed by those for the spin down) '"
#for i in range(len(sss)):
#    print(sss[i])
#    print(inside_quote(sss,i))


def bracket_checker(s):
    return True


# ---------------------------------------------------
# In[ ]:

QUO = re.compile(r"([\"\'])((\\\\{2})*|(.*?[^\\](\\{2})*))\1")

def non_quote(s0):
    s = s0[:]
    Qts1 = [str(x.group(0)) for x in QUO.finditer(s)]
    for q in Qts1:
        s = s.replace(q,'')
    return s

#sss = "s = io('ssd\" ')"
#[str(x.group(0)) for x in QUO.finditer(sss)]
#non_quote(sss)


def split_quote_core(s0,Q):
    found = False
    for q in Q:
        if q in s0:
            found = True
            ll = s0.split(q,1)
            return split_quote_core(ll[0],Q) + [q] + split_quote_core(ll[1],Q)
        else:
            continue

    if not found:
        return [s0]


def split_quote(s0):
    s = s0[:]
    Qts = [str(x.group(0)) for x in QUO.finditer(s)]
    return split_quote_core(s0,Qts)


def combine_quote_list(lst):
    return "".join(lst)


def split_on_toplevel_comma(s0):
    s = s0.strip()
    level = 0
    prev_comma_pos = -1
    pieces = []
    stack = deque()
    for i in range(len(s)):
        if i==len(s)-1:
            pieces.append(s[prev_comma_pos+1:])
        elif (not inside_quote(s,i)):
            if s[i]==',':
                if level==0 and len(stack)==0:
                    pieces.append(s[prev_comma_pos+1:i])
                    prev_comma_pos = i
                #end #if
            elif s[i]=='(':
                stack.append('(')
                level += 1
            elif s[i]=='[':
                stack.append('[')
                level += 1
            elif s[i]==')':
                if stack[-1]=='(':
                    stack.pop()
                    level -= 1
                else:
                    print("[---ERROR---]")
                    print("split_on_toplevel_comma() : bracket ( ) mismatch !!!")
                #end #if
            elif s[i]==']':
                if stack[-1]=='[':
                    stack.pop()
                    level -= 1
                else:
                    print("[---ERROR---]")
                    print("split_on_toplevel_comma() : bracket [ ] mismatch !!!")
                #end #if
            else:
                pass
            #end #if
        else:
            pass
        #end #if
    #end #for
    return pieces


#sss = "fermi_energy_list(if),sum(ahc_list(:,1,if)),sum(ahc_list(:,2,if)),(sum(ahc_list(:,3,if)))"
#sss = "'#    components of the TDF for the spin up, followed by those for the spin down) '"
#rint( split_on_toplevel_comma(sss) )



def split_on_slash(ss):
    cl,cr = 0,0
    for i in range(0,len(ss)):
        if ss[i] == '/':
            cl += 1
            continue
        else:
            break
    if cl == len(ss):
        return ['/'*cl, '', '']
    else:
        for i in range(len(ss)-1,-1,-1):
            if ss[i] == '/':
                cr += 1
                continue
            else:
                break
        if cr == 0:
            return [ss[0:cl], ss[cl:], '']
        else:
            return [ss[0:cl], ss[cl:-cr], ss[-cr:]]



def find_brackets(s,bleft='(',bright=')'):
    brackets = {}
    stack = deque()
    for i in range(len(s)):
        if s[i]==bleft:
            if not inside_quote(s,i):
                stack.append(i)
            #end #if
        elif s[i]==bright:
            if not inside_quote(s,i):
                if len(stack)==0:
                    print("[--- find_brackets() ERROR ---]")
                    print(s)
                istart = stack.pop()
                brackets[istart] = i
            #end #if
        else:
            pass
        #end #if
    #end #for
    return brackets
#end #def


#sss = "@printf \"a% ) \" (g[:]) ((1+2)/2,(g(f)))"
#for i in range(len(sss)):
#    print(inside_quote(sss,i))

#find_brackets(sss)


def find_complemetary_ket(s,pos_bra):
    assert s[pos_bra]=='('
    stack = deque()
    for i in range(pos_bra,len(s)):
        if s[i]=='(':
            stack.append(i)
        elif s[i]==')':
            istart = stack.pop()
            if istart==pos_bra:
                return i
            #end #if
        else:
            pass
        #end #if
    #end #for
    assert len(stack)==0
    return -1  # not find


def update_json_file(file,entry,data):
    if not os.path.exists(file):
        dic = {}
    else:
        with open(file,'r') as h:
            read_data = h.read()
            dic = json.loads(read_data)
    dic[entry] = data
    with open(file,'w') as f:
        f.write( json.dumps(dic) )
    #end write
    return
