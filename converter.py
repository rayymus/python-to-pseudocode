import os.path
import re
from typing import Any, Optional


#  Python file to be converted to Pseudocode
python_file = 'sample_tests.py'

#  Basic conversion
basic_conversion_rules = {
    """ Basic conversion of keys to new_keys
    key: new_key
    """
    "for ": "FOR ", "while ": "WHILE ",   
    "import ": "IMPORT ", "class ": "CLASS ", 
    "def ": "FUNCTION ", "in ": "IN ", 
    "global ": "GLOBAL ", "%": "MOD", 
    "return ": "RETURN ", "if ": "IF ",
    "elif ": "ELSEIF ", "len(": "LENGTH(",
    "match ": "SWITCH ", "case ": "CASE ",
    "except ": "CATCH ", "str(": "STR(",
    "int(": "INT(", "float(": "FLOAT(",
    }

""" Keywords that stand alone when edited (commonly when removed ':').
key: new_key
"""
stand_alone = {
    "try": "TRY",
    "finally": "FINALLY", 
    "else": "ELSE",
    "None": "Null",
    "pass": "PASS"
    }

""" Keywords that require and ending keyword when unindented
key: { (base Python)
    "keyword": The ending keyword whe unindented,
    "exclude": The Python form of other keywords that continue the key's statement
}
"""
ending_keywords = {
    "if ": {
        "keyword": "ENDIF",
        "exclude": ["elif", "else"]
    }, 
    "while ": {
        "keyword": "ENDWHILE",
        "exclude": []
    }, 
    "def ": {
        "keyword": "ENDFUNCTION",
        "exclude": []
    },
    "try": {
        "keyword": "ENDTRY",
        "exclude": ["except", "finally", "else"]
    },
    "match ": {
        "keyword": "ENDSWITCH",
        "exclude": ["case"]
    }
    }

#  Functions to keyword functions
func_to_keyword = {"print": "OUTPUT", "input": "INPUT"} 


