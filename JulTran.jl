# JulTran.jl

struct NONALLOCATO
    DT::DataType
end

macro declare(A, T, NX)
    return :( $(esc(A)) = NONALLOCATO(Array{$(esc(T)),$(esc(NX))}) )
end

macro Ndeclare(A, T)
    return :( $(esc(A)) = NONALLOCATO($(esc(T))) )
end

macro Ninit(A, T, V)
    return :( $(esc(A)) = convert($(esc(T)),$(esc(V))) )
end

macro allocate(A, T, S)
    return :( $(esc(A)) = fill(zero($(esc(T))),$(esc(S))) )
end

macro deallocate(a)
    return :( $(esc(a)) = NONALLOCATO(typeof($(esc(a)))) )
end

macro isallocated(a)
    return :( ! isa($(esc(a)), NONALLOCATO) )
end

#@isallocated A

#@declare A Float64 (2,3,4)

#@allocate A Float64 (2,3,4)

#@deallocate A

#@macroexpand (@deallocate A)

#A = rand(20000,20000)

#@deallocate A
