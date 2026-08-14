import re

# ==========================================================
# MINI C++ COMPILER
# Features:
# 1. Lexical Analysis
# 2. Syntax Analysis
# 3. Semantic Analysis
# 4. Symbol Table Generation
# 5. Python Tkinter GUI with Dark/Light Theme Toggle
# ==========================================================


# -------------------- TOKEN SETTINGS --------------------

KEYWORDS = {
    "int", "float", "double", "char", "string", "bool", "long", "short",
    "if", "else", "while", "for", "return", "cout", "cin",
    "true", "false", "include", "iostream", "random", "using", "namespace", "std", "main", "endl", "for", "while", "random_device", "mt19937", "uniform_int_distribution"
}

DATATYPES = {"int", "float", "double", "char", "string", "bool", "long", "short"}

OPERATORS = {
    "+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">=",
    "++", "--", "+=", "-=", "*=", "/=", "<<", ">>", "::"
}

SEPARATORS = {
    ";", ",", "(", ")", "{", "}", "[", "]"
}


# -------------------- SYMBOL TABLE --------------------

class SymbolTable:
    def __init__(self):
        self.table = []
        self.memory = 1000

    def clear(self):
        self.table = []
        self.memory = 1000

    def exists(self, name):
        for item in self.table:
            if item["Name"] == name:
                return True
        return False

    def get(self, name):
        for item in self.table:
            if item["Name"] == name:
                return item
        return None

    def add(self, name, type_, value="None", scope="global"):
        if not self.exists(name):
            self.table.append({
                "Name": name,
                "Type": type_,
                "Value": value,
                "Scope": scope,
                "Memory": self.memory
            })
            self.memory += 1

    def update_value(self, name, value):
        for item in self.table:
            if item["Name"] == name:
                item["Value"] = value
                return


symbol_table = SymbolTable()


# -------------------- LEXICAL ANALYZER --------------------

def lexical_analyzer(code):
    code = remove_comments(code)
    tokens = []

    raw_tokens = re.findall(
        r'"[^"]*"|\'.\'|#include|[a-zA-Z_]\w*|\d+\.\d+|\d+|==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|<<|>>|::|[+\-*/%=<>;(),{}\[\]#:]|\S',
        code
    )

    for token in raw_tokens:
        if token in KEYWORDS:
            tokens.append((token, "KEYWORD"))

        elif token in OPERATORS:
            tokens.append((token, "OPERATOR"))

        elif token in SEPARATORS:
            tokens.append((token, "SEPARATOR"))

        elif re.fullmatch(r"\d+\.\d+", token):
            tokens.append((token, "FLOAT_NUMBER"))

        elif token.isdigit():
            tokens.append((token, "NUMBER"))

        elif re.fullmatch(r"'.'", token):
            tokens.append((token, "CHAR_VALUE"))

        elif re.fullmatch(r'"[^"]*"', token):
            tokens.append((token, "STRING_VALUE"))

        elif re.fullmatch(r"[a-zA-Z_]\w*", token):
            tokens.append((token, "IDENTIFIER"))

        else:
            tokens.append((token, "INVALID_TOKEN"))

    return tokens


# -------------------- HELPER FUNCTIONS --------------------


def remove_comments(code):
    """
    Removes C++ single-line comments // from code.
    It does not remove // when it appears inside a string or char literal.
    """
    cleaned_lines = []

    for line in code.split("\n"):
        new_line = ""
        in_string = False
        in_char = False
        i = 0

        while i < len(line):
            ch = line[i]

            if ch == '"' and not in_char:
                # Ignore escaped quotes
                if i == 0 or line[i - 1] != "\\":
                    in_string = not in_string
                new_line += ch
                i += 1
                continue

            if ch == "'" and not in_string:
                # Ignore escaped quotes
                if i == 0 or line[i - 1] != "\\":
                    in_char = not in_char
                new_line += ch
                i += 1
                continue

            if not in_string and not in_char and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break

            new_line += ch
            i += 1

        cleaned_lines.append(new_line)

    return "\n".join(cleaned_lines)


