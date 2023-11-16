l = list(range(2, 1000))
for i in l:
    for k in range(2, i):
        if i % k == 0:
            break
    else:
        print(i, end=", ") #  comment

print("2 % 4 != 0")
print("This is true")

def dec_to_hex(denary: int) -> str:
    hexadecimal = ""
    while denary > 0:
        hexadecimal = digit_to_hex(denary%16) + hexadecimal
        denary //= 16
    return hexadecimal


def digit_to_hex(digit: int) -> str:
    hex_digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    return hex_digits[digit-1]


print("334 in hexadecimal is", dec_to_hex(334))

def alt_caps(s: str, current_index: int=0) -> str:
    if current_index == len(s):
        return ""
    if current_index % 2 == 0:
        return s[current_index].upper() + alt_caps(s, current_index+1)
    else:
        return s[current_index].lower() + alt_caps(s, current_index+1)
print(alt_caps("cheese"))

def my_func():
    print("for i in range()", "2 % 4 != 0")
    print("print('Thing')") #  comment

my_func()
var = "abc"
print(len(var))
var2 = "print('doejofn')"

match var:
    case "cba":
        print("execution")
    case "abc":
        try:
            raise Exception
        except Exception:
            print("Something went wrong")
        finally:
            print("execute")
    case _:
        print("wildcard")

"""big string"""
"""_summary_
"docstring"
docstring
"""
print(None)
pass