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

#https://stackoverflow.com/questions/39931112/quote-unquote-idiom-in-julia-concatenating-expr-objects
import Base.zero
zero(::Type{T}) where{T<:AbstractString} = string("")

macro declareNtimes(vars...)
    ex = Expr(:block)
    t = vars[1]
    ex.args = [:($(esc(n)) = Base.zero($(esc(t)))) for n in vars[2:end]]
    ex
end

#@declareNtimes Bool a b c

macro Ninit(A, T, V)
    return :( $(esc(A)) = Base.convert($(esc(T)),$(esc(V))) )
end

macro NinitNtimes(vars...)
    ex = Expr(:block)
    t = vars[1]
    ex.args = [:( $(esc(c.args[1])) = Base.convert($(esc(t)), $(esc(c.args[2]))) ) for c in vars[2:end]]
    ex
end

#@NinitNtimes Bool (a,false) (b,true)
#@assert !a && b

macro allocate(A, T, S)
    return :( $(esc(A)) = Base.fill(Base.zero($(esc(T))),$(esc(S))) )
end

macro deallocate(a)
    return :( $(esc(a)) = NONALLOCATO(Base.typeof($(esc(a)))) )
end

macro isallocated(a)
    return :( ! Base.isa($(esc(a)), NONALLOCATO) )
end
