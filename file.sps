PoneleQue x = [1,2,3]
Ejenie(x)

# buenos dias, como tamos como tamos

#Input y print de 'nombre'
PoneleQue nombre = Sampale()
Ejenie("Hola, mi nombre es: ", nombre)



#Prueba de ifs normales
PoneteAPensar Mide(x) == 3 y nombre == "Cole" Tonces
    Ejenie("x mide 3 y nombre es Cole")
Decidite Mide(x) == 4 o nombre == "William" Tonces
    Ejenie("x mide 4 o nombre es William")
HaceteLoco
    Ejenie("Ninguna de las condiciones se cumplió")
Cheque


#Prueba de ifs anidados
PoneteAPensar nombre == "Cole" Tonces
    Ejenie("El nombre es Cole")

    PoneteAPensar Mide(x) == 3 Tonces
        Ejenie("Además, x mide 3")
    Decidite Mide(x) > 3 Tonces
        Ejenie("Además, x mide más de 3")
    HaceteLoco
        Ejenie("Además, x mide menos de 3")
    Cheque
HaceteLoco
    Ejenie("El nombre no es Cole")
Cheque





PoneleQue z = 1

PoneteAPensar z == 2 Tonces
    Ejenie("z  es 2")
Decidite z == 3 Tonces
    Ejenie("z  es 3")
HaceteLoco
    Ejenie("z no es ni 2 ni 3")
Cheque



#FOR
PoneleQue lista = []
PasarLista PoneleQue i = 10 Hasta 15 De 2 Tonces
    Metele(lista, i)
Cheque

Ejenie(lista)


#WHILE
PoneleQue lista = []
PoneleQue i = 0

AhoritaQue i <= 20 Tonces
    Metele(lista, i)
    PoneteAPensar i == 15 Tonces
        CortalaMiPerro
    Cheque
    i = i + 5

Cheque


Ejenie(lista)

#Pop
Saca(lista,0)
Ejenie(lista)

#Funcion
HacemeElParo multiply(a, b) ->
a * b

#Len
Ejenie("La longitud de lista es: ", Mide(lista))

Ejenie("La multiplicacion de 5*5 es: ", multiply(5,5))

Ejenie("Es x una fila india? ",EsFilaIndia(x)) #is_list
Ejenie("Es multiply un paro? ",EsParo(multiply)) #is_fun
Ejenie("Es x un chambre? ",EsChambre(x)) #is_str
Ejenie("Es i un entero? ", EsEntero(i)) #is_int
