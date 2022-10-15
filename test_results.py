"""
Author:
Nilusink
"""
import matplotlib.animation as anim
import matplotlib.pyplot as plt
from time import sleep
import numpy as np


DELAY: float = .5


def re_read() -> dict:
    data: list[list[float]] = []
    with open("results.csv", "r") as inp:
        for line in inp.readlines():
            line = line.rstrip("\r")
            data.append([float(el) for el in line.split(",")])

    d_data: dict[str, list[float]] = {
        "t1": [],
        "l1": [],
        "t2": [],
        "l2": [],
    }
    for row in data:
        d_data["t1"].append(row[0])
        d_data["l1"].append(row[1])
        d_data["t2"].append(row[2])
        d_data["l2"].append(row[3])

    return d_data


def main():
    fig = plt.figure(num="Algorithms")
    # fig.set_title("Algorithms")
    # fig.set_ylabel("Wins")
    als = fig.add_subplot(1, 1, 1)
    als.grid()

    colors = ['tab:red', 'tab:green']
    names = ["Algorithm 1", "Algorithm 2"]

    def update(*_e):
        nonlocal lines
        d_data = re_read()
        lines.remove()
        lines = als.bar(names, np.array([sum(d_data["l1"]), sum(d_data["l2"])]), color=colors)

        als.relim()
        als.autoscale_view()

        plt.tight_layout()
        sleep(DELAY)

    lines = als.bar(names, [0, 0], color=colors)
    _a = anim.FuncAnimation(fig, update, repeat=True, interval=0)
    plt.show()

    d_data = re_read()
    print(f"""
Finder 1:
total time: {sum(d_data["t1"])}
first: {sum(d_data["l1"])}

Finder 2:
total time: {sum(d_data["t2"])}
first: {sum(d_data["l2"])}
""")


if __name__ == '__main__':
    main()
