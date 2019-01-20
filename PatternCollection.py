# ------------------------------------------------------------
#
# TOUCHE PAS !!!
#
# TOUCHE PAS !!!
#
# TOUCHE PAS !!!
#
# ------------------------------------------------------------


import re

excluded_arrayhead = ['if', 'write', 'read', 'rewind', 'open', 'close', 'inquire', \
                      'zero', 'one', 'trim', 'max', 'min', 'real', 'complex' ]

fortran_kwords = ['len_strip', 'strip', 'trim', 'real', 'cmplx', 'inquire', \
                  'maxval', 'minval', 'maxloc', 'minloc', \
                  'write', 'read', 'subroutine', 'function', 'program', 'allocated', \
                  'io_error', 'io_stopwatch',
                  'ZGESV', 'ZGEMM', 'ZCOPY' ]

BLAS = ['ZGESV', 'ZGEMM', 'ZCOPY']

ass_patt = re.compile(r"[^\=\<\>\!\.\/\s]\s*\=\s*[^\=\s]")

array_patt = re.compile(r"\w+\(([\w\:\+\-\*\_]*,)*([\w\:\+\-\*\_]+)\)")

array_patt_julia = re.compile(r"\w+\[([\w\:\+\-\*]*,)*([\w\:\+\-\*]+)\]")

single_quote_string_patt = re.compile(r"([\'])((\\\\{2})*|(.*?[^\\](\\{2})*))\1")

do_patt = re.compile(r"\s*do\s+[^\=\,]+\=[^\=\,]+\,")

ok_do_patt = re.compile(r"\w+\s*\:\s*do\s+[^\=\,]+\=[^\=\,]+\,")

enddo_patt = re.compile(r"\s*end\s*do\s*")

#ok_do_patt.search("       ok: do ndnnx = 1, num_shells")

write_crit_patt = re.compile(r"write\s*\(")


io_error_patt_simple = re.compile(r"io\_error\s*\(\s*")

func_patt_simple = re.compile(r"call\s+\w+\s*\(")

func_patt_no_bra = re.compile(r"call\s+\w+")


#call_io_error_patt = re.compile(r"call\s+io_error")

#if_cond_io_error_patt = re.compile(r"if\s*\([\w\(\)\[\]\.\,\:\+\-\*\/\&\^\!\=\s]+\)\s+(call)?\s*io_error")

ifdef_patt = re.compile(r"\#ifdef")

else_patt = re.compile(r"\#else")

endif_patt = re.compile(r"\#endif")

end_func_patt = re.compile(r"end\s+\#function")

func_patt = re.compile(r"function\s+\w")

fmt_line_header_patt = re.compile(r"\d{3,5}\s+format\s*\(")

jump_line_header_patt = re.compile(r"\d{3,5}\s+")

eq_sign_patt = re.compile(r"\s*\=\s*")

logic_rules = [ ('.false.','false'), ('.true.','true'), ('.and.',' && '), ('.or.',' || '), ('.ne.',' != '),\
                ('.ne.',' != '), ('/=',' != '), ('/ =',' != '),\
                ('.eq.',' == '), ('.eqv.','=='), ('.lt.',' < '),\
                ('.gt.',' > '), ('.ge.',' >= '), ('.le.',' <= ')]


number_rules = [('cmplx_0','zero(ComplexF64)'), ('cmplx_1','one(ComplexF64)'),\
                ('0.0_dp','zero(Float64)'), ('1.0_dp','one(Float64)'),\
                ('eps8','1e-8'), ('eps5','1e-5'), ('eps10','1e-10'), ('eps7','1e-7') ]

eq_rules = [ (r"\="," = "), (r"\s+\=\s+"," = ") ]

control_rules = [ (r"end\s*do", "end #for"), (r"do\s+","for "),\
                (r"then", " "), (r"if\s*\(\s*", "if ("), (r"end\s*if", "end #if"),\
                (r"end\s*subroutine", "end #function "), (r"subroutine\s+", "function "),\
                (r"end\s*function", "end #function "), (r"goto\s+", "_GOTO_ "),\
                (r"exit", "break"), (r"cycle", "continue") ]