def python_to_pseudo(lines: list) -> list:
    newlines = []
    current_word = ""
    line_index = 0
    string_scope = []
    ending_keywords_queue = []
    for line in lines[:]:
        line = line.rstrip()
        lines[line_index] = ""
        for i, character in enumerate(line):
            if not string_scope:
                if character in "'\"":
                    if character*2 == lines[line_index].strip()[:2]: #  Docstring handling
                        string_scope.append({"string": "/*", "quotes": character*3})
                        lines[line_index] = ""
                    else:
                        string_scope.append({"string": character, "quotes": character})
                    continue
                elif character in ":\t":
                    continue
                elif character == "#":
                    lines[line_index] += "//" + line[i+1:]
                    break #  Skip rest of line
                current_word += character

                for key in stand_alone:
                    if current_word == key:
                        current_word = stand_alone[key]; break
                    
                if line.strip().startswith("case _"):
                    lines[line_index] = (indent(line)*" ") + "DEFAULT"
                    if (comment:=get_comment(line)) is not None:
                        lines[line_index] += comment.replace("#", "//", 1)
                    break #  Skil rest of line

                if character in {" ", "(", ")", "{", "}", "[", "]", ",", "=", "%"}:
                    if line.strip().startswith("for ") \
                    and (not ending_keywords_queue or indent(line) != first_key(ending_keywords_queue[-1])):
                        for_ = None
                        args = line.strip().split() 
                        var = args[1] 

                        if re.search(r'(?<![\'#"])range\([^)]*\)(?![^\'"]*[\'"])', line) is not None: 
                            #  for i in range(1, 10, 2): 
                            #  FOR var = 1 TO 10 STEP 2
                            range_ = (re.findall(r'(?<![\'#"])range\([^)]*\)(?![^\'"]*[\'"])', line))[0] 
                            args = [arg.strip().removeprefix("range(").removesuffix(")") for arg in range_.split(",")]
                            if len(args) == 1:
                                start = "0"
                                end = args[0]
                            else:
                                start = args[0]
                                end = args[1]
                            step = None if len(args) < 3 else args[2]
                            for_ = f"FOR {var} = {start} TO {end}" + (f" STEP {step}" if step is not None else "")

                        else:
                            #  for var in foo:  #  for i in "abcde":
                            #  FOREACH var IN foo("ab c")  #  FOREACH i IN "abcde"
                            for_ = f"FOREACH {var} IN " + line.lstrip().removeprefix(f"for {var} in ")

                        lines[line_index] = (" "*indent(line)) + for_.removesuffix(":")
                        if (comment:=get_comment(line)) is not None:
                            lines[line_index] += comment.replace("#", "//", 1)
                        ending_keywords_queue.append(
                            {
                                indent(line): {
                                    "keyword": f"NEXT {var}",
                                    "exclude": []
                                }
                            }
                        )
                        current_word = ""
                        break #  Skip rest of linel

                    if current_word in {k for k in ending_keywords}:
                        ending_keywords_queue.append(
                            {
                                indent(line): {
                                    "keyword": ending_keywords[current_word]["keyword"], 
                                    "exclude": ending_keywords[current_word]["exclude"]
                                }
                            }
                        )
                    if current_word in {k for k in basic_conversion_rules}:
                        current_word = basic_conversion_rules[current_word]

                    lines[line_index] += current_word
                    current_word = ""
                
            else: #  String scope handling
                string_scope[-1]["string"] += character
                if character == string_scope[-1]["quotes"] \
                or string_scope[-1]["string"].endswith(string_scope[-1]["quotes"]): #  Close string scope
                    if character == string_scope[-1]["quotes"]:
                        lines[line_index] += string_scope[-1]["string"]
                    else:
                        lines[line_index] = string_scope[-1]["string"][:-3]
                        lines[line_index] += "*/"
                    string_scope.pop(-1)

        #  End of line
        if string_scope and len(string_scope[-1]["quotes"]) == 3:
            lines[line_index] += string_scope[-1]["string"]
            string_scope[-1]["string"] = ""
        lines[line_index] += current_word
        for key, value in func_to_keyword.items():
            pattern = rf'("(?:[^"\\]|\\.)*")|(\'(?:[^\'\\]|\\.)*\')|(#.*$)|(\/\/.*$)|(\/\*[\s\S]*?\*\/)|(\b{key}\b)'
            if (r:=re.findall(pattern, lines[line_index])) and key in r[0]:
                output_string = re.sub(rf'(\s*){key}\(((?:"[^"]*"|[^)])*?)\)', rf'\1{value} \2', lines[line_index])
                output_string = re.sub(rf'(\s*){key}\(([^()]*\([^()]*\)[^()]*)\)', rf'\1{value} \2', output_string)
                lines[line_index] = re.sub(rf'(\s*){key}\((.*?)\)', rf'\1{value} \2', output_string)
        current_word = ""
        newlines.append(lines[line_index])
        line_index += 1

        if ending_keywords_queue:
            for ending_keyword in ending_keywords_queue[::-1]:
                if (line_index == len(lines) \
                or indent(lines[line_index]) <= (i:=first_key(ending_keyword))):   
                    i = 0 if line_index == len(lines) else i
                    if line_index != len(lines) \
                    and (exceptions:=ending_keyword[i]["exclude"]):
                        if any(lines[line_index].startswith((" "*i)+exception) for exception in exceptions):
                            continue
                    newlines.append((" "*i) + ending_keyword[i]["keyword"])
                    ending_keywords_queue.pop(-1)

    return newlines


def indent(line: str) -> int:
    indent_ = 0
    for character in line:
        if character != " ":
            break
        indent_ += 1
    return indent_


def get_comment(line: str) -> Optional[str]:
    string_scope = None
    for i, character in enumerate(line):
        if character in {'"', "'"}:
            string_scope = character
        elif character == string_scope:
            string_scope = None
        elif string_scope is None and character == "#":
            return line[i:]

def first_key(d: dict) -> Any:
    return list(d.keys())[0]


def write_file(lines: list) -> None:
    py_file = os.path.splitext(os.path.basename(python_file))[0]
    with open(py_file + '_pseudo.txt', 'w') as writer:
        writer.write("\n".join(lines))


def main() -> None:
    with open(python_file, 'r+') as py_file_reader:
        file_lines = py_file_reader.readlines()
        new_lines = python_to_pseudo(file_lines)
        write_file(new_lines)
        print("Done")


if __name__ == '__main__':
    main()