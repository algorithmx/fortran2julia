import re
from Utinity import split_on_toplevel_comma, split_on_slash

def prt_string(fmt):
    return ("%s" if len(fmt)==1 else ('%-'+(fmt[1:])+'s'))


def prt_spaces(fmt):
    return ( ' '*int(fmt[0:-1]) )


def prt_rep_chars(fmt):
    return ( fmt[-3] * int(fmt[0:-5]) )


def prt_one_char(fmt):
    return ( '%%' if (fmt[-2]=='%') else fmt[-2] )


def prt_int(fmt):
    return ('%'+fmt[1:]+'i')


def float_____format_spec(fmt,spec):
    F = spec.upper()
    f = spec.lower()
    # matched r"\d*[fF]\d+\.\d+"
    return ( ('%'+fmt[1:]+ f) \
            if (fmt[0]==f or fmt[0]==F) \
            else ( ('%'+fmt.lower().split(f)[1]+f)*int(fmt.lower().split(f)[0])) )

def float_ord_format_spec(fmt):
    return float_____format_spec(fmt,'f')


def float_sci_format_spec(fmt):
    return float_____format_spec(fmt,'e')


def float_ggg_format_spec(fmt):
    return float_____format_spec(fmt,'g')


def no_spec(fmt):
    return fmt


def new_line(fmt):
    print("[INFO:NEW_LINE] " + str(len(fmt)))
    return '\\n' * len(fmt)


special_chars = [ (r"\$",'\\$'), (r"\\",'\\\\'), (r"\"",'\\\"'), (r"%","%%") ]


def iden_string(fmt):
    S2 = fmt[1:-1]
    for rf,rj in special_chars:
        S2 = re.sub(rf,rj,S2)
    #end #for
    return S2


spec_regex = [  re.compile(r"([\"\'])((\\\\{2})*|(.*?[^\\](\\{2})*))\1"),
                re.compile(r"\d+[xX]"),
                re.compile(r"\d+\"\([\s\-\+\_]\)\""),
                #re.compile(r"\"[\s\-\+\_\|\,]\""),
                re.compile(r"[iI]\d+"),
                re.compile(r"\d*[fF]\d+\.\d+"),
                re.compile(r"\d*[eE]\d+\.\d+"),
                re.compile(r"\d*[gG]\d+\.\d+"),
                re.compile(r"\*"),
                re.compile(r"[\/]+"),
                re.compile(r"[aA]\d*") ]


spec_trans = {  spec_regex[0]: iden_string, \
                spec_regex[1]: prt_spaces, \
                spec_regex[2]: prt_rep_chars, \
                #spec_regex[3]:prt_one_char, \
                spec_regex[3]: prt_int, \
                spec_regex[4]: float_ord_format_spec, \
                spec_regex[5]: float_sci_format_spec, \
                spec_regex[6]: float_ggg_format_spec, \
                spec_regex[7]: no_spec, \
                spec_regex[8]: new_line, \
                spec_regex[9]: prt_string }



def parse_fmt(s):
    trans = []
    spec_list = split_on_toplevel_comma(s.strip(' ()').strip(' ()'))
    for spec0 in spec_list:
        l,c,r = split_on_slash(spec0.strip())
        if (len(c) == 0) and (len(r) == 0):
            trans.append("\\n"*len(l))
            continue

        for reg in spec_regex:
            if reg.search(c) is not None:
                spec_tr = spec_trans[reg](c.strip())
                trans.append( ("\\n"*len(l)) + spec_tr + ("\\n"*len(r)) )
                break
            #end #if
        #end #for
    #end #for
    return (''.join(trans))


#sss = "(7g18.10)"
#parse_fmt(sss)
#parse_fmt("(A3,'\" ',F8.5,') ')")
#sss = "('set style data dots',/,'unset key',/, 'set xrange [0:',F8.5,']',/,'set yrange [',F16.8,' :',F16.8,']')"
#print(parse_fmt(sss))
#parse_fmt('(/1x,a25,f11.3,a/) ')


#sss = "(A3,'\" ',F8.5,') ')"
#print(parse_fmt(sss)+",")
