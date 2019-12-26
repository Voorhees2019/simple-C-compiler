# file path: C:\Users\Voorhees\PycharmProjects\test\c_code.txt
import re
import bitstring

keyword_list = ['auto', 'double', 'int', 'struct', 'break', 'else', 'long', 'switch', 'case', 'enum', 'register',
                'typedef', 'char', 'extern', 'return', 'union', 'continue', 'for', 'signed', 'void', 'do', 'if',
                'static', 'while', 'default', 'goto', 'sizeof', 'volatile', 'const', 'float', 'short', 'unsigned']

operators_dict = {"+": "PLUS", "-": "MINUS", "*": "MUL", "/": "DIV", "%": "MOD", "=": "ASSIGN", "+=": "PLUSEQ",
                  "-=": "MINUSEQ", "*=": "MULEQ", "/=": "DIVEQ", "%=": "MODEQ", "==": "EQUAL", "++": "INC",
                  "--": "DEC", "|": "LOGOR", "&": "LOGAND", "||": "OR", "&&": "AND", '!=': "NOTEQ", '>=': "GREATEQ",
                  '<=': "LOWEQ", '>': "GREATER", '<': "SMALLER", '!': "LOGNOT", '^': "XOR", '~': "COMPLEMENT",
                  '^=': "XOREQ", '~=': "COMPLEMENTEQ", '<<': "LEFTSHIFT", '>>': "RIGHTSHIFT", '<<=': "LEFTSHIFTEQ",
                  '>>=': "RIGHTSHIFTEQ", '&=': "LOGANDEQ", '|=': "LOGOREQ"}

delimiters_dict = {"\t": "TAB", "\n": "NEWLINE", "(": "LPAR", ")": "RPAR", "[": "LBRACE", "]": "RBRACE", "{": "LCBRACE",
                   "}": "RCBRACE", ":": "COLON", ",": "COMMA", ";": "SEMICOL", '...': 'ELLIPSIS'}

var_pattern = re.compile(r"[a-zA-Z][a-zA-Z0-9_]*")  # variables(identifiers)
cyrillic_pattern = re.compile(r"[\u0400-\u04FF]")  # cyrillic letters
int_pattern = re.compile(r"^[1-9]+[0-9]*$|^0$")  # int
float_pattern = re.compile(r"^[0-9]+\.[0-9]*$|^\.[0-9]+$")  # float
undefined_pattern = re.compile(r"\d+[a-zA-Z_]+[a-zA-Z0-9_]*")  # undefined(vars like "2temp")


def tokenize(line):
    tokens = line.split(" ")
    for delimiter in delimiters_dict.keys():
        for i in range(len(tokens)):
            for token in tokens:
                if token != delimiter and delimiter in token:
                    position = token.find(delimiter)
                    tokens.remove(token)
                    token = token.replace(delimiter, " ", 1)
                    start = token[:position]
                    end = token[position + 1:]
                    tokens.append(delimiter)
                    tokens.append(start)
                    tokens.append(end)

    for token in tokens:
        if " " in token:
            tokens.remove(token)
            token = token.split(" ")
            tokens += token

    c1 = tokens.count("")
    for i in range(c1):
        tokens.remove("")

    reg = re.compile(r'\+\+|--|==|!=|>=|<=|&&|\|\||<<|>>|\+=|-=|\*=|/=|\^=|%=|&=|\|=|<<=|>>=|\.\.\.|[=*/+%\-><!~&|^,]')
    operators_list = []
    for token in tokens:
        operators_list += re.findall(reg, token)
    operators_list.sort(key=len, reverse=True)

    for operator in operators_list:
        for token in tokens:
            if token != operator and operator in token and token not in operators_list:
                position = token.find(operator)
                tokens.remove(token)
                token = token.replace(operator, " ", 1)
                start = token[:position]
                end = token[position + 1:]
                tokens.append(operator)
                tokens.append(start)
                tokens.append(end)

    c1 = tokens.count("")
    for i in range(c1):
        tokens.remove("")

    tokens = list(set(tokens))
    lst = []
    for i in tokens:
        if i.isalnum():
            for j in re.finditer(i, line):
                lst.append((i, j.start()))
        elif 1 < len(i) <= 2 and i[0] == i[1]:
            for j in re.finditer(f'\{i[0]}\{i[1]}', line):
                lst.append((i, j.start()))
        elif i in operators_dict or i in delimiters_dict or i in '.':
            for j in re.finditer(f'\{i}', line):
                lst.append((i, j.start()))
        else:
            for j in re.finditer(f'{i}', line):
                lst.append((i, j.start()))
    sorted_token_list = sorted(lst, key=lambda x: x[1])

    tokens_greater_one_symbols = []
    for i in tokens:
        if len(i) > 1:
            if i.isalnum():
                for j in re.finditer(i, line):
                    tokens_greater_one_symbols.append((i, j.start(), j.end()))
            elif 1 < len(i) <= 2 and i[0] == i[1]:
                for j in re.finditer(f'\{i[0]}\{i[1]}', line):
                    tokens_greater_one_symbols.append((i, j.start(), j.end()))
            elif i in operators_dict or i in delimiters_dict or i in '.':
                for j in re.finditer(f'\{i}', line):
                    tokens_greater_one_symbols.append((i, j.start(), j.end()))
            else:
                for j in re.finditer(f'{i}', line):
                    tokens_greater_one_symbols.append((i, j.start(), j.end()))
    # print(f'tokens_greater_one_symbols: {tokens_greater_one_symbols}')
    # delete all repetitive tokens(like identifier "n" in keyword token "begin")
    for key, start, end in tokens_greater_one_symbols:
        for token, index in sorted_token_list:
            if start < index < end:
                sorted_token_list.remove((token, index))

    for key, start, end in tokens_greater_one_symbols:
        for token, index in sorted_token_list:
            if token + token == key and start <= index < end:
                sorted_token_list.remove((token, index))

    # delete from tokens all variables "n" that are in keywords like i'n't, unsig'n'ed ...
    for key, start, end in tokens_greater_one_symbols:
        # make 1 more cycle here not to jump over tokens that should be deleted if the previous is removed
        for i in range(len(sorted_token_list)):
            for token, index in sorted_token_list:
                if (token != key) and (token in key) and (start <= index <= end) and (key in keyword_list):
                    sorted_token_list.remove((token, index))
    # print(f'sorted_token_list: {sorted_token_list}')
    c = 0
    while c < len(sorted_token_list) - 1:
        if sorted_token_list[c][1] == sorted_token_list[c + 1][1]:
            if len(sorted_token_list[c][0]) > len(sorted_token_list[c + 1][0]):
                sorted_token_list.remove((sorted_token_list[c + 1][0], sorted_token_list[c][1]))
            elif len(sorted_token_list[c][0]) < len(sorted_token_list[c + 1][0]):
                sorted_token_list.remove((sorted_token_list[c][0], sorted_token_list[c][1]))
            else:
                c += 1
        else:
            c += 1

    return sorted_token_list


# def check_token(token):
#     if token in keyword_list:
#         print(token + " KEYWORD")
#     elif token in operators_dict.keys():
#         print(token + " ", operators_dict[token])
#     elif token in delimiters_dict:
#         description = delimiters_dict[token]
#         if description == 'TAB' or description == 'NEWLINE':
#             print(description)
#         else:
#             print(token + " ", description)
#     elif re.match(var_pattern, token):
#         print(token + ' IDENTIFIER')
#     elif re.match(float_pattern, token):
#         print(token + ' FLOAT')
#     elif re.match(int_pattern, token):
#         print(token + ' INT')
#     elif re.match(undefined_pattern, token):
#         print(token + ' UNDEFINED')