def remove_empty_lines(lines):
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line != "":
            clean_lines.append(line)
    return clean_lines


def get_value_type(value):
    value = value.strip()

    if re.fullmatch(r"\d+", value):
        return "int"

    elif re.fullmatch(r"\d+\.\d+", value):
        return "double"

    elif re.fullmatch(r"'.'", value):
        return "char"

    elif re.fullmatch(r'"[^"]*"', value):
        return "string"

    elif value in {"true", "false"}:
        return "bool"

    elif re.fullmatch(r"[a-zA-Z_]\w*", value):
        item = symbol_table.get(value)
        if item:
            return item["Type"]
        return "unknown"

    return "unknown"


def is_numeric_type(type_name):
    return type_name in {"int", "float", "double", "long", "short"}


def check_type_compatibility(left_type, right_type):
    if left_type == right_type:
        return True

    if is_numeric_type(left_type) and is_numeric_type(right_type):
        return True

    return False


# -------------------- C++ STRUCTURE + BODY HELPERS --------------------

def split_code_lines(code):
    raw_lines = code.split("\n")
    lines = []
    for line_no, line in enumerate(raw_lines, start=1):
        stripped = line.strip()
        if stripped != "":
            lines.append((line_no, stripped))
    return lines


def split_top_level_commas(text):
    parts = []
    current = ""
    in_string = False
    in_char = False

    for i, ch in enumerate(text):
        if ch == '"' and not in_char and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        elif ch == "'" and not in_string and (i == 0 or text[i - 1] != "\\"):
            in_char = not in_char

        if ch == "," and not in_string and not in_char:
            parts.append(current.strip())
            current = ""
        else:
            current += ch

    if current.strip():
        parts.append(current.strip())

    return parts


def has_using_namespace_std(code):
    """Return True if using namespace std; exists anywhere before main()."""
    lines = split_code_lines(remove_comments(code))
    for _, line in lines:
        if re.fullmatch(r"(int\s+)?main\s*\(\s*\)\s*\{?", line):
            break
        if re.fullmatch(r"using\s+namespace\s+std\s*;", line):
            return True
    return False


def validate_std_usage(line, using_namespace_std):
    """
    If using namespace std; exists, cout/cin/endl and std::cout/std::cin/std::endl are allowed.
    If it does not exist, cout/cin/endl must be written with std::.
    """
    if using_namespace_std:
        return True, ""

    stripped = line.strip()

    if re.match(r"^cout\b", stripped):
        return False, "cout requires either 'using namespace std;' or 'std::cout'."

    if re.match(r"^cin\b", stripped):
        return False, "cin requires either 'using namespace std;' or 'std::cin'."

    if re.match(r"^std::cout\b", stripped):
        temp = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', stripped)
        temp = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", temp)
        if re.search(r"(?<!std::)\bendl\b", temp):
            return False, "endl requires either 'using namespace std;' or 'std::endl'."

    return True, ""


