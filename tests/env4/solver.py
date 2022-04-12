import sys

from typing import List, Tuple
import time
import random
import math
import copy

"""
SA for example problem:
https://atcoder.jp/contests/future-contest-2018-qual/tasks/future_contest_2018_qual_a
"""


class Mountain:

    def __init__(self, y: int, x: int, height: int):
        self.y: int = y
        self.x: int = x
        self.height: int = height


class Board:
    def __init__(self, table: List[List[int]]):
        self.table = table


class Config:

    def __init__(self, inverse_temperature: float, neighbor_select_rate: float, max_init_height_rate: float, max_diff_rate: float):
        self.inverse_temperature: float = inverse_temperature
        self.neighbor_select_rate: float = neighbor_select_rate
        self.max_init_height_rate: float = max_init_height_rate
        self.max_diff_rate: float = max_diff_rate


def solve(problem: Board, start_time: float, config: Config) -> Tuple[float, List[Mountain]]:

    n = len(problem.table)
    m = 1000

    time_limit: float = 5.5
    dx: List[int] = [-1, 0, 1, 0]
    dy: List[int] = [0, 1, 0, -1]

    def evaluate(answer: Board):
        ans = 0
        for i in range(n):
            for j in range(n):
                ans += abs(problem.table[i][j] - answer.table[i][j])
        return ans

    def remove_mountain(board: Board, m: Mountain):
        for i in range(n):
            for j in range(n):
                distance = abs(m.y - i) + abs(m.x - j)
                h = max(m.height - distance, 0)
                board.table[i][j] -= h

    def add_mountain(board: Board, m: Mountain):
        for i in range(n):
            for j in range(n):
                distance = abs(m.y - i) + abs(m.x - j)
                h = max(m.height - distance, 0)
                board.table[i][j] += h

    solution = [Mountain(0, 0, 0) for i in range(m)]
    for i in range(m):
        solution[i].x = random.randint(0, n - 1)
        solution[i].y = random.randint(0, n - 1)
        solution[i].height = random.randint(
            1, int(n * config.max_init_height_rate) - 1)
    solution_board = Board([[0 for i in range(n)] for j in range(n)])
    for i in range(m):
        add_mountain(solution_board, solution[i])

    eval = evaluate(solution_board)

    best_eval = 1e100
    best_solution: List[Mountain] = []

    counter = 0
    time_rate = 0.0

    def accept(eval_diff: float):
        return eval_diff < 0 or math.exp(-config.inverse_temperature * time_rate * eval_diff) < random.random()

    while True:

        index = random.randint(0, m - 1)
        neighbor_select = random.random()
        if neighbor_select < config.neighbor_select_rate:

            # 上下左右に移動
            direction = random.randint(0, 3)
            nx = solution[index].x + dx[direction]
            ny = solution[index].y + dy[direction]
            if 0 <= nx < n and 0 <= ny < n:
                remove_mountain(solution_board, solution[index])
                solution[index].x = nx
                solution[index].y = ny
                add_mountain(solution_board, solution[index])

                new_eval = evaluate(solution_board)
                eval_diff = new_eval - eval
                if accept(eval_diff):
                    eval = new_eval
                    if best_eval > eval:
                        best_eval = eval
                        best_solution = copy.deepcopy(solution)

                else:
                    remove_mountain(solution_board, solution[index])
                    solution[index].x -= dx[direction]
                    solution[index].y -= dy[direction]
                    add_mountain(solution_board, solution[index])

        else:
            # 高さを少しずらす
            HIGH = 1
            LOW = 0

            diff = max(1, int(config.max_diff_rate * n * (1.0 - time_rate)))
            high_low = random.randint(0, 1)
            if n < solution[index].height + diff:
                high_low = LOW
            if solution[index].height <= diff:
                high_low = HIGH

            if high_low == LOW:
                diff *= -1

            remove_mountain(solution_board, solution[index])
            solution[index].height += diff
            add_mountain(solution_board, solution[index])

            new_eval = evaluate(solution_board)
            eval_diff = new_eval - eval
            if accept(eval_diff):
                eval = new_eval
                if best_eval > eval:
                    best_eval = eval
                    best_solution = copy.deepcopy(solution)
            else:
                remove_mountain(solution_board, solution[index])
                solution[index].height -= diff
                add_mountain(solution_board, solution[index])

        counter += 1
        if counter % 128 == 0:
            print(f"best_eval: {best_eval}", file=sys.stderr)
            end_time = time.time()
            elapsed = end_time - start_time
            if elapsed > time_limit:
                break
            time_rate = elapsed / time_limit

    return best_eval, best_solution


if __name__ == "__main__":

    start_time = time.time()

    inverse_temperature = 1.31e-6
    neighbor_select_rate = 0.10
    max_init_height_rate = 0.90
    max_diff_rate = 0.47
    filepath = "tests/dataset/0.txt"

    if len(sys.argv) == 7:
        _temp = sys.argv[1]
        inverse_temperature = float(sys.argv[2])
        neighbor_select_rate = float(sys.argv[3])
        max_init_height_rate = float(sys.argv[4])
        max_diff_rate = float(sys.argv[5])
        filepath = sys.argv[6]

    config = Config(inverse_temperature,
                    neighbor_select_rate, max_init_height_rate, max_diff_rate)

    n = 100
    board_list = []
    with open(filepath, 'r') as fin:
        for i in range(n):
            line = list(map(int, fin.readline().strip().split(" ")))
            board_list.append(line)
    board = Board(board_list)

    eval, answer = solve(board, start_time, config)

    print(len(answer))
    for m in answer:
        print(f"{m.x} {m.y} {m.height}")

    # for maximization problem
    print(f"-{eval}", file=sys.stderr)
