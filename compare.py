"""Compare my assembler with the official one.
1. Run official assembler (nand2tetris tools) on X.asm, save as X_official.hack
2. python compare.py X.asm X_official.hack
"""
import sys, subprocess
asm, official = sys.argv[1], sys.argv[2]
subprocess.run([sys.executable, "assembler.py", asm], check=True)
mine = open(asm[:-4] + ".hack").read().split()
ref = open(official).read().split()
print("MATCH" if mine == ref else "DIFFERENT")