def extract_cpp_body(code):
    code = remove_comments(code)
    """
    Supported structure:
    #include<iostream>
    optional extra headers like #include <random>
    optional using namespace std;
    int main() or main()
    {
        code here
    }
    """
    lines = split_code_lines(code)
    errors = []

    if not lines:
        return False, [], ["No code found. Please write C++ code first."]

    if len(lines) < 3:
        return False, [], [
            "Incomplete C++ program structure.",
            "Required order: #include<iostream>, optional extra #include lines, optional using namespace std;, main(), {, code, }"
        ]

    first_no, first = lines[0]

    if not re.fullmatch(r"#\s*include\s*<\s*iostream\s*>", first):
        errors.append(f"Line {first_no}: Program must start with #include<iostream>")
        return False, [], errors

    i = 1

    # Allow multiple header files after iostream, e.g. #include <random>
    while i < len(lines) and re.fullmatch(r"#\s*include\s*<\s*[a-zA-Z_][\w.]*\s*>", lines[i][1]):
        i += 1

    # Optional using namespace std;
    if i < len(lines) and re.fullmatch(r"using\s+namespace\s+std\s*;", lines[i][1]):
        i += 1

    if i >= len(lines):
        return False, [], ["Missing main function. Use main() or int main()."]

    main_index = i
    main_no, main_line = lines[main_index]

    main_with_open = re.fullmatch(r"(int\s+)?main\s*\(\s*\)\s*\{", main_line)
    main_only = re.fullmatch(r"(int\s+)?main\s*\(\s*\)", main_line)

    if main_with_open:
        open_index = main_index
        body_start = main_index + 1
    elif main_only:
        if len(lines) <= main_index + 1:
            errors.append(f"Line {main_no}: main() must be followed by opening brace '{{'.")
            return False, [], errors
        brace_no, brace_line = lines[main_index + 1]
        if brace_line != "{":
            errors.append(f"Line {brace_no}: Opening brace '{{' must appear after main().")
            return False, [], errors
        open_index = main_index + 1
        body_start = main_index + 2
    else:
        errors.append(f"Line {main_no}: Missing or invalid main(). Use main() or int main().")
        return False, [], errors

    close_index = None
    brace_balance = 0

    for i in range(open_index, len(lines)):
        line_no, line = lines[i]

        brace_balance += line.count("{")
        brace_balance -= line.count("}")

        if brace_balance == 0 and i > open_index:
            close_index = i
            break

    if close_index is None:
        return False, [], ["Missing closing brace '}' for main function."]

    if close_index != len(lines) - 1:
        extra_no, extra_line = lines[close_index + 1]
        return False, [], [f"Line {extra_no}: No code is allowed after final closing brace -> {extra_line}"]

    body_lines = lines[body_start:close_index]
    return True, body_lines, []


def normalize_expr_for_check(expr):
    expr = expr.strip()
    expr = re.sub(r"\bstd::", "", expr)
    expr = re.sub(r"\b[a-zA-Z_]\w*\s*\([^()]*\)", "0", expr)
    return expr


def is_valid_expression(expr):
    expr = normalize_expr_for_check(expr)
    operand = r"([a-zA-Z_]\w*|\d+\.\d+|\d+|'.'|\"[^\"]*\"|true|false)"
    return re.fullmatch(operand + r"(\s*[+\-*/%]\s*" + operand + r")*", expr.strip()) is not None


def is_standard_declaration(line):
    return re.fullmatch(
        r"^(int|float|double|char|string|bool|long|short)\s+[a-zA-Z_]\w*(\s*=\s*[^,;]+)?(\s*,\s*[a-zA-Z_]\w*(\s*=\s*[^,;]+)?)*\s*;$",
        line
    ) is not None


def is_advanced_declaration(line):
    # Supports simple library/object declarations such as:
    # std::random_device rd;
    # std::mt19937 gen(rd());
    # std::uniform_int_distribution<int> distr(1, 100);
    return re.fullmatch(
        r"^((std::)?[a-zA-Z_]\w*(\s*<\s*[^;<>]+\s*>)?)\s+[a-zA-Z_]\w*\s*(\([^;]*\))?\s*;$",
        line
    ) is not None


def get_advanced_declaration_parts(line):
    match = re.fullmatch(
        r"^((std::)?[a-zA-Z_]\w*(\s*<\s*[^;<>]+\s*>)?)\s+([a-zA-Z_]\w*)\s*(\([^;]*\))?\s*;$",
        line
    )
    if not match:
        return None
    return match.group(1).replace(" ", ""), match.group(4), match.group(5) or "None"

# -------------------- SYNTAX ANALYZER --------------------

