# fortran2julia

## using python to translate fortran90 to julia 

This is an ongoing effort to translate FORTRAN90 to Julia. I could use `ccall()` to simplify my life, but I really need to understand what happens in the original F90 code. 

Life is simple here because the array conventions of the two languages are the same. 

https://docs.julialang.org/en/v1/manual/arrays/index.html

https://docs.oracle.com/cd/E19957-01/805-4940/z400091044d0/

If you have any questions / suggestions, please open an issue. Your question will help me to improve the code ! 


## NOTE:

1. The file "JulTran.jl" contains necessary Julia structs and macros for the translated code to run.

2. One needs to `using Printf` explicitly at the beginning of the translated code.

3. Is it meaningfuul to translate ?

## Oh, by the way, you still have to manually finalize the translation since:

1. I haven't figured out how to deal with the fabulous FORTRAN `GOTO` instruction

2. FORTRAN compiler can deal with negative array index if the array is allocated accordingly. I translate the FORTRAN90 `do` loop literaly even though the iterator may be negative. Please be cautious. I do not want to translate the do loop because I may replace most of them by something like `a[:,i] += b` in Julia. That can only be accomplished by a human ...

3. Plans

3.1 write a skeleton of each F90 file with empty contents inside functions

3.2 automate the translation of the `read(...) ...` instructions in the F90 file
