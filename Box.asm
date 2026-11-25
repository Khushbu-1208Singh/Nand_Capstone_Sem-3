// Box.asm  --  K = 61
// While any key is pressed, draw a black box:
//   starts at row 61, 20 rows tall, 32 pixels wide (2 words) at the left edge.
// Row r starts at SCREEN + 32*r  ->  16384 + 32*61 = 18336
// When no key is pressed the same area is painted white (box disappears).

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE           // key pressed -> black
    @color
    M=0             // no key -> white
    @DRAW
    0;JMP
(BLACK)
    @color
    M=-1            // all 16 bits set = black
(DRAW)
    @18336          // first word of row 61
    D=A
    @addr
    M=D
    @20             // 20 rows
    D=A
    @rows
    M=D
(ROW)
    @color
    D=M
    @addr
    A=M
    M=D             // left word  (pixels 0-15)
    A=A+1
    M=D             // right word (pixels 16-31)
    @32             // move down one row (32 words)
    D=A
    @addr
    M=D+M
    @rows
    M=M-1
    D=M
    @ROW
    D;JGT           // more rows left?
    @LOOP
    0;JMP