def syntax_analyzer(code):
    using_namespace_std = has_using_namespace_std(code)
    status, body_lines, structure_errors = extract_cpp_body(code)

    if not status:
        return False, structure_errors

    errors = []

    for index, line in body_lines:

        if line in {"{", "}"}:
            continue

        declaration_pattern = r"^(int|float|double|char|string|bool|long|short)\s+[a-zA-Z_]\w*(\s*=\s*[^,;]+)?(\s*,\s*[a-zA-Z_]\w*(\s*=\s*[^,;]+)?)*\s*;$"
        assignment_pattern = r"^[a-zA-Z_]\w*\s*=\s*.+\s*;$"
        if_pattern = r"^if\s*\(.+\)\s*\{?$"
        else_pattern = r"^else\s*\{?$"
        for_pattern = r"^for\s*\(.+\)\s*\{?$"
        while_pattern = r"^while\s*\(.+\)\s*\{?$"
        cout_pattern = r"^(std::)?cout\s*(<<\s*.+)+;$"
        cin_pattern = r"^(std::)?cin\s*(>>\s*[a-zA-Z_]\w*\s*)+;$"
        return_pattern = r"^return\s+.+\s*;$"
        increment_pattern = r"^[a-zA-Z_]\w*\s*(\+\+|--)\s*;$"
        function_call_pattern = r"^((std::)?[a-zA-Z_]\w*::)?[a-zA-Z_]\w*\s*\([^;]*\)\s*;$"

        std_ok, std_error = validate_std_usage(line, using_namespace_std)
        if not std_ok:
            errors.append(f"Line {index}: {std_error}")
            continue

        valid = False

        declaration_match = re.fullmatch(declaration_pattern, line)
        if declaration_match:
            datatype = declaration_match.group(1)
            variables_part = line[len(datatype):].strip().rstrip(";").strip()
            valid = True

            for item in split_top_level_commas(variables_part):
                if "=" in item:
                    name, expr = item.split("=", 1)
                    name = name.strip()
                    expr = expr.strip()

                    if not re.fullmatch(r"[a-zA-Z_]\w*", name) or not is_valid_expression(expr):
                        valid = False
                        break
                else:
                    if not re.fullmatch(r"[a-zA-Z_]\w*", item):
                        valid = False
                        break

        elif is_advanced_declaration(line):
            valid = True

        elif re.fullmatch(assignment_pattern, line):
            expr = line.split("=", 1)[1].rstrip(";").strip()
            valid = is_valid_expression(expr) or True  # allow function calls / advanced expressions in mini mode

        elif (
            re.fullmatch(if_pattern, line)
            or re.fullmatch(else_pattern, line)
            or re.fullmatch(for_pattern, line)
            or re.fullmatch(while_pattern, line)
            or re.fullmatch(cout_pattern, line)
            or re.fullmatch(cin_pattern, line)
            or re.fullmatch(return_pattern, line)
            or re.fullmatch(increment_pattern, line)
            or re.fullmatch(function_call_pattern, line)
        ):
            valid = True

        if not valid:
            errors.append(f"Line {index}: Invalid C++ syntax -> {line}")

    if errors:
        return False, errors

    return True, ["Syntax is valid."]

# -------------------- SEMANTIC ANALYZER --------------------

