PoneleQue x = [1,2,3]

# buenos dias, como tamos como tamos

Ejenie(x)

PoneleQue x = 1

PoneleQue x = 2

PoneteAPensar x NadaQueVer 2 THEN
    Ejenie("x no es 2 ")
Decidite x NadaQueVer 2 THEN
    Ejenie("x es 2")
HaceteLoco
    Ejenie("x es 2")
END


#FOR
PoneleQue lista = []
PasarLista PoneleQue i = 10 Hasta 15 De 2 THEN
    APPEND(lista, i)
END

Ejenie(lista)


#WHILE
PoneleQue lista = []
PoneleQue i = 0

AhoritaQue i <= 20 THEN
    APPEND(lista, i)
    i = i + 5
END

Ejenie(lista)


HacemeElParo multiply(a, b) ->
a * b


Ejenie(multiply(5,5))
