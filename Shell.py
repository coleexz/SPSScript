import Basic

while True:
    text = input('Algo >')
    result, error = Basic.run('<stdin>',text)

    if error: print(error.as_string())
    else: print(result)
