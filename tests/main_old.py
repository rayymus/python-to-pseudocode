"""
Old iteration of converter.py, non-functional
"""

import os.path
import re

'''
INSTRUCTIONS
1. Put the file you want to convert into the same folder as it, and rename it to "py_file.py"
2. Run the converter file
'''

python_file = 'py_file.py'

#  Basic conversion
basic_conversion_rules = {"for": "FOR", "while": "WHILE", "until": "UNTIL",
                          "import": "IMPORT", "class": "CLASS", "def": "FUNCTION", "else:": "ELSE",
                          "except:": "EXCEPT:", "try:": "TRY:", "pass": "PASS", 
                          "in": "IN", "global": "GLOBAL", "%": "MOD", 
                          "return": "RETURN", "if": "IF", "elif": "ELSEIF"}
#  Example, if statements must exit with ENDIF
ending_conversion_rules = {"=": "SET ", "#F": "CALL "}
#  Functions to keyword functions
advanced_conversion_rules = {"print": "OUTPUT", "input": "INPUT"}
#  Usually for base function renaming
prefix_conversions = {"len(": "LENGTH("}
suffix_conversions = {}


def string_scope_check(word: str, 
                       string_scope: bool | str) -> tuple[str, bool | str, str, bool]:
    flag = True
    string, r = "", True
    baseword = word
    for i, character in enumerate(word):
        if string_scope and character == string_scope:
            if not flag:
                string = baseword.removeprefix(word) + baseword.removesuffix(word[i+1:])
                word += word[i+1:]
            else:
                string = word[:i+1]
                word = word[i+1:]
            r = False
            string_scope = False
        elif character in {"'", '"'}:
            string_scope = character
            string = word[i:]
            word = word[:i]
            r = True
            flag = False
    if string_scope and string_scope not in word and flag:
        word = ""
    return word, string_scope, string, r


