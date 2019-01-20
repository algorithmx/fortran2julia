# fortran2julia

## using python to translate fortran90 to julia 

This is an ongoing effort to translate FORTRAN90 to Julia. I could use `ccal()` to simplify my life, but I really need to understand what happens in the original F90 code. 

Life is simple here because the array conventions of the two languages are the same. 

If you have any questions / suggestions, please open an issue. Your question will help me to improve the code ! 


## NOTE:

1. The file "JulTran.jl" contains necessary Julia structs and macros for the translated code to run.

2. One needs to `using Printf` explicitly at the beginning of the translated code.

3. Is it meaningfuul to translate ?
