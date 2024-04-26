# Install requirements: pip install -r requirements.txt
# To execute: python search_translations.py --path=wp-content/plugins --translate

import argparse
import json
import os

from googletrans import Translator

languages_text = ["Spanish", "English"]
languages_file = ["es_ES", "en_US"]
config = {}

translator = None

def append_to_po_file(file_path, variable, translation, check_translation=True):
    if translation is None:
        return
    if check_translation and check_translation_po_file(file_path, variable):
        return

    with open(file_path, "a") as output_file:
        output_file.write("msgid \""+variable+"\"\n")
        output_file.write("msgstr \""+translation+"\"\n")
        print(f"The variable (\033[92m{variable}\033[0m) has been added to the file")

def check_translation_po_file(file_path, variable):
    try:
        with open(file_path, "r") as input_file:
            for line in input_file:
                if "msgid \""+variable+"\"\n" in line:
                    print(f"The variable (\033[33m{variable}\033[0m) exists, nothing to do")
                    return True  # The variable exists, nothing to do
        return False
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False

def get_translation(variable_to_translate, source_language_code, dest_language_code):
    try:
        translation = translator.translate(variable_to_translate, src=source_language_code, dest=dest_language_code).text
        return translation
    except Exception as e:
        print("\033[91mTranslation not available\033[0m")
        return None

def get_hash_variables(line):
    result = []
    for part in line.split("__('")[1:]:
        result += ["'" + part.split("')")[0] + "'"]
    for part in line.split('__("')[1:]:
        if ", '"+config["domain"]+"')" in part:
            continue
        result += ['"' + part.split('")')[0] + '"']
    return result

def search_php_files(directory_search, translate):
    for root, dirs, files in os.walk(directory_search):
        for file in files:
            if file.endswith(".php"):
                print("Checking file: \033[93m"+os.path.join(root, file)+"\033[0m")
                with open(os.path.join(root, file), "r") as f:
                    lines = f.readlines()
                with open(os.path.join(root, file), "w") as f:
                    for line in lines:
                        if "__(" in line:
                            hash_variables = get_hash_variables(line)
                            for hash_variable in hash_variables:
                                if not hash_variable.endswith(", '"+config["domain"]+"'"):
                                    # Get the variable without quotes
                                    variable = clean_variable(hash_variable)
                                    print("\nText translatable: \033[94m"+variable+"\033[0m")
                                    # Get the variable with domain
                                    domain_variable = "__(" + variable + ", '"+config["domain"]+"')"
                                    line = line.replace("__("+hash_variable+")", domain_variable)
                                    variable_without_quotes = variable[1:-1]
                                    for index, language_file in enumerate(languages_file):
                                        path_po_file = config["path_translations"] + "/" + language_file + ".po"
                                        translation = ""
                                        if translate:
                                            if not check_translation_po_file(path_po_file, variable_without_quotes):
                                                # Se han de quitar el escapar las comillas dobles
                                                variable_to_translate = variable_without_quotes.replace("\\", "")
                                                print("To translate: \033[95m"+variable_to_translate+"\033[0m")
                                                translation = get_translation(variable_to_translate,"ca",language_file[:2])
                                                if translation is not None:
                                                    # Volver a escapar las comillas dobles para el .po
                                                    translation = translation.replace('"', '\\"')
                                                    print(languages_text[index]+" translation: \033[96m"+translation+"\033[0m")
                                        # Append the variable to the .po file
                                        append_to_po_file(path_po_file, variable_without_quotes, translation)
                        f.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search translations in PHP files')
    parser.add_argument('--path_search', default=".", help='Directory to search translations')
    parser.add_argument('--path_translations', default=".", help='Directory save translations')
    parser.add_argument('--rem_old_translations', default=False, help='Remove translations that do not exist in the code')
    parser.add_argument('--generate_mo', default=False, help='Generate the .mo files')
    parser.add_argument('--domain', default="translation", help='Domain of the translations')
    parser.add_argument('--transform_lowercase', default=False, help='Transform string translate to lowercase')
    parser.add_argument('--translate', action='store_true', help='Translate variables')

    if config["translate"]:
        translator = Translator()

    print("Searching translations in \033[93m" + config["path_search"]+"\033[0m")
    search_php_files(config["path_search"], config["translate"])

    if (config["translate"]):

        # Generate the .mo files
        print("Generating .mo files")
        for language_file in languages_file:
            os.system("msgfmt "+config["path_translations"] + "/" + language_file + ".po"+" -o "+config["path_translations"] + "/" + language_file + ".mo")

    print("Done!")