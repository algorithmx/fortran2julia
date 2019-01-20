import re

def prt_string(fmt):
    return ("%s" if len(fmt)==1 else ('%-'+(fmt[1:])+'s'))


def prt_spaces(fmt):
    return ( ' '*int(fmt[0:-1]) )


#prt_rep_chars(fmt::String) = (fmt[end-2]^parse(Int,fmt[1:end-5]))


def prt_rep_chars(fmt):
    return ( fmt[-3] * int(fmt[0:-5]) )


#prt_one_char(fmt::String) = ((fmt[end-1]=='%') ? ("%%") : (fmt[end-1]))


def prt_one_char(fmt):
    return ( '%%' if (fmt[-2]=='%') else fmt[-2] )


#prt_int(fmt::String) = ("%" * (fmt[2:end]) * "i")


def prt_int(fmt):
    return ('%'+fmt[1:]+'i')


#float_ord_format_spec(fmt::String) = ( (fmt[1]=='f'||fmt[1]=='F') ? ("%"*fmt[2:end]*"f") : repeat(("%"*split(fmt,['f','F'])[2]*"f"),parse(Int,split(fmt,['f','F'])[1])) )


def float_ord_format_spec(fmt):
    return ( ('%'+fmt[1:]+'f') \
            if (fmt[0]=='f' or fmt[0]=='F') \
            else (('%'+fmt.lower().split('f')[1]+'f')*int(fmt.lower().split('f')[0])) )


#float_sci_format_spec(fmt::String)


def float_sci_format_spec(fmt):
    return ( ('%'+fmt[1:]+'e') \
            if (fmt[0]=='e' or fmt[0]=='E') \
            else (('%'+fmt.lower().split('e')[1]+'e')*int(fmt.lower().split('e')[0])) )


def no_spec(fmt):
    return fmt


def new_line(fmt):
    return '\\n'


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
                re.compile(r"\*"),
                re.compile(r"\/"),
                re.compile(r"[aA]\d*") ]


spec_trans = {  spec_regex[0]: iden_string, \
                spec_regex[1]: prt_spaces, \
                spec_regex[2]: prt_rep_chars, \
                #spec_regex[3]:prt_one_char, \
                spec_regex[3]: prt_int, \
                spec_regex[4]: float_ord_format_spec, \
                spec_regex[5]: float_sci_format_spec, \
                spec_regex[6]: no_spec, \
                spec_regex[7]: new_line, \
                spec_regex[8]: prt_string }




def parse_fmt(s):
    trans = []
    for spec0 in s.strip(' ()').strip(' ()').split(','):
        spec = spec0.strip()
        if spec=='/':
            trans.append('\\n')
            continue
        else:
            begin_slash = spec[0]=='/'
            end_slash = spec[-1]=='/'
            spec = (spec[1:] if begin_slash else spec0)
            spec = (spec[:-1] if end_slash else spec)
            for reg in spec_regex:
                if reg.search(spec) is not None:
                    spec_tr = spec_trans[reg](spec.strip())
                    spec_tr = ('\\n'+spec_tr if begin_slash else spec_tr)
                    spec_tr = (spec_tr+'\\n' if end_slash else spec_tr)
                    trans.append(spec_tr)
                    break
                #end #if
            #end #for
        #end #if
    #end #for
    return (''.join(trans))





#parse_fmt("(A3,'\" ',F8.5,') ')")
#sss = "('set style data dots',/,'unset key',/, 'set xrange [0:',F8.5,']',/,'set yrange [',F16.8,' :',F16.8,']')"
#print(parse_fmt(sss))
#parse_fmt('(/1x,a25,f11.3,a/) ')


#sss = "(A3,'\" ',F8.5,') ')"
#print(parse_fmt(sss)+",")