misc_rules = [  (r'\s*=\s*1\s*,\s*','= 1:'), (r'\s*=\s*2\s*,\s*','= 2:'), (r"\s*\*\*\s*","^"),\
                (r'\.not\.',"! "), (r'\s*\>\s+\='," >="), (r'\s*\<\s+\='," <="), (r"write\s+\(","write("),\
                (r'\=\s+\=',"=="), (r"\)\'",") '"), (r'Call\s+',' '), (r"trim","strip") ]

comm_patt = [ re.compile(r"end\s+module"),\
              re.compile(r"module\s+\w+"),\
              re.compile(r"use\s+\w+"),\
              re.compile(r"include\s+\w+"),\
              re.compile(r"implicit\s+\w+"),\
              re.compile(r"end\s+interface"),\
              re.compile(r"interface"),\
              re.compile(r"integer[^_]"),\
              re.compile(r"real[^_]"),\
              re.compile(r"complex[^_]"),\
              re.compile(r"character[^_]"),\
              re.compile(r"logical[^_]"),\
              re.compile(r"private"),\
              re.compile(r"public"),\
              re.compile(r"contains"),\
              re.compile(r"type[^_]"),\
              re.compile(r"if\s+\(\s*ierr\s*") ]


comm_list = [ "end",\
              "module",\
              "use",\
              "include",\
              "implicit",\
              "end",\
              "interface",\
              "integer",\
              "real",\
              "complex",\
              "character",\
              "logical",\
              "private",\
              "public",\
              "contains",\
              "type",\
              "if" ]

comm_patt_select = [ re.compile(r"select\s+case"), re.compile(r"end\s+select"), re.compile(r"case") ]

comm_list_select = [ "select", "end", "case" ]

if_allo_patt = re.compile(r"(if\s*\([\w\>\<\=\(\)\[\]\.\,\:\+\-\*\/\&\^\!\s]+\)\s+)?allocate\s*\(")

if_deallo_patt = re.compile(r"(if\s*\([\w\>\<\=\(\)\[\]\.\,\:\+\-\*\/\&\^\!\s]+\)\s+)?deallocate\s*\(")

comment_repl_rule = [ ('![ysl','#[ysl'), ('-!','- #'), ('!-','# -'),\
                      ('!! ','## '), ('!~','#ALTER_CODE '), ('!%','#UNDEF '),\
                      ('!=','# ='), ('! ','# '), ('!','# ') ]


do_jump_patt = re.compile(r"\d+\s+[^\=\,]+\=[^\=\,]+\,")

do_while_patt = re.compile(r"\s*do\s+while\s*")

dp_patt = re.compile(r"\d+\.\d+\_dp")

real_patt1 = re.compile(r"real\([\w\s\-\+\(\)\[\]\*\/\_\:]+\,\s*dp\s*\)")

real_patt2 = re.compile(r"real\([\w\s\-\+\(\)\[\]\*\/\_\:]+\,\s*kind\s*\=\s*dp\s*\)")

cmplx_patt1 = re.compile(r"cmplx\([\w\s\-\+\(\)\[\]\*\/\_\:]+\,\s*dp\s*\)")

cmplx_patt2 = re.compile(r"cmplx\([\w\s\-\+\(\)\[\]\*\/\_\:]+\,\s*kind\s*\=\s*dp\s*\)")

array_colon_expr_patt = re.compile(r"\w+\((\:\s*\,\s*)*\:\s*\)")

write_head_firstarg_patt = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,")

write_patt_adv = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\'[a-zA-Z0-9\!\:\"\(\)\*\+\,\.\|\/\-\s]*\s*\'\s*\)")

write_FMT_patt_adv = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*[Ff][Mm][Tt]\s*\=\s*\'[a-zA-Z0-9\!\:\"\(\)\*\+\,\.\|\/\-\s]*\s*\'\s*\)")

write_patt_no_adv = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\'[a-zA-Z0-9\!\:\"\(\)\*\+\,\.\|\/\-\s]*\s*\'\s*\,\s*advance\s*\=\s*[\"\']no[\"\']\s*\)")

write_star_patt = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\*\s*\)")

