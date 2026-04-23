# Hava Programming Language

Hava is a simple interpreted programming language written in Python.  
The goal of this project is to explore how programming languages are designed and executed, while providing a clean and intuitive syntax in Turkish.

## Motivation

I built Hava to understand how programming languages work internally — not just how to use them.  
This project focuses on concepts like parsing, execution flow, and language design.

## Technical Overview

Hava consists of three main components:

- **Lexer**: Tokenizes input using defined language rules  
- **Parser**: Builds structured instructions based on grammar  
- **Interpreter**: Executes instructions using a custom runtime environment  

The interpreter evaluates code dynamically by walking through the parsed structure and executing operations step by step.

## Features

- Simple and readable syntax (Turkish-based)
- Variables and assignments
- Arithmetic operations (+, -, *, /)
- Conditional statements (if / else)
- Loops
- Function definitions and calls
- Interpreter-based execution

## Example Code

```hava
Hava > fonksiyon test1():: hava_isim = "hava" :
Hava > test1():
Hava > yaz(hava_isim):
```

**Output:**
```
hava
```

## Running the Project

Run the interpreter with:

```bash
python run-interpreter.py
```

Then write your code in the interactive console.

## Notes

- This project is in beta and still under development  
- Currently interpreter-based (no compiler yet)  
- Designed as a learning-focused project  

## Learning Outcome

Through this project, I gained hands-on experience with:

- how interpreters execute code  
- structuring a custom programming language  
- designing syntax and execution logic  

This project reflects my interest in understanding programming beyond surface-level coding.