def lexer_analyzer(path):
    flag1 = True
    while flag1:
        try:
            f = open(path).read()
            flag1 = False
        except FileNotFoundError:
            print("Invalid path. File doesn\'t found. Try again")
            path = input("Enter Source Code's Path:\n")
            lexer_analyzer(path)
        except PermissionError:
            print("Permission denied. Try again")
            path = input("Enter Source Code's Path:\n")
            lexer_analyzer(path)
        except OSError:
            print("Invalid argument. Try again")
            path = input("Enter Source Code's Path:\n")
            lexer_analyzer(path)

    if re.findall(cyrillic_pattern, f):
        print('An Error occurred. Cyrillic characters are present/')
        exit(1)
    lines = f.split("\n")
    count = 0
    for line in lines:
        count += 1
        sorted_token_list = tokenize(line)
        print("\n#LINE ", count)
        print(line)
        # print("Tokens list: ", tokens)
        # print(f'Sorted Token list {sorted_token_list}')
        # for token in tokens:
        #     check_token(token)

        yield sorted_token_list, line, count


def syntax_analyzer(sorted_token_list, line, line_number):
    global operators_dict
    del operators_dict["++"], operators_dict["--"]
    del operators_dict['='], operators_dict['+='], operators_dict['-='], operators_dict['*='], operators_dict['/='], \
        operators_dict['&='], operators_dict['|='], operators_dict['^='], operators_dict['~='], operators_dict['%='], \
        operators_dict['<<='], operators_dict['>>=']
    dec_inc_dict = {"++": "INC", "--": "DEC"}
    assign_dict = {"=": "ASSIGN", "+=": "PLUSEQ", "-=": "MINUSEQ", "*=": "MULEQ", "/=": "DIVEQ", "%=": "MODEQ",
                   '^=': "XOREQ", '~=': "COMPLEMENTEQ", '<<=': "LEFTSHIFTEQ", '>>=': "RIGHTSHIFTEQ", '&=': "LOGANDEQ",
                   '|=': "LOGOREQ"}
    undefined = []
    token_table = []

    def make_token_table(sorted_token_list):
        for token, index in sorted_token_list:
            if token in keyword_list:
                token_table.append({'token': token, 'index': f'{index}', 'type': 'keyword', 'name': f'{token}'})
            elif token in dec_inc_dict:
                token_table.append(
                    {'token': token, 'index': f'{index}', 'type': 'dec_inc', 'name': dec_inc_dict[token]})
            elif token in operators_dict.keys():
                token_table.append(
                    {'token': token, 'index': f'{index}', 'type': 'operator', 'name': operators_dict[token]})
            elif token in assign_dict.keys():
                token_table.append(
                    {'token': token, 'index': f'{index}', 'type': 'assignment', 'name': assign_dict[token]})
            elif token in delimiters_dict:
                token_table.append(
                    {'token': token, 'index': f'{index}', 'type': 'delimiter', 'name': delimiters_dict[token]})
            elif re.match(var_pattern, token):
                token_table.append({'token': token, 'index': f'{index}', 'type': 'identifier', 'name': f'{token}'})
            elif re.match(float_pattern, token):
                # for negative float numbers
                if token_table[-1]['name'] == 'MINUS' and token_table[-2]['name'] == 'ASSIGN':
                    negative_num_ind = token_table[-1]['index']
                    token_table.pop()
                    token_table.append({'token': f'-{token}', 'index': f'{negative_num_ind}', 'type': 'float', 'name': f'-{token}'})
                    continue
                token_table.append({'token': token, 'index': f'{index}', 'type': 'float', 'name': f'{token}'})
            elif re.match(int_pattern, token):
                # for negative int numbers
                if token_table[-1]['name'] == 'MINUS' and token_table[-2]['name'] == 'ASSIGN' or \
                        token_table[-2]['name'] == 'LBRACE':
                    negative_num_ind = token_table[-1]['index']
                    token_table.pop()
                    token_table.append({'token': f'-{token}', 'index': f'{negative_num_ind}', 'type': 'int', 'name': f'-{token}'})
                    continue
                token_table.append({'token': token, 'index': f'{index}', 'type': 'int', 'name': f'{token}'})
            elif re.match(undefined_pattern, token):
                undefined.append((token, index))
            else:
                undefined.append((token, index))

    make_token_table(sorted_token_list)
    # print(f'token_table: {token_table}')
    if undefined:
        print(f'ERROR: undefined character in line {line_number} in index = {undefined[0][1]}')
        exit(1)

    def equal_number_of_brackets(line):
        lpar = line.count('(')
        rpar = line.count(')')
        lbrace = line.count('[')
        rbrace = line.count(']')
        lcbrace = line.count('{')
        rcbrace = line.count('}')
        if lpar == rpar and lbrace == rbrace and lcbrace == rcbrace:
            return True
        else:
            return False

    if not equal_number_of_brackets(line):
        print(f"ERROR: not equal amount of brackets")
        exit(1)

    def check_syntax(token_table, index):
        token = token_table[index]
        # the last token must be SEMICOL
        if token_table[-1]['name'] != 'SEMICOL':
            print(f'ERROR: ";" expected in line {line_number} in index {int(token_table[-1]["index"]) + 1}')
            exit(1)
        # if the last token is SEMICOL, go to the next line
        if index == len(token_table) - 1:
            if token['name'] != 'SEMICOL':
                print(f'ERROR: ";" expected in line {line_number} in index {token["index"]}')
                exit(1)
            else:
                return
        # the first token or the next one after SEMICOL must be an identifier, inc, dec or keyword(type)
        if index == 0:
            if token['type'] != 'keyword':
                print(f'ERROR: incorrect token at the beginning of line {line_number} in index {token["index"]}')
                exit(1)
        if token_table[index - 1]['name'] == 'SEMICOL':
            if token['type'] != 'identifier' and token['name'] != 'DEC' and token['name'] != 'INC' and \
                    token['name'] != 'double' and token['name'] != 'int' and token['name'] != 'char' and \
                    token['name'] != 'float' and token['name'] != 'short' and token['name'] != 'unsigned' and \
                    token['name'] != 'long' and token['name'] != 'signed':
                print(
                    f'ERROR: incorrect character at the beginning of command in line {line_number} in index {token["index"]}')
                exit(1)
        # if current token is identifier
        if token['type'] == 'identifier':
            if token_table[index + 1]['type'] == 'operator':
                check_syntax(token_table, index + 1)
            elif token_table[index + 1]['type'] == 'dec_inc':
                check_syntax(token_table, index + 1)
            elif token_table[index + 1]['type'] == 'assignment':
                if token_table[index - 1]['name'] == 'SEMICOL' or token_table[index - 1]['name'] == 'double' or \
                        token_table[index - 1]['name'] == 'int' or token_table[index - 1]['name'] == 'char' or \
                        token_table[index - 1]['name'] == 'float' or token_table[index - 1]['name'] == 'unsigned' or \
                        token_table[index - 1]['name'] == 'signed' or token_table[index - 1]['name'] == 'short' or \
                        token_table[index - 1]['name'] == 'long' or token_table[index - 1]['name'] == 'MUL' or \
                        token_table[index - 1]['name'] == 'COMMA':
                    check_syntax(token_table, index + 1)
                else:
                    print(f'ERROR: invalid assignment in line {line_number} in index {token["index"]}')
                    exit(1)
            elif token_table[index + 1]['type'] == 'identifier' or token_table[index + 1]['type'] == 'int' or \
                    token_table[index + 1]['type'] == 'float' or token_table[index + 1]['type'] == 'keyword':
                print(
                    f'ERROR: incorrect statement after identifier in line {line_number} in index {token_table[index + 1]["index"]}')
                exit(1)
            elif token_table[index + 1]['type'] == 'delimiter':
                if token_table[index + 1]['name'] == 'RPAR' or token_table[index + 1]['name'] == 'RBRACE' or \
                        token_table[index + 1]['name'] == 'LPAR' or token_table[index + 1]['name'] == 'LBRACE' or \
                        token_table[index + 1]['name'] == 'SEMICOL' or token_table[index + 1]['name'] == 'COMMA':
                    check_syntax(token_table, index + 1)
        # if current token is increment or decrement
        if token['type'] == 'dec_inc':
            if (token_table[index - 1]['type'] == 'identifier' and token_table[index + 1]['name'] == 'SEMICOL') or \
                    (token_table[index - 1]['name'] == 'SEMICOL' and token_table[index + 1]['type'] == 'identifier'):
                check_syntax(token_table, index + 1)
            else:
                print(f'ERROR: invalid increment or decrement assignment in index {token["index"]}')
                exit(1)
        # if current token is operator
        if token['type'] == 'operator':
            if token_table[index + 1]['type'] == 'identifier' or token_table[index + 1]['type'] == 'int' or \
                    token_table[index + 1]['type'] == 'float' or token_table[index + 1]['name'] == 'LPAR':
                check_syntax(token_table, index + 1)
            else:
                print(
                    f'ERROR: invalid character after operator in line {line_number} in index = {token_table[index + 1]["index"]}')
                exit(1)
        # if current token is assignment
        if token['type'] == 'assignment':
            if token_table[index + 1]['type'] == "identifier" or token_table[index + 1]['type'] == "int" or \
                    token_table[index + 1]['type'] == "float" or token_table[index + 1]['name'] == "LPAR" or \
                    token_table[index + 1]['name'] == "LOGAND":
                check_syntax(token_table, index + 1)
            else:
                print(
                    f'ERROR: invalid statement after assignment in line {line_number} in index = {token_table[index + 1]["index"]}')
                exit(1)
        # if current token is a number
        if token['type'] == 'int' or token['type'] == 'float':
            if token_table[index + 1]['name'] == 'SEMICOL' or token_table[index + 1]['type'] == 'operator' or \
                    token_table[index + 1]['name'] == 'RPAR' or token_table[index + 1]['name'] == 'RBRACE' or \
                    token_table[index + 1]['name'] == 'COMMA':
                check_syntax(token_table, index + 1)
            else:
                print(
                    f'ERROR: invalid character after the number in line {line_number} in index = {token_table[index + 1]["index"]}')
                exit(1)
        # if current token is a delimiter
        if token['type'] == 'delimiter':
            if token['name'] == 'LPAR':
                if token_table[index + 1]['type'] == 'identifier' or token_table[index + 1]['name'] == 'LPAR' or \
                        token_table[index + 1]['type'] == 'int' or token_table[index + 1]['type'] == 'float' or \
                        (token_table[index + 1]['name'] == 'RPAR' and token_table[index - 1]['type'] == 'identifier') or \
                        token_table[index + 1]['name'] == 'LBRACE':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid statement after lpar bracket in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
            elif token['name'] == 'LBRACE':
                if token_table[index + 1]['name'] == 'LPAR' and token_table[index + 2]['name'] == 'RPAR':
                    print(
                        f'ERROR: no argument given to brackets in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
                if token_table[index + 1]['type'] == 'identifier' or token_table[index + 1]['name'] == 'LPAR' or \
                        token_table[index + 1]['type'] == 'int':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid statement after lbrace bracket in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
            elif token['name'] == 'SEMICOL':
                check_syntax(token_table, index + 1)
            elif token['name'] == 'COMMA':
                if token_table[index + 1]['type'] == 'identifier':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid character after comma in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
            elif token['name'] == 'RPAR':
                if token_table[index + 1]['name'] == 'SEMICOL' or token_table[index + 1]['type'] == 'operator' or \
                        token_table[index + 1]['name'] == 'RPAR' or token_table[index + 1]['name'] == 'RBRACE' or \
                        token_table[index + 1]['name'] == 'COMMA':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid statement after rpar bracket in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
            elif token['name'] == 'RBRACE':
                if token_table[index + 1]['name'] == 'LBRACE' or token_table[index + 1]['name'] == 'SEMICOL' or \
                        token_table[index + 1]['type'] == 'operator' or token_table[index + 1]['name'] == 'RPAR' or \
                        token_table[index + 1]['name'] == 'COMMA' or token_table[index + 1]['type'] == 'assignment':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid statement after rbrace bracket in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)
        # if current token is a keyword
        if token['type'] == 'keyword':
            if token['name'] == 'double' or token['name'] == 'int' or token['name'] == 'float' or \
                    token['name'] == 'short' or token['name'] == 'char' or token['name'] == 'signed' or \
                    token['name'] == 'unsigned':
                if token_table[index + 1]['type'] == 'identifier' or token_table[index + 1]['name'] == 'MUL':
                    check_syntax(token_table, index + 1)
                else:
                    print(
                        f'ERROR: invalid declaration in line {line_number} in index = {token_table[index + 1]["index"]}')
                    exit(1)

    check_syntax(token_table, 0)
    operators_dict["++"] = 'INC'
    operators_dict["--"] = "DEC"
    operators_dict['='], operators_dict['+='], operators_dict['-='], operators_dict['*='], operators_dict['/='], \
    operators_dict['&='], operators_dict['|='], operators_dict['^='], operators_dict['~='], operators_dict['%='], \
    operators_dict['<<='], operators_dict['>>='] = "ASSIGN", "PLUSEQ", "MINUSEQ", "MULEQ", "DIVEQ", "LOGANDEQ", \
                                                   "LOGOREQ", "XOREQ", "COMPLEMENTEQ", "MODEQ", "LEFTSHIFTEQ", "RIGHTSHIFTEQ"
    return token_table, line, line_number


