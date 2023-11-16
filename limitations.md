Does not take into account type annotations.

Does not correctly change double print statements [i.e print("print(abc)")].

Does not take into account string prefixes [i.e. r"abc", f"{foo}"].

Does not change "with" statements or file handling.

Does not change object methods [i.e str.upper() to UPPER(str)].

Cannot handle code with Syntax Errors correctly.
