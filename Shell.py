import Basic

while True:
	text = input('basic > ')
	result, error = Basic.run('<stdin>', text)

	if error: print(error.as_string())
	elif result: print(result)
