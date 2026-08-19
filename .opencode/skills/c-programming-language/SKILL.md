---
name: c-programming-language
description: Applies Kernighan & Ritchie's The C Programming Language to write clear, portable C: types and operators, control flow, functions and the argument-passing model, pointers and arrays, structures, input and output, the standard library, and the UNIX system interface. Use when the user says 'learn C', 'K&R', 'C programming', 'pointers in C', 'structures C', 'standard library', 'write portable C', 'C idioms', 'getchar putchar', or when writing C that is correct, small, and readable.
---

# The C Programming Language (Kernighan & Ritchie)

K&R is the original and still the clearest statement of the C language. This skill applies its style: compact, precise, and portable.

## Language core

- C has a small core: data types, operators, expressions, statements, functions, pointers, structures, and I/O. Master each precisely.
- Types and their sizes vary by implementation; use the declared size guarantees and the standard library's fixed-size types.
- Every object has a type and a value; keep them consistent to avoid the classic casts-as-cure-alls.

## Pointers and arrays

- Pointers hold addresses and are typed; pointer arithmetic is scaled by the pointed-to type.
- Strings are null-terminated arrays of char; the standard functions assume that convention.
- Passing an array to a function passes a pointer to its first element; sizes travel separately.

## Functions and structures

- Functions pass arguments by value; passing a pointer lets a function modify the caller's object.
- Structures group related data and can be assigned and passed; pointers to structures are the efficient path for large ones.
- Use enums and typedefs to give meaning to integer constants.

## The UNIX interface

- File I/O goes through descriptors with open, read, write, and close; the standard library adds buffered streams.
- Command-line arguments arrive in argv; the environment is a separate array.
- Prefer the standard library's portable functions; reach for the system calls only when the library lacks a guarantee.

## Pairs with
apue-unix-programming, expert-c-programming, computer-systems-programmers-perspective, dragon-book-compilers, code-execution-guided-swemaster