def l2pseudo(to_pseudo):
    ifelse = None
    function = None
    for_loop = None
    line_index = 0
    while line_index < len(to_pseudo):
        line = to_pseudo[line_index]
        line = (nocomment := no_comment(line))[0]
        line = re.split(r'(\s+)', line)
        for key, value in basic_conversion_rules.items():
            string_scope = False
            for i, word in enumerate(line):
                word = (check := string_scope_check(word, string_scope))[0]
                string_scope = check[1]
                if not word: continue
                if word == key:
                    line[i] = value
                    line[i] = (line[i] + check[2]) if check[3] else (check[2] + line[i])
                if line[i].startswith("FUNCTION"):
                    function = get_indent(line)
        for key, value in prefix_conversions.items():
            string_scope = False
            for i, word in enumerate(line):
                word = (check := string_scope_check(word, string_scope))[0]
                string_scope = check[1]
                if not word: continue
                if word.startswith(key):
                    line[i] = value + word.removeprefix(key)
                    line[i] = (line[i] + check[2]) if check[3] else (check[2] + line[i])
        # for key, value in suffix_conversions.items():
        #     string_scope = False
        #     for i, word in enumerate(line):
        #         word = (check := string_scope_check(word, string_scope))[0]
        #         string_scope = check[1]
        #         if not word: continue
        #         if word.endswith(key):
        #             line[i] = word.removesuffix(key) + value
        #             line[i] = (line[i] + check[2]) if check[3] else (check[2] + line[i])
        line = (("".join(line))[::-1].replace(":", ""))[::-1]
        line = re.split(r'(\s+)', line)
        for key, value in advanced_conversion_rules.items():
            if key in "".join(line):
                line = (nostring := no_string("".join(line)))[0] + nostring[2]
                line = line.replace(f"{key}(", f"{value} ", 1)
                line = line[::-1].replace(")", "", 1)[::-1]
                l = nostring[0].replace(f"{key}(", f"{value} ", 1)
                print(nostring, 'foernferwgrferferfefe')
                line = l + nostring[1] + line[len(l):]
                line = re.split(r'(\s+)', line)

        for i in ("IF", "ELIF"):
            if ("".join(line)).lstrip().startswith(i):
                line = "".join(line)[::-1].replace(":", " THEN", 1)[::-1]
                ifelse = get_indent(line)
                line = re.split(r'(\s+)', line)

        if (linestring := "".join(line)).lstrip().startswith("FOR "):
            if "range(" in linestring:
                linestring = linestring.replace(" IN range(", " = ")
                if len(range_params := linestring.split(",")) == 1:
                    first_param = "0"
                    second_param = range_params[0].split("=")[-1].strip()
                    linestring = linestring.replace(f"{second_param})", f"{first_param} TO {second_param}")
                if len(range_params := linestring.split(",")) != 3:
                    linestring = re.sub(r'FOR\s+(\w+)\s*=\s*(\d+),\s*(\w+)\)', r'FOR \1 = \2 TO \3', linestring)
                elif len(range_params) == 3:
                    linestring = re.sub(r'FOR\s+(\w+)\s*=\s*(\d+),?\s*(\d+)?,?\s*(\d+)?\)', r'FOR \1 = \2 TO \3 STEP \4', linestring)
                var = (re.findall(r'FOR\s(\w+)\s=', linestring))[0]
            else:
                linestring = linestring.replace("FOR ", "FOREACH ")
                var = (re.findall(r'FOREACH\s(\w+)\sIN', linestring))[0]
            line = re.split(r'(\s+)', linestring) #  FOR x = 1 TO 4
            for_loop = get_indent(line), var

        # print(line)
        to_pseudo[line_index] = "".join(line) + (nocomment[1].replace("#", "//"))
        line_index += 1
        indent = ""
        if line_index+1 >= len(to_pseudo):
            if function is not None:
                to_pseudo.append(function+"ENDFUNCTION\n")
            elif ifelse is not None:
                to_pseudo.append(ifelse+"ENDIF\n")
            continue
        print(re.split(r'(\s+)', to_pseudo[line_index+1]))
        indent = get_indent(to_pseudo[line_index+1]) 
        if ifelse is not None and len(indent) <= len(ifelse) and \
        not to_pseudo[line_index+1].startswith(f"{ifelse}else"):
            to_pseudo.insert(line_index+1, ifelse+"ENDIF\n")
            ifelse = None
        elif for_loop is not None and len(indent) <= len(for_loop[0]) and \
        not to_pseudo[line_index+1].startswith(f"{for_loop[0]}else"):
            to_pseudo.insert(line_index+1, f"NEXT {for_loop[1]}\n")
            for_loop = None
        elif function is not None and len(indent) <= len(function):
            to_pseudo.insert(line_index+1, function+"ENDFUNCTION\n")
            function = None
        
    return to_pseudo


def get_indent(line: str | list) -> str:
    line = line if type(line) == str else "".join(line)
    indent = ""
    for k in line:
        if k != " ":
            break
        indent += k  
    return indent 


def no_comment(word: str) -> tuple[str, str] | str:
    string_scope = False
    for i, l in enumerate(word):
        if l in {"'", '"'} and not string_scope:
            string_scope = l
        elif l == string_scope:
            string_scope = False
        elif not string_scope and l == "#":
            return word[:i], word[i:] #  word, comment
    return word, ""


def no_string(word: str) -> tuple[str, str, str]:
    string_scope = False
    string = ""
    string_index = [len(word), len(word)]
    for i, l in enumerate(word):
        if l in {"'", '"'} and not string_scope: #  Enter string scope
            string_scope = l
            string_index[0] = i
        elif l == string_scope: #  Exit string scope
            string_scope = False
            string += l
            string_index[1] = i
        if string_scope:
            string += l
    return word[:string_index[0]], string, word[string_index[1]+1:] #  word, string, word
            

def p2file(to_file):
    py_file = os.path.splitext(os.path.basename(python_file))[0]
    with open(py_file + '_pseudo.txt', 'w') as writer:
        writer.write("".join(to_file))


def main():
    with open(python_file, 'r+') as py_file_reader:
        file_lines = py_file_reader.readlines()
        work_file = l2pseudo(file_lines)
        p2file(work_file)


if __name__ == '__main__':
    main()

#  nested special cases
#  multiple strings


