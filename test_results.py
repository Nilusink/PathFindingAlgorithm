"""
Author:
Nilusink
"""
import matplotlib.pyplot as plt


def main():
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

    print(f"""
Finder 1:
total time: {sum(d_data["t1"])}
wins: {sum(d_data["l1"])}

Finder 2:
total time: {sum(d_data["t2"])}
wins: {sum(d_data["l2"])}

""")


if __name__ == '__main__':
    main()
