VAR x = [1,2,3]

#buenos dias, como tamos como tamos

PRINT(x)

APPEND(x, 4)
PRINT(x)


VAR name = INPUT()
PRINT(name)

PRINT(LEN(x))

IF 5==5 THEN;
    PRINT("HELLO")
ELSE
    PRINT("ADIOS")
END;

FUN add (a,b) -> a + b
PRINT(add(5,5))

PRINT(IS_FUN(add))
PRINT(IS_FUN(name))
PRINT(IS_LIST(name))
PRINT(IS_LIST(x))

VAR arr = []

FOR VAR i = 0 TO 10  STEP 2 THEN;
    PRINT(i)
    APPEND(arr, i)
    IF i < 5 THEN;
        CONTINUE
    ELSE
        PRINT("TERMINO EL FOR")
        BREAK
    END;
END

PRINT(arr)


VAR prueba = add(1,1)
PRINT(prueba)



FUN greet(name) -> PRINT("Hello " + name)
greet("William")