write_star_out_patt = re.compile(r"write\s*\(\s*\*\s*\,\s*\'[a-zA-Z0-9\!\:\"\(\)\*\+\,\.\|\/\-\s]*\s*\'\s*\)")

write_three_number_patt = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\d{3,5}\s*\)")

write_three_number_patt_no_adv = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\d{3,5}\s*\,\s*advance\s*\=\s*[\"\']no[\"\']\s*\)")

write_a_patt = re.compile(r"write\s*\(\s*[\s\w\(\)]+\s*\,\s*\'\s*\([aA]\s*\)\s*\'\s*\)")

write_no_fmt_patt = re.compile(r"write\s*\(\s*\w+\s*\)")

array_head_patt = re.compile(r"\w+\[")

#allocatable_patt = re.compile(r"\s*allocatable(\s*\,\s*[\w\s\,\(\)\:\+\-\*\/]+)*\s*\:\:\s*")
#allocatable_patt = re.compile(r"\s*allocatable(\s*\,\s*[\w\s\,\(\)\:]+)*\s*\:\:\s*")  # catastrophic
allocatable_patt = re.compile(r"\s*allocatable\s*(\s*\,\s*[\w]+\s*(\(\s*\:(\s*\,\s*\:\s*)*\))?)*\s*\:\:\s*")

real_type_patt = re.compile(r"real(\(\s*(kind\s*\=)?\s*\w+\s*\))?")

#real_type_patt.search("    real(DP),allocatable :: wdist_wssc_frac(:,:,:,:), irdist_real(:,:,:,:,:)")

complex_type_patt = re.compile(r"complex(\(\s*(kind\s*\=)?\s*\w+\s*\))?")

int_type_patt = re.compile(r"integer")

bool_type_patt = re.compile(r"logical")

chars_type_patt = re.compile(r"character\(\s*len\s*\=\s*\w+\s*\)")

#chars_type_patt.search("    character( len = 60 )             :: header")

var_types = {real_type_patt:"Float64",\
            complex_type_patt:"ComplexF64",\
            int_type_patt:"Int64",\
            bool_type_patt:"Bool",\
            chars_type_patt:"String"}


dim_patt = re.compile(r"dimension\((\s*\:\s*\,)*\:\s*\)")

allo_vars_patt = re.compile(r"\w+\s*\((\s*\:\s*\,)*\:\s*\)")

vars_name_patt = re.compile(r"(\s*[^\,]+\s*\,)*\s*[^\,]+\s*")

bracket_colon_patt = re.compile(r"\((\s*\:\s*\,)*\:\s*\)")

public_patt = re.compile(r"public\s*(\,)?")

public_vars_patt = re.compile(r"\s*public\s*(\s*\,\s*[\w]+\s*)*\s*\:\:\s*")

DIRECT_public_patt = re.compile(r"public\s*\:\:")

save_patt = re.compile(r"save\s*(\,)?")

save_vars_patt = re.compile(r"\s*save\s*(\s*\,\s*[\w]+\s*)*\s*\:\:\s*")

FORTRAN_CONTROL_patt = re.compile(r"\#FORTRAN_CONTROL\s")

if_err_patt = re.compile(r"if\s*\(\s*ierr")

deallocate_array_patt = re.compile(r"deallocate\s*\(")

allocate_array_patt = re.compile(r"allocate\s*\(")

iter_patt = re.compile(r"[\w\+\-\*\/\^\s\(\)]+\:[\w\+\-\*\/\^\s\(\)]+")

stat_patt = re.compile(r"\,\s*stat\s*\=\s*\w+\s*")

allo_name_patt = re.compile(r"\w+\s*\(")

#allo_name_patt.search("a(2,3,4)")

allo_shape_patt = re.compile(r"\s*\((\s*[\w\+\-\*\/\^\s\(\)\:]+\,)*\s*[\w\+\-\*\/\^\s\(\)\:]+\s*\)")

#allo_shape_patt.search("a(1:2,3*i,4)")

#allo_shape_patt.search("a(,1:2,3*i,4)")

module_patt = re.compile(r"\s*module\s+\w+")

module_procedure_patt = re.compile(r"\s*module\s+procedure\s+")

end_module_patt = re.compile(r"\s*end\s+(\#)?\s*module\s+\w+")
