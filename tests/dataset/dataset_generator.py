# -*- coding: utf-8 -*-

import random

if __name__ == "__main__":

    dataset_size = 50

    for seed in range(dataset_size):
        print(f"generate seed {seed}")
        n = 100
        table = [[0 for i in range(n)] for j in range(n)]
        random.seed(seed)

        for m in range(1000):
            x = random.randint(0, n - 1)
            y = random.randint(0, n - 1)
            h = random.randint(1, n)

            for i in range(n):
                for j in range(n):
                    distance = abs(y - i) + abs(x - j)
                    height = max(h - distance, 0)
                    table[i][j] += height

        with open(f"{seed:02}.txt", 'w') as fout:
            for i in range(n):
                fout.write(" ".join(list(map(str, table[i]))) + "\n")