def semantics_check(general_token_table, line, line_number):
    lst1 = []
    for i in range(len(general_token_table)):
        if general_token_table[i]['name'] == 'SEMICOL':
            lst1.append(i)
    operations = []  # list of lists(consist of token dicts) commands from ; to ;
    operations.append(list(general_token_table[0:lst1[0] + 1]))
    for i in range(len(lst1) - 1):
        operations.append(list(general_token_table[lst1[i] + 1:lst1[i + 1] + 1]))
    ops_list = line.split(';')
    ops_list.pop()  # list of string commands from ; to ;
    declared_vars = []
    declared_lists = []
    types = ['char', 'short', 'int', 'float', 'double']

    def assign_value_all_vars_with_this_name(i, j, v):
        try:
            for k in range(len(operations)):
                for t in range(len(operations[k])):
                    if operations[i][j]['name'] == operations[k][t]['name']:
                        # this key also adds to general_token_table
                        operations[k][t]['value'] = v
        except KeyError:
            print(f'ERROR: in line {line_number} in index {operations[i][j]["index"]}. '
                  f'The identifier \'{operations[i][j]["name"]}\' was not declared')
            exit(1)

    def assign_value_all_lists_with_this_name(i, j, ind, v):
        try:
            for k in range(len(operations)):
                for t in range(len(operations[k])):
                    if operations[i][j]['name'] == operations[k][t]['name']:
                        # this key also adds to general_token_table
                        operations[k][t]['array'][ind] = v
        except KeyError:
            print(f'ERROR: in line {line_number} in index {operations[i][j]["index"]}. '
                  f'The identifier \'{operations[i][j]["name"]}\' was not declared')
            exit(1)

    def convert_to_IEEE754(number):
        def binary_float(num):
            return bitstring.BitArray(float=num, length=32).bin

        def binary_to_hex(num):
            return hex(int(num, 2)).replace('0x', '')

        bin_float_number = binary_float(number)
        hex4bits_list = []
        for i in range(len(bin_float_number)):
            if i % 4 == 3:
                hex4bits_list.append(bin_float_number[i - 3:i + 1])
        hex_number = '0x' + ''.join(list(map(binary_to_hex, hex4bits_list)))
        return int(hex_number, 16)

    def write_to_asm_file(string):
        asm_file = open('asm_file.txt', 'a')
        asm_file.write(f'{string}\n')
        asm_file.close()

    def delele_PARs():
        # delete all LPARs and RPARs if they are like a[(n)]
        p = 0
        while p < len(expression_token_table):
            if expression_token_table[p]['name'] == 'LPAR' or \
                    expression_token_table[p]['name'] == 'RPAR':
                del expression_token_table[p]
            p += 1

    def is_onlyAND_or_onlyOR():
        op_lst2 = [expression_token_table2[x] for x in range(len(expression_token_table2)) if
                   expression_token_table2[x]['type'] == 'operator']
        if len(op_lst2) == 1 and (op_lst2[0]['name'] == 'AND' or op_lst2[0]['name'] == 'OR'):
            return True
        return False

    asm_file = open('asm_file.txt', 'w')
    asm_file.write(f'mov eq1, {convert_to_IEEE754(1)}\n')
    asm_file.write(f'mov eq0, {convert_to_IEEE754(0)}\n')
    asm_file.close()
    # check declaration scope
    for i in range(len(operations)):
        for j in range(len(operations[i])):
            if operations[i][0]['type'] == 'keyword':
                id_type = operations[i][0]['name']
                if operations[i][j]['type'] == 'identifier':
                    # error id redeclaration of var
                    if operations[i][j]['name'] in declared_vars and operations[i][j+1]['name'] != 'RBRACE' and \
                            operations[i][j-1]['name'] != 'ASSIGN':
                        print(f'ERROR: redeclaration of \'{operations[i][j]["vartype"]}\' identifier \'{operations[i][j]["name"]}\' '
                              f'in line {line_number} in index {operations[i][j]["index"]}')
                        exit(1)
                    # add to all the identifiers in operations(table of tokens) a new key "vartype"
                    for k in range(len(operations)):
                        for t in range(len(operations[k])):
                            if operations[i][j]['name'] == operations[k][t]['name']:
                                # this key also adds to general_token_table
                                operations[k][t]['vartype'] = f'{id_type}'
                                if operations[i][j + 1]['name'] != 'LBRACE':
                                    declared_vars.append(operations[k][t]['name'])
                    # assign zero value to uninitialized vars
                    if (operations[i][j+1]['name'] != 'ASSIGN' and operations[i][j - 1]['type'] == 'keyword') or \
                            (operations[i][j + 1]['name'] == 'SEMICOL' and operations[i][j - 1]['type'] == 'keyword') or\
                            (operations[i][j+1]['name'] == 'COMMA' and operations[i][j-1]['name'] == 'COMMA') or \
                            (operations[i][j + 1]['name'] == 'SEMICOL' and operations[i][j - 1]['name'] == 'COMMA') or \
                            (operations[i][j + 1]['name'] == 'SEMICOL' and operations[i][j - 1]['name'] == 'MUL') or \
                            (operations[i][j + 1]['name'] == 'COMMA' and operations[i][j - 1]['name'] == 'MUL'):
                        # or (operations[i][j+2]['name'] == operations[i][j]['name']):
                        for k in range(len(operations)):
                            for t in range(len(operations[k])):
                                if operations[i][j]['name'] == operations[k][t]['name']:
                                    operations[k][t]['value'] = 0
                    # array declaration
                    if operations[i][j+1]['name'] == 'LBRACE':
                        declared_lists.append(operations[i][j]['name'])
                        # if var in braces
                        if operations[i][j+2]['type'] == 'identifier':
                            # check if the var was declared before
                            was_before = 0
                            if operations[i][j + 2]['name'] in declared_vars:
                                was_before = 1
                                # check the compatibility of types in array declaration
                                if operations[i][j + 2]['vartype'] == 'int' or operations[i][j + 2]['vartype'] == 'short' or \
                                        operations[i][j+2]['vartype'] == 'char':
                                    # add to all the list vars field "amount_of_elements"
                                    for k in range(len(operations)):
                                        for t in range(len(operations[k])):
                                            if operations[i][j]['name'] == operations[k][t]['name']:
                                                operations[k][t]['amount_of_array_elements'] = operations[i][j + 2]['value']
                                                operations[k][t]['array'] = [0 for q in range(operations[i][j + 2]['value'])]
                                else:
                                    print(
                                        f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 2]["index"]}. '
                                        f'Array elements must be "char", "int" or "short" but \'{operations[i][j + 2]["vartype"]}\' was given')
                                    exit(1)
                            if was_before == 0:
                                print(f'ERROR: in line {line_number} in index {operations[i][j+2]["index"]}.'
                                      f' Identifier \'{operations[i][j+2]["name"]}\' was not declared before')
                                exit(1)
                        # if int in braces
                        if operations[i][j+2]['type'] == 'int':
                            # add to all the list vars field "amount_of_elements"
                            for k in range(len(operations)):
                                for t in range(len(operations[k])):
                                    if operations[i][j]['name'] == operations[k][t]['name']:
                                        operations[k][t]['amount_of_array_elements'] = int(operations[i][j+2]['name'])
                                        operations[k][t]['array'] = [0 for q in range(int(operations[i][j+2]['name']))]
                # check correct assignment in vars declaration
                if operations[i][j]['name'] == 'ASSIGN':
                    # error if defining and immediately assigning array value like "a[2] = 4"
                    if operations[i][j - 1]['name'] == 'RBRACE':
                        print(
                            f'ERROR: invalid initializer in line {line_number} in index {operations[i][j + 1]["index"]}')
                        exit(1)
                    # if after assignment is identifier
                    if operations[i][j + 1]['type'] == 'identifier':
                        proper_var = 0
                        # check if the var was declared before
                        if operations[i][j+1]['name'] in declared_vars:
                            # check the compatibility of types in assignment
                            if types.index(operations[i][j + 1]['vartype']) <= types.index(operations[i][j-1]['vartype']):
                                proper_var = 1
                            else:
                                print(
                                    f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 1]["index"]}. '
                                    f'Could not convert \'{operations[i][j + 1]["vartype"]}\' to \'{operations[i][j - 1]["vartype"]}\'')
                                exit(1)
                        # assign declared vars the value of the var they are assigned to(in declare scope)
                        if proper_var == 1:
                            v = operations[i][j+1]['value']
                            assign_value_all_vars_with_this_name(i, j-1, v)
                        else:
                            print(
                                f'ERROR: in line {line_number} in index = {operations[i][j + 1]["index"]}.'
                                f' Identifier \'{operations[i][j + 1]["name"]}\' is undeclared')
                            exit(1)
                    # if after assignment is int or float number
                    if operations[i][j+1]['type'] == 'int':
                        if operations[i][j-1]['vartype'] == 'char' or operations[i][j-1]['vartype'] == 'short' or \
                                operations[i][j-1]['vartype'] == 'int':
                            v = int(operations[i][j+1]['name'])
                            assign_value_all_vars_with_this_name(i, j-1, v)
                        elif operations[i][j-1]['vartype'] == 'float' or operations[i][j-1]['vartype'] == 'double':
                            v = float(operations[i][j + 1]['name'])
                            assign_value_all_vars_with_this_name(i, j - 1, v)
                    elif operations[i][j+1]['type'] == 'float':
                        if operations[i][j-1]['vartype'] == 'float' or operations[i][j-1]['vartype'] == 'double':
                            v = float(operations[i][j+1]['name'])
                            assign_value_all_vars_with_this_name(i, j-1, v)
                        else:
                            print(f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 1]["index"]}. '
                                  f'Could not convert \'{operations[i][j + 1]["type"]}\' to \'{operations[i][j - 1]["vartype"]}\'')
                            exit(1)
    # check initialization scope
    for i in range(len(operations)):
        for j in range(len(operations[i])):
            aaa = operations[i][j]['name']
            # check if statement after ';' starts not with keyword
            if operations[i][0]['type'] != 'keyword':
                # if statement starts with dec or inc
                if operations[i][j]['type'] == 'dec_inc':
                    # if dec
                    if operations[i][j]['name'] == 'DEC':
                        if operations[i][j + 1]['type'] == 'identifier':
                            write_to_asm_file(f'movups xmm0, {operations[i][j+1]["name"]}')
                            write_to_asm_file(f'movups xmm1, eq1')
                            write_to_asm_file(f'subss xmm0, xmm1')
                            write_to_asm_file(f'movups {operations[i][j+1]["name"]}, xmm0')
                            v = operations[i][j + 1]['value'] - 1
                            assign_value_all_vars_with_this_name(i, j + 1, v)
                        elif operations[i][j - 1]['type'] == 'identifier':
                            write_to_asm_file(f'movups xmm0, {operations[i][j - 1]["name"]}')
                            write_to_asm_file(f'movups xmm1, eq1')
                            write_to_asm_file(f'subss xmm0, xmm1')
                            write_to_asm_file(f'movups {operations[i][j - 1]["name"]}, xmm0')
                            v = operations[i][j - 1]['value'] - 1
                            assign_value_all_vars_with_this_name(i, j - 1, v)
                    # if inc
                    elif operations[i][j]['name'] == 'INC':
                        if operations[i][j + 1]['type'] == 'identifier':
                            write_to_asm_file(f'movups xmm0, {operations[i][j + 1]["name"]}')
                            write_to_asm_file(f'movups xmm1, eq1')
                            write_to_asm_file(f'addss xmm0, xmm1')
                            write_to_asm_file(f'movups {operations[i][j + 1]["name"]}, xmm0')
                            v = operations[i][j + 1]['value'] + 1
                            assign_value_all_vars_with_this_name(i, j + 1, v)
                        elif operations[i][j - 1]['type'] == 'identifier':
                            write_to_asm_file(f'movups xmm0, {operations[i][j - 1]["name"]}')
                            write_to_asm_file(f'movups xmm1, eq1')
                            write_to_asm_file(f'addss xmm0, xmm1')
                            write_to_asm_file(f'movups {operations[i][j - 1]["name"]}, xmm0')
                            v = operations[i][j - 1]['value'] + 1
                            assign_value_all_vars_with_this_name(i, j - 1, v)
                # if statement starts with identifier
                if operations[i][j]['type'] == 'identifier':
                    # check if the var was declared
                    if operations[i][j]['name'] in declared_vars or operations[i][j]['name'] in declared_lists:
                        pass
                    else:
                        print(f'ERROR: in line {line_number} in index {operations[i][j]["index"]}. '
                              f'The identifier \'{operations[i][j]["name"]}\' was not declared')
                        exit(1)
                    # error if a without '[' if a is array
                    if operations[i][j]['name'] in declared_lists and operations[i][j+1]['name'] != 'LBRACE':
                        print(f'ERROR: expected \'[\' in line {line_number} in index {operations[i][j+1]["index"]}. '
                              f'\'{operations[i][j]["name"]}\' is array')
                        exit(1)
                    # incorrect type if try to reach with '[' to identifier
                    if operations[i][j+1]['name'] == 'LBRACE' and operations[i][j]['name'] not in declared_lists:
                        print(
                            f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 1]["index"]}. '
                            f'\'{operations[i][j]["name"]}\' is not array')
                        exit(1)
                    # if '=' is after identifier in initializing scope
                    if operations[i][j+1]['name'] == "ASSIGN":
                        # assigning the identifier to 'int' number in initializing scope
                        if operations[i][j+2]['type'] == 'int' and operations[i][j+3]['name'] == 'SEMICOL':
                            if operations[i][j]['vartype'] == 'int' or operations[i][j]['vartype'] == 'char' or \
                                    operations[i][j]['vartype'] == 'short':
                                v = int(operations[i][j+2]['name'])
                                assign_value_all_vars_with_this_name(i, j, v)
                                write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                            elif operations[i][j]['vartype'] == 'float' or operations[i][j]['vartype'] == 'double':
                                v = float(operations[i][j + 2]['name'])
                                assign_value_all_vars_with_this_name(i, j, v)
                                write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                        # assigning the identifier to 'float' number in initializing scope
                        elif operations[i][j + 2]['type'] == 'float' and operations[i][j + 3]['name'] == 'SEMICOL':
                            if operations[i][j]['vartype'] == 'float' or operations[i][j]['vartype'] == 'double':
                                v = float(operations[i][j+2]['name'])
                                assign_value_all_vars_with_this_name(i, j, v)
                                write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                            else:
                                print(
                                    f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j+2]["index"]}. '
                                    f'Could not convert \'{operations[i][j+2]["type"]}\' to \'{operations[i][j]["vartype"]}\'')
                                exit(1)
                        # assigning identifier value to another identifier in initializing scope
                        if operations[i][j+2]['type'] == 'identifier' and operations[i][j+3]['name'] == 'SEMICOL':
                            # error if try to assign array without '[' to some var like "s = a" where a is array
                            if operations[i][j+2]['name'] in declared_lists and operations[i][j+3]['name'] != 'LBRACE':
                                print(f'ERROR: in line {line_number} in index = {operations[i][j + 2]["index"]}. '
                                      f'Incorrect assignment, \'{operations[i][j+2]["name"]}\' is array, \'[\' expected')
                                exit(1)
                            # check if var was declared
                            if operations[i][j+2]['name'] in declared_vars:
                                # check the compatibility
                                if types.index(operations[i][j+2]['vartype']) <= types.index(operations[i][j]['vartype']):
                                    v = operations[i][j+2]['value']
                                    assign_value_all_vars_with_this_name(i, j, v)
                                    write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                                else:
                                    print(
                                        f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 2]["index"]}. '
                                        f'Could not convert \'{operations[i][j + 2]["vartype"]}\' to \'{operations[i][j]["vartype"]}\'')
                                    exit(1)
                            else:
                                print(f'ERROR: in line {line_number} in index {operations[i][j+2]["index"]}. '
                                      f'The identifier \'{operations[i][j+2]["name"]}\' was not declared')
                                exit(1)
                        # assigning identifier value to array's element value
                        if operations[i][j+2]['type'] == 'identifier' and operations[i][j+2]['name'] in declared_lists \
                                and operations[i][j+6]['name'] == 'SEMICOL':
                            # s=a[3] check the compatibility. if vartype(a) <= vartype(s)
                            if types.index(operations[i][j+2]['vartype']) <= types.index(operations[i][j]['vartype']):
                                # if in array brackets is an 'int' number
                                if operations[i][j + 4]['type'] == 'int':
                                    # check if number in brackets is in available amount of array elements
                                    if int(operations[i][j + 4]['name']) < operations[i][j + 2]['amount_of_array_elements']:
                                        v = operations[i][j+2]['array'][int(operations[i][j+4]['name'])]
                                        assign_value_all_vars_with_this_name(i, j, v)
                                        write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                                    else:
                                        print(f'ERROR: in line {line_number} in index {operations[i][j + 4]["index"]}. '
                                              f'Value is not in available array\'s element range.'
                                              f' Max value can be {operations[i][j + 2]["amount_of_array_elements"]-1}')
                                        exit(1)
                                # if in array brackets is an identifier
                                elif operations[i][j + 4]['type'] == 'identifier':
                                    # check if the var was declared before
                                    if operations[i][j+4]['name'] in declared_vars:
                                        # s=a[n] check the compatibility. it vartype(n) <= 'int'
                                        if types.index(operations[i][j + 4]['vartype']) <= types.index('int'):
                                            v = operations[i][j+2]['array'][operations[i][j+4]['value']]
                                            assign_value_all_vars_with_this_name(i, j, v)
                                            write_to_asm_file(f'mov {operations[i][j]["name"]}, {convert_to_IEEE754(operations[i][j]["value"])}')
                                        else:
                                            print(
                                                f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 4]["index"]}. '
                                                f'Could not convert \'{operations[i][j + 4]["vartype"]}\' to \'int\'')
                                            exit(1)
                                    else:
                                        print(f'ERROR: in line {line_number} in index {operations[i][j + 4]["index"]}. '
                                              f'The identifier \'{operations[i][j + 4]["name"]}\' was not declared')
                                        exit(1)
                            else:
                                print(
                                    f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 2]["index"]}. '
                                    f'Could not convert \'{operations[i][j + 2]["vartype"]}\' to \'{operations[i][j]["vartype"]}\'')
                                exit(1)
                    # if current token is array
                    if operations[i][j+1]['name'] == 'LBRACE':
                        # check if identifier in brackets was declared before
                        if operations[i][j+2]['type'] == 'identifier' and operations[i][j+2]['name'] not in declared_vars:
                            print(f'ERROR: in line {line_number} in index {operations[i][j+2]["index"]}. '
                                  f'The identifier \'{operations[i][j+2]["name"]}\' was not declared')
                            exit(1)
                        # check if "a[10]" is out of range
                        if operations[i][j+2]['type'] == 'int':
                            if int(operations[i][j + 2]['name']) >= operations[i][j]['amount_of_array_elements'] or \
                                    int(operations[i][j+2]['name']) < 0:
                                print(f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                      f'Value is not in available array\'s element range.'
                                      f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                exit(1)
                        # check if "a[n]" is out of range
                        elif operations[i][j+2]['type'] == 'identifier':
                            if types.index(operations[i][j + 2]['vartype']) > types.index('int'):
                                print(f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 2]["index"]}. '
                                      f'Could not convert \'{operations[i][j + 2]["vartype"]}\' to \'int\'')
                                exit(1)
                            if operations[i][j+2]['value'] >= operations[i][j]['amount_of_array_elements'] or \
                                    operations[i][j+2]['value'] < 0:
                                print(f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                      f'Value is not in available array\'s element range.'
                                      f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                exit(1)

                        # check if "a[2];"
                        # if operations[i][j+4]['name'] == 'SEMICOL':
                        #     # check if 'int' number is in brackets
                        #     if operations[i][j+2]['type'] == 'int':
                        #         # "a[40];" error if range of a is 39
                        #         if int(operations[i][j+2]['name']) >= operations[i][j]['amount_of_array_elements']:
                        #             print(f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                        #                   f'Value is not in available array\'s element range.'
                        #                   f' Max value can be {operations[i][j]["amount_of_array_elements"]-1}')
                        #             exit(1)
                        #     # check if identifier is in brackets
                        #     elif operations[i][j+2]['type'] == 'identifier':
                        #         # check if it is 'int' identifier
                        #         if types.index(operations[i][j+2]['vartype']) > types.index('int'):
                        #             print(
                        #                 f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j+2]["index"]}. '
                        #                 f'Could not convert \'{operations[i][j+2]["vartype"]}\' to \'int\'')
                        #             exit(1)

                        # check if it's array's element assignment "a[2]=1" or "a[n]=2" if n is 'int'
                        if operations[i][j+4]['name'] == 'ASSIGN' and operations[i][j-1]['name'] == 'SEMICOL':
                            # if 'int' number is after '='
                            if operations[i][j + 5]['type'] == 'int':
                                # check the compatibility "a[1]=2". correct if vartype(2) <= vartype(a)
                                if types.index('int') <= types.index(operations[i][j]['vartype']):
                                    # if 'int' number is in brackets
                                    if operations[i][j + 2]['type'] == 'int':
                                        # check if 'int' number in brackets is proper for array's elements range
                                        if int(operations[i][j + 2]['name']) < operations[i][j]['amount_of_array_elements']:
                                            ind = int(operations[i][j+2]['name'])
                                            v = int(operations[i][j+5]['name'])
                                            assign_value_all_lists_with_this_name(i, j, ind, v)
                                            write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                            write_to_asm_file(f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j+2]["name"])*4}], eax')
                                        else:
                                            print(
                                                f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                f'Value is not in available array\'s element range.'
                                                f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                            exit(1)
                                    # if identifier is in brackets
                                    elif operations[i][j + 2]['type'] == 'identifier':
                                        # "a[n]=45" check if vartype(n) <= 'int'
                                        if types.index(operations[i][j+2]['vartype']) <= types.index('int'):
                                            # check if the vars value is not greater than array's range
                                            if operations[i][j+2]['value'] < operations[i][j]['amount_of_array_elements']:
                                                ind = operations[i][j+2]['value']
                                                v = int(operations[i][j+5]['name'])
                                                assign_value_all_lists_with_this_name(i, j, ind, v)
                                                write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                                write_to_asm_file(
                                                    f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j + 2]["value"]) * 4}], eax')
                                            else:
                                                print(
                                                    f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                    f'Value is not in available array\'s element range.'
                                                    f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                                exit(1)
                                        else:
                                            print(
                                                f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 5]["index"]}. '
                                                f'Could not convert \'{operations[i][j+2]["vartype"]}\' to \'int\'')
                                            exit(1)
                                else:
                                    print(
                                        f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j+5]["index"]}. '
                                        f'Could not convert \'int\' to \'{operations[i][j]["vartype"]}\'')
                                    exit(1)
                            # if 'float' number is after '='
                            elif operations[i][j + 5]['type'] == 'float':
                                # check the compatibility "a[1]=2.3". correct if vartype(2) <= vartype(a)
                                if types.index('float') <= types.index(operations[i][j]['vartype']):
                                    # if 'int' number is in brackets
                                    if operations[i][j + 2]['type'] == 'int':
                                        # check if 'int' number in brackets is proper for array's elements range
                                        if int(operations[i][j + 2]['name']) < operations[i][j]['amount_of_array_elements']:
                                            ind = int(operations[i][j + 2]['name'])
                                            v = float(operations[i][j + 5]['name'])
                                            assign_value_all_lists_with_this_name(i, j, ind, v)
                                            write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                            write_to_asm_file(
                                                f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j + 2]["name"]) * 4}], eax')
                                        else:
                                            print(
                                                f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                f'Value is not in available array\'s element range.'
                                                f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                            exit(1)
                                    # if identifier is in brackets
                                    elif operations[i][j + 2]['type'] == 'identifier':
                                        # "a[n]=45.9" check if vartype(n) <= 'int'
                                        if types.index(operations[i][j + 2]['vartype']) <= types.index('int'):
                                            # check if the vars value is not greater than array's range
                                            if operations[i][j + 2]['value'] < operations[i][j]['amount_of_array_elements']:
                                                ind = operations[i][j + 2]['value']
                                                v = float(operations[i][j + 5]['name'])
                                                assign_value_all_lists_with_this_name(i, j, ind, v)
                                                write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                                write_to_asm_file(
                                                    f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j + 2]["value"]) * 4}], eax')
                                            else:
                                                print(
                                                    f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                    f'Value is not in available array\'s element range.'
                                                    f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                                exit(1)
                                        else:
                                            print(
                                                f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 5]["index"]}. '
                                                f'Could not convert \'{operations[i][j + 2]["vartype"]}\' to \'int\'')
                                            exit(1)
                                else:
                                    print(
                                        f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 5]["index"]}. '
                                        f'Could not convert \'float\' to \'{operations[i][j]["vartype"]}\'')
                                    exit(1)
                            # if identifier is after '='
                            elif operations[i][j + 5]['type'] == 'identifier':
                                # check the compatibility "a[1]=n". correct if vartype(n) <= vartype(a)
                                if types.index(operations[i][j+5]['vartype']) <= types.index(operations[i][j]['vartype']):
                                    # if 'int' number is in brackets
                                    if operations[i][j + 2]['type'] == 'int':
                                        # check if 'int' number in brackets is proper for array's elements range
                                        if int(operations[i][j + 2]['name']) < operations[i][j]['amount_of_array_elements']:
                                            ind = int(operations[i][j + 2]['name'])
                                            v = float(operations[i][j + 5]['value'])
                                            assign_value_all_lists_with_this_name(i, j, ind, v)
                                            write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                            write_to_asm_file(
                                                f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j + 2]["name"]) * 4}], eax')
                                        else:
                                            print(
                                                f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                f'Value is not in available array\'s element range.'
                                                f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                            exit(1)
                                    # if identifier is in brackets
                                    elif operations[i][j + 2]['type'] == 'identifier':
                                        # "a[n]=b" check if vartype(n) <= 'int'
                                        if types.index(operations[i][j + 2]['vartype']) <= types.index('int'):
                                            # check if the vars value is not greater than array's range
                                            if operations[i][j + 2]['value'] < operations[i][j]['amount_of_array_elements']:
                                                ind = operations[i][j + 2]['value']
                                                v = operations[i][j + 5]['value']
                                                assign_value_all_lists_with_this_name(i, j, ind, v)
                                                write_to_asm_file(f'mov eax, {convert_to_IEEE754(v)}')
                                                write_to_asm_file(
                                                    f'mov dword ptr[{operations[i][j]["name"]} + {int(operations[i][j + 2]["value"]) * 4}], eax')
                                            else:
                                                print(
                                                    f'ERROR: in line {line_number} in index {operations[i][j + 2]["index"]}. '
                                                    f'Value is not in available array\'s element range.'
                                                    f' Max value can be {operations[i][j]["amount_of_array_elements"] - 1}')
                                                exit(1)
                                        else:
                                            print(
                                                f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 5]["index"]}. '
                                                f'Could not convert \'{operations[i][j + 2]["vartype"]}\' to \'int\'')
                                            exit(1)
                                else:
                                    print(
                                        f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j + 5]["index"]}. '
                                        f'Could not convert \'{operations[i][j+5]["vartype"]}\' to \'{operations[i][j]["vartype"]}\'')
                                    exit(1)
                    # check if after '=' is expression
                    if operations[i][j+1]['name'] == 'ASSIGN' and operations[i][j+3]['name'] != 'SEMICOL':
                        res_vartype = ''
                        assign_to = operations[i][j]['vartype']
                        s1 = ops_list[i][ops_list[i].index(operations[i][j+1]['token'])+1:]  # s1: n&&b==a[n]
                        expression = tokenize(s1)
                        # expression is a list of tokens after assignment
                        expression = [x for (x, y) in expression]
                        logic_ops = ['&&', '||', '==', '!=', '>', '>=', '<', '<=']
                        unary_ops = ['+', '-', '*', '/', '%', '&', '|', '^']
                        # filling res_vartype with first var's type to compare with then
                        flag = 0
                        for p in range(len(expression)):
                            for o in range(len(general_token_table)):
                                if expression[p] == general_token_table[o]['name'] and expression[p] in declared_vars:
                                    res_vartype = general_token_table[o]['vartype']
                                    flag = 1
                                    break
                                elif expression[p] == general_token_table[o]['name'] and expression[p] in declared_lists:
                                    res_vartype = general_token_table[o]['vartype']
                                    flag = 1
                                    break
                                elif expression[p] == general_token_table[o]['name'] and \
                                        general_token_table[o]['type'] == 'int':
                                    res_vartype = 'char'
                                    flag = 1
                                elif expression[p] == general_token_table[o]['name'] and \
                                        general_token_table[o]['type'] == 'float':
                                    res_vartype = 'float'
                                    flag = 1
                            if flag == 1:
                                break
                        c = 0
                        while c < len(expression):
                            if expression[c] in declared_vars:
                                for o in range(len(general_token_table)):
                                    if general_token_table[o]['name'] == expression[c]:
                                        if types.index(general_token_table[o]['vartype']) > types.index(res_vartype):
                                            res_vartype = general_token_table[o]['vartype']
                            elif expression[c] in declared_lists:
                                del expression[c+1:c+4]
                                for o in range(len(general_token_table)):
                                    if general_token_table[o]['name'] == expression[c]:
                                        if types.index(general_token_table[o]['vartype']) > types.index(res_vartype):
                                            res_vartype = general_token_table[o]['vartype']
                            elif re.match(float_pattern, expression[c]):
                                if types.index('float') > types.index(res_vartype):
                                    res_vartype = 'float'
                            c += 1

                        # check the compatibility of res_vartype and assign_to var
                        if types.index(res_vartype) > types.index(assign_to):
                            print(
                                f'ERROR: type incompatibility in line {line_number} in index = {operations[i][j]["index"]}. '
                                f'Could not convert \'{res_vartype}\' to \'{assign_to}\'')
                            exit(1)
                    # TODO
                        expression_token_table = operations[i][operations[i].index(operations[i][j + 2]):-1]
                        expression_token_table2 = operations[i][operations[i].index(operations[i][j + 2]):-1]
                        # print(f'expression_token_table: {expression_token_table}')
                        c = 0
                        left_is_var_or_num = 0
                        left_is_arr_elem = 0
                        right_is_var_or_num = 0
                        right_is_arr_elem = 0
                        # while len(expression_token_table):
                        while c < len(expression_token_table):
                            delele_PARs()
                            # look for '==' or '!='
                            if expression_token_table[c]['name'] == 'EQUAL' or expression_token_table[c]['name'] == 'NOTEQ' or \
                                    (expression_token_table[c]['name'] == 'AND' and is_onlyAND_or_onlyOR()) or \
                                    (expression_token_table[c]['name'] == 'OR' and is_onlyAND_or_onlyOR()):
                                # what is before EQUAL or NOTEQ or AND or OR
                                # if before '==' or '!=' or '&&' or '||' is identifier
                                if expression_token_table[c-1]['type'] == 'identifier':
                                    left_is_var_or_num = 1
                                    write_to_asm_file(f'mov {expression_token_table[c-1]["name"]}, '
                                                      f'{convert_to_IEEE754(expression_token_table[c-1]["value"])}')
                                    write_to_asm_file(f'movups xmm0, {expression_token_table[c-1]["name"]}')
                                # if before '==' or '!=' or '&&' or '||' is number
                                elif expression_token_table[c-1]['type'] == 'int' or expression_token_table[c-1]['type'] == 'float':
                                    left_is_var_or_num = 1
                                    write_to_asm_file(f'mov num_before_eq, '
                                                      f'{convert_to_IEEE754(float(expression_token_table[c - 1]["name"]))}')
                                    write_to_asm_file(f'movups xmm0, num_before_eq')
                                # if before '==' or '!=' or '&&' or '||' is array's element
                                elif expression_token_table[c-1]['name'] == 'RBRACE':
                                    left_is_arr_elem = 1
                                    # if in array's brackets is number like 'a[5]==' or 'a[5]!='
                                    if expression_token_table[c-2]['type'] == 'int':
                                        write_to_asm_file(f'mov esi, {expression_token_table[c-2]["name"]}')
                                        write_to_asm_file(f'movups xmm0, [4 * esi] + {expression_token_table[c-4]["name"]}')
                                    # if in array's brackets is identifier like 'a[n]==' or 'a[5]!='
                                    elif expression_token_table[c - 2]['type'] == 'identifier':
                                        write_to_asm_file(f'mov esi, {expression_token_table[c - 2]["value"]}')
                                        write_to_asm_file(f'movups xmm0, [4 * esi] + {expression_token_table[c - 4]["name"]}')
                                # what is after EQUAL or NOTEQ or AND or OR
                                # if after '==' or '!=' or '&&' or '||' is identifier
                                if expression_token_table[c+1]['name'] in declared_vars:
                                    right_is_var_or_num = 1
                                    write_to_asm_file(f'mov {expression_token_table[c + 1]["name"]}, '
                                                      f'{convert_to_IEEE754(expression_token_table[c + 1]["value"])}')
                                    write_to_asm_file(f'movups xmm1, {expression_token_table[c + 1]["name"]}')
                                # if after '==' or '!=' or '&&' or '||' is number
                                elif expression_token_table[c+1]['type'] == 'int' or expression_token_table[c+1]['type'] == 'float':
                                    right_is_var_or_num = 1
                                    write_to_asm_file(f'mov num_after_eq, '
                                                      f'{convert_to_IEEE754(float(expression_token_table[c + 1]["name"]))}')
                                    write_to_asm_file(f'movups xmm1, num_after_eq')
                                # if after '==' or '!=' or '&&' or '||' is array's element
                                elif expression_token_table[c + 1]['name'] in declared_lists:
                                    right_is_arr_elem = 1
                                    # if in array's brackets is number like '==a[5]' or '!=a[5]'
                                    if expression_token_table[c + 3]['type'] == 'int':
                                        write_to_asm_file(f'mov esi, {expression_token_table[c + 3]["name"]}')
                                        write_to_asm_file(
                                            f'movups xmm1, [4 * esi] + {expression_token_table[c + 1]["name"]}')
                                    # if in array's brackets is identifier like '==a[n]' or '!=a[n]'
                                    elif expression_token_table[c + 3]['type'] == 'identifier':
                                        write_to_asm_file(f'mov esi, {expression_token_table[c + 3]["value"]}')
                                        write_to_asm_file(
                                            f'movups xmm1, [4 * esi] + {expression_token_table[c + 1]["name"]}')
                                # MAIN comiss
                                if expression_token_table[c]['name'] == 'EQUAL' or expression_token_table[c]['name'] == 'NOTEQ':
                                    write_to_asm_file(f'comiss xmm0, xmm1')
                                elif expression_token_table[c]['name'] == 'AND' or expression_token_table[c]['name'] == 'OR':
                                    write_to_asm_file(f'comiss xmm0, eq0')
                                if expression_token_table[c]['name'] == 'EQUAL' or expression_token_table[c]['name'] == 'AND':
                                    write_to_asm_file(f'jz mark1')
                                elif expression_token_table[c]['name'] == 'NOTEQ' or expression_token_table[c]['name'] == 'OR':
                                    write_to_asm_file(f'jnz mark1')
                                if expression_token_table[c]['name'] == 'EQUAL' or expression_token_table[c]['name'] == 'NOTEQ':
                                    write_to_asm_file(f'movups xmm2, eq0')
                                elif expression_token_table[c]['name'] == 'AND' or expression_token_table[c]['name'] == 'OR':
                                    write_to_asm_file(f'movups xmm2, xmm1')
                                write_to_asm_file(f'jmp mark2')
                                write_to_asm_file(f'mark1:')
                                if expression_token_table[c]['name'] == 'EQUAL' or expression_token_table[c]['name'] == 'NOTEQ':
                                    write_to_asm_file(f'\t\tmovups xmm2, eq1')
                                elif expression_token_table[c]['name'] == 'AND' or expression_token_table[c]['name'] == 'OR':
                                    write_to_asm_file(f'\t\tmovups xmm2, xmm0')
                                write_to_asm_file(f'mark2:')
                                # if there is only one operation in command '==' or '!='
                                op_lst = [expression_token_table[x] for x in range(len(expression_token_table)) if expression_token_table[x]['type']=='operator']
                                if len(op_lst) == 1 and (op_lst[0]['name'] == 'EQUAL' or op_lst[0]['name'] == 'NOTEQ' or
                                        op_lst[0]['name'] == 'AND' or op_lst[0]['name'] == 'OR'):
                                    write_to_asm_file(f'\t\tmovups {operations[i][j]["name"]}, xmm2')
                                if left_is_var_or_num and right_is_var_or_num:
                                    expression_token_table[c-1] = {'name': 'xmm2'}
                                    del expression_token_table[c:c+2]
                                elif left_is_var_or_num and right_is_arr_elem:
                                    expression_token_table[c-1] = {'name': 'xmm2'}
                                    del expression_token_table[c:c+5]
                                elif left_is_arr_elem and right_is_var_or_num:
                                    expression_token_table[c-4] = {'name': 'xmm2'}
                                    del expression_token_table[c-3:c+2]
                                elif left_is_arr_elem and right_is_arr_elem:
                                    expression_token_table[c-4] = {'name': 'xmm2'}
                                    del expression_token_table[c-3:c+5]
                                c = 0
                            # look for '&&' or '||'
                            if expression_token_table[c]['name'] == 'AND' or expression_token_table[c]['name'] == 'OR':
                                # check what is before AND or OR
                                # if before '&&' or '||' is 'xmm2'
                                if expression_token_table[c-1]['name'] == 'xmm2':
                                    # check what is after '&&' or '||'
                                    # if after '&&' or '||' is identifier
                                    if expression_token_table[c+1]['name'] in declared_vars:
                                        write_to_asm_file(f'\t\tmovups xmm3, {expression_token_table[c+1]["name"]}')
                                    # if after '&&' or '||' is number
                                    elif expression_token_table[c+1]['type'] == 'int' or expression_token_table[c+1]['type'] == 'float':
                                        write_to_asm_file(f'\t\tmov num_after_and_or, '
                                                          f'{convert_to_IEEE754(float(expression_token_table[c+1]["name"]))}')
                                        write_to_asm_file(f'\t\tmovups xmm3, num_after_and_or')
                                    # if after '&&' or '||' is array's element
                                    if expression_token_table[c+1]['name'] in declared_lists:
                                        # if in array's brackets is number like '&&a[5]' or '||a[5]'
                                        if expression_token_table[c + 3]['type'] == 'int':
                                            write_to_asm_file(f'\t\tmov esi, {expression_token_table[c + 3]["name"]}')
                                            write_to_asm_file(
                                                f'\t\tmovups xmm3, [4 * esi] + {expression_token_table[c + 1]["name"]}')
                                        # if in array's brackets is identifier like '&&a[n]' or '||a[n]'
                                        elif expression_token_table[c + 3]['type'] == 'identifier':
                                            write_to_asm_file(f'\t\tmov esi, {expression_token_table[c + 3]["value"]}')
                                            write_to_asm_file(
                                                f'\t\tmovups xmm3, [4 * esi] + {expression_token_table[c + 1]["name"]}')
                                    # main comiss for '&&' or '||'
                                    write_to_asm_file(f'\t\tcomiss xmm3, eq0')
                                    if expression_token_table[c]['name'] == 'AND':
                                        write_to_asm_file(f'\t\tjz mark3')
                                    elif expression_token_table[c]['name'] == 'OR':
                                        write_to_asm_file(f'\t\tjnz mark3')
                                    write_to_asm_file(f'\t\tmovups {operations[i][j]["name"]}, xmm2')
                                    write_to_asm_file(f'\t\tjmp mark4')
                                    write_to_asm_file(f'mark3:')
                                    write_to_asm_file(f'\t\tmovups {operations[i][j]["name"]}, xmm3')
                                    write_to_asm_file(f'mark4:')

                                # check what is after AND or OR
                                # if after '&&' or '||' is 'xmm2'
                                elif expression_token_table[c+1]['name'] == 'xmm2':
                                    # check what is before '&&' or '||'
                                    # if before '&&' or '||' is identifier
                                    if expression_token_table[c-1]['name'] in declared_vars:
                                        write_to_asm_file(f'\t\tmovups xmm3, {expression_token_table[c-1]["name"]}')
                                    # if before '&&' or '||' is number
                                    elif expression_token_table[c-1]['type'] == 'int' or expression_token_table[c-1]['type'] == 'float':
                                        write_to_asm_file(f'\t\tmov num_before_and_or, '
                                                          f'{convert_to_IEEE754(float(expression_token_table[c-1]["name"]))}')
                                        write_to_asm_file(f'\t\tmovups xmm3, num_before_and_or')
                                    # if before '&&' or '||' is array's element
                                    if expression_token_table[c-1]['name'] == 'RBRACE':
                                        # if in array's brackets is number like 'a[5]&&' or 'a[5]||'
                                        if expression_token_table[c - 2]['type'] == 'int':
                                            write_to_asm_file(f'\t\tmov esi, {expression_token_table[c - 2]["name"]}')
                                            write_to_asm_file(
                                                f'\t\tmovups xmm3, [4 * esi] + {expression_token_table[c - 4]["name"]}')
                                        # if in array's brackets is identifier like 'a[n]&&' or 'a[n]||'
                                        elif expression_token_table[c - 2]['type'] == 'identifier':
                                            write_to_asm_file(f'\t\tmov esi, {expression_token_table[c - 2]["value"]}')
                                            write_to_asm_file(
                                                f'\t\tmovups xmm3, [4 * esi] + {expression_token_table[c - 4]["name"]}')
                                    # main comiss for '&&' or '||'
                                    write_to_asm_file(f'\t\tcomiss xmm3, eq0')
                                    if expression_token_table[c]['name'] == 'AND':
                                        write_to_asm_file(f'\t\tjz mark3')
                                    elif expression_token_table[c]['name'] == 'OR':
                                        write_to_asm_file(f'\t\tjnz mark3')
                                    write_to_asm_file(f'\t\tmovups {operations[i][j]["name"]}, xmm2')
                                    write_to_asm_file(f'\t\tjmp mark4')
                                    write_to_asm_file(f'mark3:')
                                    write_to_asm_file(f'\t\tmovups {operations[i][j]["name"]}, xmm3')
                                    write_to_asm_file(f'mark4:')
                            c += 1
        # TODO make available to generate assembly code for array's element assignment like 'a[n]=b||n'

    # print(f'expression_token_table1: {expression_token_table}')
    # print(f'operations: {operations}')
    # print(f'general_tt: {general_token_table}')
    # print(f'declared_vars: {declared_vars}')
    # print(f'declared_lists: {declared_lists}')
    # print(f's1: {s1}')
    # print(f'expression: {expression}')
    # print(f'assign_to: {assign_to}')
    # print(f'res_vartype: {res_vartype}')


def main():
    source_code_path = input("Enter Source Code's Path:\n")
    lexem_table = lexer_analyzer(source_code_path)
    for sorted_token_list, line, line_number in lexem_table:
        syntax_res = syntax_analyzer(sorted_token_list, line, line_number)
        semantics_check(*syntax_res)


if __name__ == "__main__":
    main()
