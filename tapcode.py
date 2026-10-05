#!/usr/bin/env python3
"""tapcode - 敲击码(波利比乌斯方阵)编解码器。

5x5 方阵, I/J 合并为一格(国际通用约定):

      1   2   3   4   5
    +---+---+---+---+---+
  1 | A | B | C | D | E |
    +---+---+---+---+---+
  2 | F | G | H | I/J | K |
    +---+---+---+---+---+
  3 | L | M | N | O | P |
    +---+---+---+---+---+
  4 | Q | R | S | T | U |
    +---+---+---+---+---+
  5 | V | W | X | Y | Z |
    +---+---+---+---+---+

编码规则: 先敲行数, 空格, 再敲列数, 用 . 表示每次敲击。
例: SOS -> ".... ... ... .... .... ..."
"""

import argparse
import sys

ROWS = [
    "ABCDE",
    "FGHIK",   # I/J 共用 (2,4), K 单独占 (2,5)
    "LMNOP",
    "QRSTU",
    "VWXYZ",
]

# 字母 -> (行, 列), 均为 1-based
ENCODE = {}
for r, row in enumerate(ROWS, start=1):
    for c, ch in enumerate(row, start=1):
        ENCODE[ch] = (r, c)
ENCODE["J"] = ENCODE["I"]  # J 与 I 同格

# (行, 列) -> 字母, (2,4) 显示为 I/J
DECODE = {}
for ch, (r, c) in ENCODE.items():
    if (r, c) not in DECODE:
        DECODE[(r, c)] = ch
DECODE[(2, 4)] = "I/J"


def encode(text):
    """编码为敲击点串。空格分隔字母, 双空格分隔单词。"""
    if not text or not text.strip():
        raise ValueError("输入为空")
    out = []
    for word in text.upper().split():
        letters = []
        for ch in word:
            if ch not in ENCODE:
                raise ValueError("不支持的字符: %r(仅支持 A-Z)" % ch)
            r, c = ENCODE[ch]
            letters.append("." * r + " " + "." * c)
        out.append("  ".join(letters))
    return "   ".join(out)


def decode(text):
    """解码敲击点串。"""
    if not text.strip():
        raise ValueError("输入为空")
    words = []
    for word in text.strip().split("   "):
        letters = []
        for token in word.split("  "):
            parts = token.split(" ")
            if len(parts) != 2 or not all(set(p) <= {"."} and p for p in parts):
                raise ValueError("非法敲击串: %r" % token)
            r, c = len(parts[0]), len(parts[1])
            if not (1 <= r <= 5 and 1 <= c <= 5):
                raise ValueError("行列超出 1-5: %r" % token)
            letters.append(DECODE[(r, c)])
        words.append("".join(letters))
    return " ".join(words)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="敲击码(Tap Code)编解码: 5x5 方阵, 行敲+列敲")
    ap.add_argument("text", nargs="?", help="要编码/解码的文本(缺省读 stdin)")
    ap.add_argument("--decode", "-d", action="store_true", help="解码模式")
    args = ap.parse_args(argv)

    text = args.text
    if text is None:
        if sys.stdin.isatty():
            print("error: 请提供文本或用管道输入", file=sys.stderr)
            return 2
        text = sys.stdin.read().strip()

    try:
        print(decode(text) if args.decode else encode(text))
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
