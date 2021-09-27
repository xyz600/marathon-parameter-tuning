# -*- coding: utf-8 -*-

if __name__ == "__main__":

    n = 100
    with open("out_0.txt") as fin:
        for idx, line in enumerate(fin.readlines()[1:]):
            x, y, h = map(int, line.strip().split(" "))
            print(f"line: {idx}")

            assert(0 <= x < n)
            assert(0 <= y < n)
            assert(0 < h <= n)
