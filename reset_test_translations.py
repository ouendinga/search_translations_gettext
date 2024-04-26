import os

string = '''<?php
// TEST TRANSLATIONS
__("this is the first test");
__("this is a \\"test\\"");
__("this is a \\"test of work\\"");
__("this is test a \\"test of work\\"");
__("this is a (test of work)");
__('parenthesis test (1900-2000)');
__('alphabetically (A-Z)');
__('(parenthesis)');
__("this is another (test of work)");
__('this is another (test of work)');
__("first test") && __("double test");
__("double test") && __("double test");
?>
<?php echo __("test within PHP (1900-2000)") ?>
<label class="form-test-class" for="test"> <?php echo __("alphabet (a-z)") ?> </label>
<div class="div-test-class"><?php echo __("test") ?> </div>
<?php echo __("(testing)") ?>'''

file_path = "test_folder_translation/test_file_translation.php"

with open(file_path, "w") as file:
	file.write(string)

os.system("rm -rf *.po")
os.system("rm -rf *.mo")