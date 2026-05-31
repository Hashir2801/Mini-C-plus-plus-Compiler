# Mini C++ Compiler

## Overview

Mini C++ Compiler is a Python Tkinter based educational compiler project
that performs:

-   Lexical Analysis
-   Syntax Analysis
-   Semantic Analysis
-   Symbol Table Generation
-   Dark/Light Theme Switching
-   Undo/Redo Support

This project is designed for Compiler Construction and Programming
Language courses.

------------------------------------------------------------------------

## Features

### Lexical Analysis

-   Identifies keywords
-   Identifies identifiers
-   Identifies operators
-   Identifies separators
-   Identifies literals

### Syntax Analysis

Supports:

``` cpp
#include<iostream>
#include <iostream>

using namespace std;

int main()
{
    // code
}
```

or

``` cpp
#include<iostream>

int main()
{
    std::cout << "Hello";
}
```

### Semantic Analysis

-   Variable declaration checking
-   Redeclaration detection
-   Undeclared variable detection
-   Type compatibility checking

### Symbol Table

Displays:

-   Variable Name
-   Data Type
-   Value
-   Scope
-   Memory Address

------------------------------------------------------------------------

## Supported Statements

### Variable Declarations

``` cpp
int a;
int a = 5;
int a,b,c;
float x = 5.5;
```

### Assignments

``` cpp
a = 10;
b = a + 5;
```

### Input

``` cpp
cin >> a;
std::cin >> a;
```

### Output

``` cpp
cout << a;
cout << "Hello" << endl;

std::cout << a;
std::cout << "Hello" << std::endl;
```

### Return Statement

``` cpp
return 0;
```

### Conditions

``` cpp
if(a > b)
{
}
else
{
}
```

------------------------------------------------------------------------

## Comment Support

Single-line comments are ignored:

``` cpp
// This is a comment

int a = 5; // Inline comment
```

------------------------------------------------------------------------

## Requirements

-   Python 3.10+
-   Tkinter

------------------------------------------------------------------------

## Installation

### Clone Repository

``` bash
git clone <repository-url>
```

### Run Compiler

``` bash
python mini_cpp_compiler_final.py
```

or

``` bash
py mini_cpp_compiler_final.py
```

------------------------------------------------------------------------

## Project Structure

``` text
mini_cpp_compiler_final.py
README.md
```

------------------------------------------------------------------------

## GUI Modules

### Source Code Panel

Used to write C++ code.

### Tokens Tab

Displays lexical tokens.

### Compiler Output Tab

Displays syntax and semantic results.

### Symbol Table Tab

Displays generated symbol table.

------------------------------------------------------------------------

## Sample Program

``` cpp
#include<iostream>
using namespace std;

int main()
{
    int num1, num2;

    cin >> num1;
    cin >> num2;

    cout << num1 + num2 << endl;

    return 0;
}
```

------------------------------------------------------------------------

## Author

BS Computer Science Project Mini C++ Compiler using Python and Tkinter
