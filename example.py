import sys
sys.path.append(('.'))

import os

from fortran2julia import *
from translate import *


fd = './Wannier/wannier90-2.1.0/src/postw90/'

# !!! please create a folder called "jl" in the above folder to store the translated codes and logs.

#allo_lines_fn, allo_json_fn, allo_log_fn, func_log_fn, modu_log_fn
lines_fn = fd + 'jl/' + 'declarations.json'
json_fn = fd + 'jl/' + 'allocatables.json'
allo_fn = fd + 'jl/' + 'allocates.json'
funcs_fn = fd + 'jl/' + 'functions.json'
modu_fn = fd + 'jl/' + 'modules.json'
PV_log_fn = fd + 'jl/' + 'public_variables.json'


for fn in os.listdir(fd):
    if os.path.isfile(fd+fn) and fn.endswith('.F90'):
        print(" --------------------- " + fn + " --------------------- ")
        print("step 1:")
        st1 = first_run(fd+fn)
        with open(fd+'/jl/'+fn+'.run1.jl','w') as f:
            f.write(st1)
        print("step 1: finished")
        print("step 2:")
        st2 = second_run(st1)
        with open(fd+'/jl/'+fn+'.run2.jl','w') as f:
            f.write(st2)
        print("step 2: finished")
        print("step 3:")
        st3 = third_run(st2)
        with open(fd+'/jl/'+fn+'.run3.jl','w') as f:
            f.write(st3)
        print("step 3: finished")
        print("step 4:")
        st4 = fourth_run(st3)
        with open(fd+'/jl/'+fn+'.run4.jl','w') as f:
            f.write(st4)
        print("step 4: finished")
        print("step 5:")
        st5 = fifth_run(st4, fn, lines_fn, json_fn, allo_fn, funcs_fn, modu_fn, PV_log_fn)
        print("step 5: finished")
        with open(fd+'/jl/'+fn+'.run5.jl','w') as f:
            f.write(st5)





for fn in os.listdir(fd):
    if os.path.isfile(fd+fn) and fn.endswith('.F90'):
        print(" --------------------- " + fn + " --------------------- ")
        with open(fd+'/jl/'+fn+'.run5.jl','r') as f:
            st5 = f.read()
        print("step 6:")
        st6 = sixth_run(st5, fn, json_fn, allo_fn, funcs_fn, modu_fn)
        print("step 6: finished")
        with open(fd+'/jl/'+fn+'.run6.jl','w') as f:
            f.write(st6)
        #end #with
