
import re
import tkinter as tk
from tkinter import ttk, messagebox

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
    "true", "false", "include", "using", "namespace", "std", "main"
}

DATATYPES = {"int", "float", "double", "char", "string", "bool", "long", "short"}

OPERATORS = {
    "+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">=",
    "++", "--", "+=", "-=", "*=", "/=", "<<", ">>"
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
    tokens = []

    raw_tokens = re.findall(
        r'"[^"]*"|\'.\'|[a-zA-Z_]\w*|\d+\.\d+|\d+|==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|<<|>>|[+\-*/%=<>;(),{}\[\]]|\S',
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


# -------------------- SYNTAX ANALYZER --------------------

def syntax_analyzer(code):
    errors = []
    lines = remove_empty_lines(code.split("\n"))

    if len(lines) == 0:
        return False, ["No code found. Please write C++ code first."]

    for index, line in enumerate(lines, start=1):

        if line in {"{", "}"} or re.fullmatch(r"main\s*\(\s*\)\s*\{", line):
            continue

        declaration_pattern = r"^(int|float|double|char|string|bool|long|short)\s+[a-zA-Z_]\w*\s*(=\s*([a-zA-Z_]\w*|\d+|\d+\.\d+|'.'|\"[^\"]*\"|true|false)(\s*[+\-*/%]\s*([a-zA-Z_]\w*|\d+|\d+\.\d+))*)?\s*;$"

        assignment_pattern = r"^[a-zA-Z_]\w*\s*=\s*([a-zA-Z_]\w*|\d+|\d+\.\d+|'.'|\"[^\"]*\"|true|false)(\s*[+\-*/%]\s*([a-zA-Z_]\w*|\d+|\d+\.\d+|'.'|\"[^\"]*\"|true|false))*\s*;$"

        if_pattern = r"^if\s*\(\s*([a-zA-Z_]\w*|\d+|\d+\.\d+)\s*(==|!=|<=|>=|<|>)\s*([a-zA-Z_]\w*|\d+|\d+\.\d+)\s*\)$"

        else_pattern = r"^else$"

        cout_pattern = r"^(cout|print)\s*<<\s*([a-zA-Z_]\w*|\"[^\"]*\"|\d+|\d+\.\d+)\s*;$"

        cin_pattern = r"^cin\s*>>\s*[a-zA-Z_]\w*\s*;$"

        valid = (
            re.fullmatch(declaration_pattern, line)
            or re.fullmatch(assignment_pattern, line)
            or re.fullmatch(if_pattern, line)
            or re.fullmatch(else_pattern, line)
            or re.fullmatch(cout_pattern, line)
            or re.fullmatch(cin_pattern, line)
        )

        if not valid:
            errors.append(f"Line {index}: Invalid C++ syntax -> {line}")

    if errors:
        return False, errors

    return True, ["Syntax is valid."]


# -------------------- SEMANTIC ANALYZER --------------------

def semantic_analyzer(code):
    symbol_table.clear()
    errors = []
    lines = remove_empty_lines(code.split("\n"))

    for index, line in enumerate(lines, start=1):

        if line in {"{", "}"} or re.fullmatch(r"main\s*\(\s*\)\s*\{", line):
            continue

        declaration_match = re.fullmatch(
            r"(int|float|double|char|string|bool|long|short)\s+([a-zA-Z_]\w*)\s*(=\s*(.+))?\s*;",
            line
        )

        if declaration_match:
            datatype = declaration_match.group(1)
            name = declaration_match.group(2)
            value = declaration_match.group(4)

            if symbol_table.exists(name):
                errors.append(f"Line {index}: Variable '{name}' already declared.")
                continue

            if value is None:
                symbol_table.add(name, datatype, "None")
                continue

            parts = re.findall(r'"[^"]*"|\'.\'|[a-zA-Z_]\w*|\d+\.\d+|\d+', value)

            expression_valid = True

            for part in parts:
                if part in KEYWORDS and part not in {"true", "false"}:
                    continue

                part_type = get_value_type(part)

                if part_type == "unknown":
                    errors.append(f"Line {index}: Variable '{part}' is not declared.")
                    expression_valid = False
                    continue

                if not check_type_compatibility(datatype, part_type):
                    errors.append(f"Line {index}: Type mismatch in expression for variable '{name}'.")
                    expression_valid = False

            if expression_valid:
                symbol_table.add(name, datatype, value)

            continue

        assignment_match = re.fullmatch(
            r"([a-zA-Z_]\w*)\s*=\s*(.+)\s*;",
            line
        )

        if assignment_match and not line.startswith(tuple(DATATYPES)):
            name = assignment_match.group(1)
            expr = assignment_match.group(2).strip()

            if not symbol_table.exists(name):
                errors.append(f"Line {index}: Variable '{name}' is not declared.")
                continue

            left_type = symbol_table.get(name)["Type"]
            parts = re.findall(r'"[^"]*"|\'.\'|[a-zA-Z_]\w*|\d+\.\d+|\d+', expr)

            for part in parts:
                if part in KEYWORDS and part not in {"true", "false"}:
                    continue

                part_type = get_value_type(part)

                if part_type == "unknown":
                    errors.append(f"Line {index}: Variable '{part}' is not declared.")
                    continue

                if not check_type_compatibility(left_type, part_type):
                    errors.append(f"Line {index}: Type mismatch. Cannot assign {part_type} expression to {left_type} variable '{name}'.")

            if len(errors) == 0:
                symbol_table.update_value(name, expr)

            continue

        if_match = re.fullmatch(
            r"if\s*\(\s*([a-zA-Z_]\w*|\d+|\d+\.\d+)\s*(==|!=|<=|>=|<|>)\s*([a-zA-Z_]\w*|\d+|\d+\.\d+)\s*\)",
            line
        )

        if if_match:
            left = if_match.group(1)
            right = if_match.group(3)

            for item in [left, right]:
                if re.fullmatch(r"[a-zA-Z_]\w*", item):
                    if not symbol_table.exists(item):
                        errors.append(f"Line {index}: Variable '{item}' is not declared in condition.")

            continue

        cout_match = re.fullmatch(r"(cout|print)\s*<<\s*([a-zA-Z_]\w*|\"[^\"]*\"|\d+|\d+\.\d+)\s*;", line)

        if cout_match:
            value = cout_match.group(1)

            if re.fullmatch(r"[a-zA-Z_]\w*", value) and value not in {"cout", "print"}:
                if not symbol_table.exists(value):
                    errors.append(f"Line {index}: Variable '{value}' is not declared for cout statement.")

            continue

        cin_match = re.fullmatch(r"cin\s*>>\s*([a-zA-Z_]\w*)\s*;", line)

        if cin_match:
            name = cin_match.group(1)

            if not symbol_table.exists(name):
                errors.append(f"Line {index}: Variable '{name}' is not declared for cin statement.")

            continue

    if errors:
        return False, errors

    return True, ["Semantic analysis completed successfully."]


# -------------------- GUI APPLICATION --------------------

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini C++ Compiler")
        self.root.geometry("1250x760")
        self.root.minsize(1100, 700)

        self.current_theme = "dark"
        self.setup_colors()
        self.setup_style()
        self.create_layout()
        self.apply_theme()

    def setup_colors(self):
        self.themes = {
            "dark": {
                "root": "#0f172a",
                "header": "#111827",
                "card": "#1e293b",
                "input": "#020617",
                "text": "#f8fafc",
                "muted": "#94a3b8",
                "output_text": "#e5e7eb",
                "tree_bg": "#111827",
                "tree_head": "#1e293b",
                "accent": "#38bdf8",
                "toggle_bg": "#f8fafc",
                "toggle_fg": "#111827"
            },
            "light": {
                "root": "#e5e7eb",
                "header": "#ffffff",
                "card": "#f8fafc",
                "input": "#ffffff",
                "text": "#111827",
                "muted": "#475569",
                "output_text": "#111827",
                "tree_bg": "#ffffff",
                "tree_head": "#dbeafe",
                "accent": "#2563eb",
                "toggle_bg": "#111827",
                "toggle_fg": "#ffffff"
            }
        }

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def refresh_tree_style(self):
        colors = self.themes[self.current_theme]

        self.style.configure(
            "Treeview",
            background=colors["tree_bg"],
            foreground=colors["output_text"],
            rowheight=28,
            fieldbackground=colors["tree_bg"],
            bordercolor="#334155",
            borderwidth=1
        )

        self.style.configure(
            "Treeview.Heading",
            background=colors["tree_head"],
            foreground=colors["text"],
            font=("Segoe UI", 10, "bold")
        )

        self.style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

        self.style.configure("TNotebook", background=colors["root"], borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=colors["tree_head"],
            foreground=colors["text"],
            padding=[12, 7],
            font=("Segoe UI", 9, "bold")
        )
        self.style.map("TNotebook.Tab", background=[("selected", colors["input"])])

    def create_layout(self):
        self.header = tk.Frame(self.root, height=70)
        self.header.pack(fill="x")

        self.title = tk.Label(
            self.header,
            text="Mini C++ Compiler",
            font=("Segoe UI", 24, "bold")
        )
        self.title.pack(side="left", padx=25, pady=15)

        self.subtitle = tk.Label(
            self.header,
            text="Lexical Analysis  |  Syntax Analysis  |  Semantic Analysis  |  Symbol Table",
            font=("Segoe UI", 11)
        )
        self.subtitle.pack(side="left", padx=15, pady=25)

        self.theme_btn = tk.Button(
            self.header,
            text="Switch to Light Theme",
            command=self.toggle_theme,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8
        )
        self.theme_btn.pack(side="right", padx=25, pady=17)

        self.main = tk.Frame(self.root)
        self.main.pack(fill="both", expand=True, padx=20, pady=20)

        self.left = tk.Frame(self.main, bd=0)
        self.left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.right = tk.Frame(self.main)
        self.right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        self.code_label = tk.Label(
            self.left,
            text="Source Code",
            font=("Segoe UI", 15, "bold")
        )
        self.code_label.pack(anchor="w", padx=18, pady=(15, 5))

        self.code_input = tk.Text(
            self.left,
            insertbackground="#ffffff",
            font=("Consolas", 13),
            relief="flat",
            wrap="none",
            height=22,
            undo=True,
            maxundo=-1
        )
        self.code_input.pack(fill="both", expand=True, padx=18, pady=10)

        # Undo / Redo Shortcuts
        self.code_input.bind("<Control-z>", self.undo_action)
        self.code_input.bind("<Control-y>", self.redo_action)

        self.button_frame = tk.Frame(self.left)
        self.button_frame.pack(fill="x", padx=18, pady=(5, 18))

        self.btn_lexical = self.make_button(self.button_frame, "Lexical Analysis", self.run_lexical, "#2563eb")
        self.btn_syntax = self.make_button(self.button_frame, "Syntax Analysis", self.run_syntax, "#7c3aed")
        self.btn_semantic = self.make_button(self.button_frame, "Semantic Analysis", self.run_semantic, "#0891b2")
        self.btn_full = self.make_button(self.button_frame, "Run Full Compiler", self.run_full, "#16a34a")
        self.btn_clear_output = self.make_button(self.button_frame, "Clear Output", self.clear_output, "#ea580c")
        self.btn_clear_code = self.make_button(self.button_frame, "Clear Code", self.clear_code, "#dc2626")

        self.btn_lexical.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.btn_syntax.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.btn_semantic.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.btn_full.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.btn_clear_output.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.btn_clear_code.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        for i in range(3):
            self.button_frame.columnconfigure(i, weight=1)

        self.tabs = ttk.Notebook(self.right)
        self.tabs.pack(fill="both", expand=True)

        self.token_frame = tk.Frame(self.tabs)
        self.output_frame = tk.Frame(self.tabs)
        self.symbol_frame = tk.Frame(self.tabs)

        self.tabs.add(self.token_frame, text="Tokens")
        self.tabs.add(self.output_frame, text="Compiler Output")
        self.tabs.add(self.symbol_frame, text="Symbol Table")

        self.create_token_table()
        self.create_output_box()
        self.create_symbol_table()

    def make_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=10
        )

    def create_token_table(self):
        self.token_count_label = tk.Label(
            self.token_frame,
            text="Total Tokens: 0",
            font=("Segoe UI", 13, "bold")
        )
        self.token_count_label.pack(anchor="w", padx=15, pady=(12, 0))

        self.token_tree = ttk.Treeview(
            self.token_frame,
            columns=("Lexeme", "Token Type"),
            show="headings"
        )
        self.token_tree.heading("Lexeme", text="Lexeme")
        self.token_tree.heading("Token Type", text="Token Type")
        self.token_tree.column("Lexeme", width=180)
        self.token_tree.column("Token Type", width=180)
        self.token_tree.pack(fill="both", expand=True, padx=15, pady=15)

    def create_output_box(self):
        self.output_box = tk.Text(
            self.output_frame,
            insertbackground="#ffffff",
            font=("Consolas", 12),
            relief="flat",
            wrap="word"
        )
        self.output_box.pack(fill="both", expand=True, padx=15, pady=15)

    def create_symbol_table(self):
        self.symbol_tree = ttk.Treeview(
            self.symbol_frame,
            columns=("Name", "Type", "Value", "Scope", "Memory"),
            show="headings"
        )

        self.symbol_tree.heading("Name", text="Name", anchor="center")
        self.symbol_tree.heading("Type", text="Type", anchor="center")
        self.symbol_tree.heading("Value", text="Value", anchor="center")
        self.symbol_tree.heading("Scope", text="Scope", anchor="center")
        self.symbol_tree.heading("Memory", text="Memory", anchor="center")

        self.symbol_tree.column("Name", width=130, minwidth=100, anchor="center", stretch=True)
        self.symbol_tree.column("Type", width=130, minwidth=100, anchor="center", stretch=True)
        self.symbol_tree.column("Value", width=170, minwidth=120, anchor="center", stretch=True)
        self.symbol_tree.column("Scope", width=130, minwidth=100, anchor="center", stretch=True)
        self.symbol_tree.column("Memory", width=130, minwidth=100, anchor="center", stretch=True)

        self.symbol_tree.pack(fill="both", expand=True, padx=15, pady=15)

    def apply_theme(self):
        colors = self.themes[self.current_theme]
        self.refresh_tree_style()

        self.root.configure(bg=colors["root"])
        self.header.configure(bg=colors["header"])
        self.main.configure(bg=colors["root"])
        self.left.configure(bg=colors["card"])
        self.right.configure(bg=colors["root"])
        self.button_frame.configure(bg=colors["card"])

        self.title.configure(bg=colors["header"], fg=colors["text"])
        self.subtitle.configure(bg=colors["header"], fg=colors["muted"])
        self.code_label.configure(bg=colors["card"], fg=colors["text"])

        self.theme_btn.configure(
            bg=colors["toggle_bg"],
            fg=colors["toggle_fg"],
            activebackground=colors["toggle_bg"],
            activeforeground=colors["toggle_fg"]
        )

        self.code_input.configure(
            bg=colors["input"],
            fg=colors["output_text"],
            insertbackground=colors["output_text"]
        )

        self.output_box.configure(
            bg=colors["input"],
            fg=colors["output_text"],
            insertbackground=colors["output_text"]
        )

        for frame in [self.token_frame, self.output_frame, self.symbol_frame]:
            frame.configure(bg=colors["tree_bg"])

        self.token_count_label.configure(
            bg=colors["tree_bg"],
            fg=colors["accent"]
        )

        if self.current_theme == "dark":
            self.theme_btn.configure(text="Switch to Light Theme")
        else:
            self.theme_btn.configure(text="Switch to Dark Theme")

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"

        self.apply_theme()

    def undo_action(self, event=None):
        try:
            self.code_input.edit_undo()
        except:
            pass

    def redo_action(self, event=None):
        try:
            self.code_input.edit_redo()
        except:
            pass

    def get_code(self):
        return self.code_input.get("1.0", tk.END).strip()

    def clear_token_table(self):
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)

    def clear_symbol_table_gui(self):
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)

    def clear_output(self):
        self.output_box.delete("1.0", tk.END)
        self.clear_token_table()
        self.clear_symbol_table_gui()
        self.token_count_label.config(text="Total Tokens: 0")

    def clear_code(self):
        self.code_input.delete("1.0", tk.END)
        self.clear_output()

    def write_output(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)

    def show_symbols(self):
        self.clear_symbol_table_gui()
        for item in symbol_table.table:
            self.symbol_tree.insert(
                "",
                tk.END,
                values=(
                    item["Name"],
                    item["Type"],
                    item["Value"],
                    item["Scope"],
                    item["Memory"]
                )
            )

    def run_lexical(self):
        self.clear_token_table()
        code = self.get_code()

        if not code:
            messagebox.showwarning("Warning", "Please enter C++ source code.")
            return

        tokens = lexical_analyzer(code)

        for lexeme, token_type in tokens:
            self.token_tree.insert("", tk.END, values=(lexeme, token_type))

        self.token_count_label.config(text=f"Total Tokens: {len(tokens)}")
        self.tabs.select(self.token_frame)

    def run_syntax(self):
        code = self.get_code()
        self.output_box.delete("1.0", tk.END)

        status, result = syntax_analyzer(code)

        self.write_output("SYNTAX ANALYSIS RESULT")
        self.write_output("-" * 45)

        for line in result:
            self.write_output(line)

        if status:
            self.write_output("\nStatus: Valid Syntax")
        else:
            self.write_output("\nStatus: Invalid Syntax")

        self.tabs.select(self.output_frame)

    def run_semantic(self):
        code = self.get_code()
        self.output_box.delete("1.0", tk.END)

        syntax_status, syntax_result = syntax_analyzer(code)

        if not syntax_status:
            self.write_output("Semantic analysis cannot run because syntax has errors.\n")
            for line in syntax_result:
                self.write_output(line)
            self.tabs.select(self.output_frame)
            return

        status, result = semantic_analyzer(code)

        self.write_output("SEMANTIC ANALYSIS RESULT")
        self.write_output("-" * 45)

        for line in result:
            self.write_output(line)

        if status:
            self.write_output("\nStatus: Semantic Correct")
        else:
            self.write_output("\nStatus: Semantic Error")

        self.show_symbols()
        self.tabs.select(self.output_frame)

    def run_full(self):
        self.clear_output()
        code = self.get_code()

        if not code:
            messagebox.showwarning("Warning", "Please enter C++ source code.")
            return

        tokens = lexical_analyzer(code)
        for lexeme, token_type in tokens:
            self.token_tree.insert("", tk.END, values=(lexeme, token_type))

        self.token_count_label.config(text=f"Total Tokens: {len(tokens)}")

        self.write_output("MINI C++ COMPILER OUTPUT")
        self.write_output("=" * 50)

        self.write_output("\n1. LEXICAL ANALYSIS")
        self.write_output("-" * 30)
        self.write_output("Tokens generated successfully.")

        self.write_output("\n2. SYNTAX ANALYSIS")
        self.write_output("-" * 30)

        syntax_status, syntax_result = syntax_analyzer(code)

        for line in syntax_result:
            self.write_output(line)

        if not syntax_status:
            self.write_output("\nCompilation stopped due to syntax errors.")
            self.tabs.select(self.output_frame)
            return

        self.write_output("\n3. SEMANTIC ANALYSIS")
        self.write_output("-" * 30)

        semantic_status, semantic_result = semantic_analyzer(code)

        for line in semantic_result:
            self.write_output(line)

        if semantic_status:
            self.write_output("\nFinal Result: Code compiled successfully.")
        else:
            self.write_output("\nFinal Result: Code has semantic errors.")

        self.show_symbols()
        self.tabs.select(self.output_frame)


# -------------------- MAIN --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()
