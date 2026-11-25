#!/usr/bin/env python3
"""Hack assembler (Nand to Tetris, Project 6).  K = 61  ->  K mod 3 = 1
Extra feature: a wrong line prints a clear message with its line number
(e.g. "Line 7: invalid instruction") instead of crashing.

Usage: python assembler.py Prog.asm      -> writes Prog.hack
"""
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
def dest_bits(d):
    """d1=A, d2=D, d3=M. Letters may be in any order (e.g. DM or MD)."""
    if len(set(d)) != len(d) or any(c not in "ADM" for c in d):
        return None
    return ("1" if "A" in d else "0") + ("1" if "D" in d else "0") + ("1" if "M" in d else "0")
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
SYMBOLS.update({f"R{i}": i for i in range(16)})


def valid_symbol(s):
    if not s or s[0].isdigit():
        return False
    return all(c.isalnum() or c in "_.$:" for c in s)


def clean(line):
    """Remove comment and all whitespace."""
    return "".join(line.split("//")[0].split())


def assemble(lines):
    errors = []
    symbols = dict(SYMBOLS)

    # ---------- First pass: labels ----------
    code = []                      # (line_number, text)
    pc = 0
    for n, raw in enumerate(lines, 1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith("("):
            if not text.endswith(")") or text.count("(") != 1 or text.count(")") != 1:
                errors.append(f"Line {n}: invalid label '{text}' (missing ')')")
                continue
            name = text[1:-1]
            if not valid_symbol(name):
                errors.append(f"Line {n}: invalid label name '{name}'")
            elif name in symbols:
                errors.append(f"Line {n}: label '{name}' already defined")
            else:
                symbols[name] = pc
            continue
        code.append((n, text))
        pc += 1

    # ---------- Second pass: translate ----------
    next_var = 16
    out = []
    for n, text in code:
        if text[0] == "@":
            sym = text[1:]
            if not sym:
                errors.append(f"Line {n}: invalid instruction '@' has no address")
                continue
            if sym.isdigit():
                val = int(sym)
                if val > 32767:
                    errors.append(f"Line {n}: address {val} is too large (max 32767)")
                    continue
            elif valid_symbol(sym):
                if sym not in symbols:
                    symbols[sym] = next_var
                    next_var += 1
                val = symbols[sym]
            else:
                errors.append(f"Line {n}: invalid instruction '{text}' (bad symbol)")
                continue
            out.append(format(val, "016b"))
        else:
            dest, comp, jump = "", text, ""
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)
            dbits = dest_bits(dest)
            if dbits is None:
                errors.append(f"Line {n}: invalid destination '{dest}' in '{text}'")
            elif comp not in COMP:
                errors.append(f"Line {n}: invalid instruction '{text}' (unknown computation '{comp}')")
            elif jump not in JUMP:
                errors.append(f"Line {n}: invalid jump '{jump}' in '{text}'")
            else:
                out.append("111" + COMP[comp] + dbits + JUMP[jump])
    return out, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"Cannot open file: {e}")
        sys.exit(1)

    out, errors = assemble(lines)
    if errors:
        for e in errors:
            print(e)
        print(f"Assembly failed: {len(errors)} error(s). No .hack file written.")
        sys.exit(1)

    hack = path[:-4] + ".hack"
    with open(hack, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"Wrote {hack} ({len(out)} instructions)")


if __name__ == "__main__":
    main()
