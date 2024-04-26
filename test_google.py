from googletrans import Translator

src_language = "ca"
dest_language = "es"
variables_to_translate = ["públic", "public", "(prova)"]

for variable_to_translate in variables_to_translate:
	translator = Translator()
	try:
		translation = translator.translate(variable_to_translate, src=src_language, dest=dest_language).text
		print(translation)
	except Exception as e:
		print("Translation not available")