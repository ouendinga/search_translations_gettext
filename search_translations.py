# Install requirements: pip install -r requirements.txt
# To execute: python search_translations.py --path=wp-content/plugins --translate

import argparse
import json
import os

from googletrans import Translator

config = {}
language_code_text = {}

translator = None

def append_to_po_file(file_path, variable, translation, check_translation=True):
    if translation is None:
        return
    if check_translation and check_translation_po_file(file_path, variable):
        return

    with open(file_path, "a") as output_file:
        output_file.write("msgid \""+variable+"\"\n")
        output_file.write("msgstr \""+translation+"\"\n")
        print(f"The variable (\033[92m{variable}\033[0m) has been added to the file (\033[92m{file_path}\033[0m)")

def check_translation_po_file(file_path, variable):
    try:
        with open(file_path, "r") as input_file:
            for line in input_file:
                if "msgid \""+variable+"\"\n" in line:
                    print(f"The variable (\033[33m{variable}\033[0m) exists in file (\033[92m{file_path}\033[0m), nothing to do")
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
    print("Searching translations in \033[93m" + directory_search+"\033[0m")
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
                                    for language_code in language_code_text.keys():
                                        if language_code not in config["languages_code_translate"]:
                                            continue
                                        print("\033[93m"+language_code_text[language_code]+"\033[0m")
                                        path_po_file = config["path_translations"] + "/" + language_code + ".po"
                                        translation = ""
                                        if translate:
                                            if not check_translation_po_file(path_po_file, variable_without_quotes):
                                                # Se han de quitar el escapar las comillas dobles
                                                variable_to_translate = variable_without_quotes.replace("\\", "")
                                                print("To translate: \033[95m"+variable_to_translate+"\033[0m")
                                                translation = get_translation(variable_to_translate,"ca",language_code[:2])
                                                if translation is not None:
                                                    # Volver a escapar las comillas dobles para el .po
                                                    translation = translation.replace('"', '\\"')
                                                    print(language_code_text[language_code]+" translation: \033[96m"+translation+"\033[0m")
                                        # Append the variable to the .po file
                                        append_to_po_file(path_po_file, variable_without_quotes, translation)
                        f.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search translations in PHP files')
    parser.add_argument('--path_search', default=".", help='Directory to search translations')
    parser.add_argument('--path_translations', default=".", help='Directory save translations')
    parser.add_argument('--domain', default="translation", help='Domain of the translations')
    parser.add_argument('--translate', action='store_true', help='Translate variables')
    parser.add_argument('--rem_old_translations', default=False, help='Remove translations that do not exist in the code')
    parser.add_argument('--generate_mo', default=False, help='Generate the .mo files')
    parser.add_argument('--transform_lowercase', default=False, help='Transform string translate to lowercase')
    parser.add_argument('--languages_code_translate', default=[], help='Languages code to translate')
    parser.add_argument('--file_config', default=False, help='File config params. If is set, the other params are ignored')
    args = parser.parse_args()

    # Load the config params
    if not args.file_config:
        config["path_search"] = args.path_search
        config["path_translations"] = args.path_translations
        config["domain"] = args.domain
        config["translate"] = args.translate
        config["rem_old_translations"] = args.rem_old_translations
        config["generate_mo"] = args.generate_mo
        config["transform_lowercase"] = args.transform_lowercase
        config["languages_code_translate"] = args.languages_code_translate
    else:
        with open(args.file_config, "r") as file:
            config = json.load(file)

    # print(f"Config params: {config}")

    # Load the language code and text available
    with open("language_code_text.json", "r") as file:
        language_code_text = json.load(file)

    if config["translate"]:
        # Init the translator
        translator = Translator()

    search_php_files(config["path_search"], config["translate"])

    if (config["translate"]):

        # Generate the .mo files
        print("Generating .mo files")
        for language_code in language_code_text.keys():
            if language_code not in config["languages_code_translate"]:
                continue
            os.system("msgfmt "+config["path_translations"] + "/" + language_code + ".po"+" -o "+config["path_translations"] + "/" + language_code + ".mo")

    print("Done!")