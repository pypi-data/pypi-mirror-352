# Orlang

A simple, expressive programming language that transpiles to Python. Orlang is inspired by the Afaan Oromo language, using its syntax and keywords to create a unique and culturally relevant programming experience.

## Features

- Clean, Afaan Oromo-inspired syntax
- Support for basic data types (integers, strings, booleans)
- Variable declarations and assignments
- Control flow statements (if/else, while loops, for loops)
- Transpiles to readable Python code

## Installation

### Using pip

```bash
pip install orlang
```

### From Source

#### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (optional)

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/firo1919/orlang.git
cd orlang
```

2. Install the package in development mode:
```bash
# Using pip
pip install -e .

# Or using uv
uv pip install -e .
```

This will install the `orlang` command-line tool globally.

## Usage

### Command Line

Run an Orlang file:
```bash
orlang path/to/your/file.orl
```

### Example Code

```orlang
// Variable declaration
bakka count = 0;

// While loop
yeroo (count < 5) {
    barreessi count;
    count = count + 1;
}

// For loop
hama (bakka i = 0; i < 5; i = i + 1) {
    barreessi i;
}
```

## Language Specification

### Afaan Oromo Keywords

Orlang uses Afaan Oromo words as keywords to make programming more accessible and culturally relevant:

- `bakka` - Variable declaration (meaning "place" or "location")
- `barreessi` - Print statement (meaning "write")
- `yoo` - If statement (meaning "if")
- `kanbiroo` - Else statement (meaning "otherwise")
- `yeroo` - While loop (meaning "time" or "when")
- `hama` - For loop (meaning "until")
- `dhugaa` - True (meaning "true")
- `soba` - False (meaning "false")
- `duwwaa` - Null (meaning "empty")

### Variables

Variables must be declared using the `bakka` keyword:
```orlang
bakka name = "value";
```

### Control Flow

#### If Statements
```orlang
yoo (condition) {
    // code
} kanbiroo {
    // code
}
```

#### While Loops
```orlang
yeroo (condition) {
    // code
}
```

#### For Loops
```orlang
hama (bakka i = 0; i < limit; i = i + 1) {
    // code
}
```

### Operators

#### Arithmetic
- `+` - Addition
- `-` - Subtraction
- `*` - Multiplication
- `/` - Division

#### Comparison
- `==` - Equal to
- `!=` - Not equal to
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal to
- `<=` - Less than or equal to

#### Logical
- `fi` - Logical AND (meaning "and")
- `ykn` - Logical OR (meaning "or")

## License

This project is licensed under the MIT License - see the LICENSE file for details.
