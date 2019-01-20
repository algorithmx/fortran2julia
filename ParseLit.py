import re

double_prec_literal_patt = re.compile(r"\d+(\.\d*)?[dD]([\-\+])?\d+")

def parse_double(s):
    return s.lower().replace('d','e')

single_prec_literal_patt = re.compile(r"\d+(\.\d*)?[eE]([\-\+])?\d+")

def parse_single(s):
    return s.lower().replace('e','f')

integer_literal_patt = re.compile(r"([\-\+])?\d+")

def parse_int(s):
    return s

true_bool_patt = re.compile(r"\.true\.")

def parse_TRUE(s):
    return 'true'

false_bool_patt = re.compile(r"\.false\.")

def parse_FALSE(s):
    return 'false'

replace_literal = { double_prec_literal_patt: parse_double,\
                    single_prec_literal_patt: parse_single,\
                    integer_literal_patt: parse_int,\
                    true_bool_patt: parse_TRUE,\
                    false_bool_patt: parse_FALSE }

def parse_number(s):
    for p in replace_literal.keys():
        if p.search(s.strip()) is not None:
            return replace_literal[p](s.strip())

    return s


dp_patt = re.compile(r"\d+\.\d*([eE]([\+\-])?\d+)?\_dp")

real_patt = re.compile(r"real\([\w\-\+\(\)\[\]\*\/\,\.\:]+\,\s*(kind\s*\=)?\s*dp\s*\)")

cmplx_patt = re.compile(r"cmplx\([\w\-\+\(\)\[\]\*\/\,\.\:]*?\s*\,\s*(kind\s*\=)?\s*dp\s*\)")


def process_dp(s0):
    s = s0[:]
    for x in dp_patt.finditer(s):
        s = s.replace(x.group(0), str(x.group(0))[:-3] )

    for x in real_patt.finditer(s):
        y = re.sub(r"\s*\,\s*(kind\s*\=)?\s*dp\s*\)", '', str(x.group(0)))
        y = re.sub(r"real\s*\(\s*", '', y)
        s = s.replace(x.group(0),y)

    for x in cmplx_patt.finditer(s):
        y = re.sub(r"\s*\,\s*(kind\s*\=)?\s*dp\s*\)", ')', str(x.group(0)))
        y = re.sub(r"cmplx\s*\(\s*", "ComplexF64(", y)
        s = s.replace(x.group(0),y)

    return s


#sss = "cmplx(1.2e-10_dp,1,dp)"
#real_patt.search(sss)
#process_dp(sss)

'''
def process_dp(s0, skipComm=True):
    if (is_julia_comment(s0) or is_fortran_comment(s0)) and skipComm:
        return s0

    s = s0[:]
    dp_all = [str(x.group(0)) for x in dp_patt.finditer(s)]
    for y in dp_all:
        s = s.replace(y,"Float64("+y[:-3]+")")
    #end #for
    #
    dp_all = [str(x.group(0)) for x in real_patt1.finditer(s)]
    for y in dp_all:
        y0 = re.sub(r"\,\s*dp\s*\)",'',y)
        y0 = re.sub(r"real\(\s*",'',y0)
        s = s.replace(y,"Float64("+ y0 +")")
    #end #for
    #
    dp_all = [str(x.group(0)) for x in real_patt2.finditer(s)]
    for y in dp_all:
        y0 = re.sub(r"\,\s*kind\s*\=\s*dp\s*\)",'',y)
        y0 = re.sub(r"real\(\s*",'',y0)
        s = s.replace(y,"Float64("+ y0 +")")
    #end #for
    #
    dp_all = [str(x.group(0)) for x in cmplx_patt1.finditer(s)]
    for y in dp_all:
        y0 = re.sub(r"\,\s*dp\s*\)",'',y)
        y0 = re.sub(r"cmplx\(\s*",'',y0)
        s = s.replace(y,"ComplexF64("+ y0 +")")
    #end #for
    #
    dp_all = [str(x.group(0)) for x in cmplx_patt2.finditer(s)]
    for y in dp_all:
        y0 = re.sub(r"\,\s*kind\s*\=\s*dp\s*\)",'',y)
        y0 = re.sub(r"cmplx\(\s*",'',y0)
        s = s.replace(y,"ComplexF64("+ y0 +")")
    #end #for
    #
    return s
'''