def semantic_analyzer(code):
    using_namespace_std = has_using_namespace_std(code)
    symbol_table.clear()
    errors = []

    status, body_lines, structure_errors = extract_cpp_body(code)
    if not status:
        return False, structure_errors

    block_depth = 0

    for index, line in body_lines:

        if line == "{":
            block_depth += 1
            continue
        if line == "}":
            block_depth = max(0, block_depth - 1)
            continue
        if line.startswith("else"):
            continue

        std_ok, std_error = validate_std_usage(line, using_namespace_std)
        if not std_ok:
            errors.append(f"Line {index}: {std_error}")
            continue

        # for-loop variables are accepted in local scope for this mini compiler.
        for_match = re.fullmatch(r"for\s*\((.*);(.*);(.*)\)\s*\{?", line)
        if for_match:
            init = for_match.group(1).strip()
            decl = re.fullmatch(r"(int|float|double|char|string|bool|long|short)\s+([a-zA-Z_]\w*)\s*=\s*(.+)", init)
            if decl:
                datatype, name, value = decl.group(1), decl.group(2), decl.group(3)
                if not symbol_table.exists(name):
                    symbol_table.add(name, datatype, value, scope="local")
            continue

        declaration_match = re.fullmatch(
            r"(int|float|double|char|string|bool|long|short)\s+(.+)\s*;",
            line
        )

        if declaration_match:
            datatype = declaration_match.group(1)
            variables_part = declaration_match.group(2).strip()

            declarations = split_top_level_commas(variables_part)
            line_valid = True
            pending_adds = []

            for declaration in declarations:
                var_match = re.fullmatch(r"([a-zA-Z_]\w*)\s*(=\s*(.+))?", declaration)

                if not var_match:
                    errors.append(f"Line {index}: Invalid declaration -> {declaration}")
                    line_valid = False
                    continue

                name = var_match.group(1)
                value = var_match.group(3)

                if symbol_table.exists(name) or any(item[0] == name for item in pending_adds):
                    errors.append(f"Line {index}: Variable '{name}' already declared.")
                    line_valid = False
                    continue

                if value is None:
                    pending_adds.append((name, datatype, "None"))
                    continue

                parts = re.findall(r'"[^"]*"|\'.\'|[a-zA-Z_]\w*|\d+\.\d+|\d+|true|false', value)
                expression_valid = True

                for part in parts:
                    if part in KEYWORDS and part not in {"true", "false"}:
                        continue

                    part_type = get_value_type(part)

                    for pending_name, pending_type, pending_value in pending_adds:
                        if part == pending_name:
                            part_type = pending_type

                    if part_type == "unknown":
                        errors.append(f"Line {index}: Variable '{part}' is not declared.")
                        expression_valid = False
                        continue

                    if not check_type_compatibility(datatype, part_type):
                        errors.append(f"Line {index}: Type mismatch in expression for variable '{name}'.")
                        expression_valid = False

                if expression_valid:
                    pending_adds.append((name, datatype, value))
                else:
                    line_valid = False

            if line_valid:
                for name, datatype, value in pending_adds:
                    symbol_table.add(name, datatype, value)

            continue

        advanced = get_advanced_declaration_parts(line)
        if advanced:
            type_, name, value = advanced
            if symbol_table.exists(name):
                errors.append(f"Line {index}: Variable '{name}' already declared.")
            else:
                symbol_table.add(name, type_, value)
            continue

        assignment_match = re.fullmatch(r"([a-zA-Z_]\w*)\s*=\s*(.+)\s*;", line)

        if assignment_match and not line.startswith(tuple(DATATYPES)):
            name = assignment_match.group(1)
            expr = assignment_match.group(2).strip()

            if not symbol_table.exists(name):
                errors.append(f"Line {index}: Variable '{name}' is not declared.")
                continue

            symbol_table.update_value(name, expr)
            continue

        if_match = re.fullmatch(r"if\s*\((.+)\)\s*\{?", line)
        if if_match:
            continue

        if re.fullmatch(r"while\s*\((.+)\)\s*\{?", line):
            continue

        cout_match = re.fullmatch(r"(std::)?cout\s*(<<\s*.+)+;", line)
        if cout_match:
            continue

        cin_match = re.fullmatch(r"(std::)?cin\s*(>>\s*[a-zA-Z_]\w*\s*)+;", line)
        if cin_match:
            names = re.findall(r">>\s*([a-zA-Z_]\w*)", line)
            for name in names:
                if not symbol_table.exists(name):
                    errors.append(f"Line {index}: Variable '{name}' is not declared for cin statement.")
            continue

        if re.fullmatch(r"return\s+.+\s*;", line):
            continue

        if re.fullmatch(r"[a-zA-Z_]\w*\s*(\+\+|--)\s*;", line):
            continue

        if re.fullmatch(r"((std::)?[a-zA-Z_]\w*::)?[a-zA-Z_]\w*\s*\([^;]*\)\s*;", line):
            continue

    if errors:
        return False, errors

    return True, ["Semantic analysis completed successfully."]
