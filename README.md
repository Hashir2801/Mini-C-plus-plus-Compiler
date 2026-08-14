# Mini C++ Compiler

A web-based educational Mini C++ Compiler that performs lexical, syntax, and semantic analysis for a supported subset of C++.

## Features

- Lexical Analysis
- Syntax Analysis
- Semantic Analysis
- Symbol Table Generation
- Token table with lexeme and token type
- Syntax and semantic error reporting
- Variable declaration and redeclaration checking
- Undeclared variable detection
- Basic type compatibility checks
- `std::cout`, `std::cin`, and `using namespace std;` validation
- Support for common declarations, assignments, loops, conditions, input/output, and return statements
- Responsive Flask-based web interface
- Ready for Vercel deployment

## Project Structure

```text
app.py
compiler_core.py
requirements.txt
README.md
```

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Vercel Deployment

Keep `app.py` and `compiler_core.py` in the repository root together with `requirements.txt`.

Push the project to GitHub and import the repository into Vercel. A separate `vercel.json` is not required for a root-level Flask app.

## Important Note

This is an educational mini compiler. It analyzes the C++ subset implemented in the project and does not generate machine code or replace a production C++ compiler such as GCC or Clang.

## Original Project

The original desktop application used Python Tkinter with:

- source-code editor
- token table
- compiler output
- symbol-table tab
- dark/light theme toggle

The Vercel version replaces the Tkinter desktop interface with a browser-based Flask interface while preserving the compiler-analysis logic.
