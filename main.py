from concurrent.futures import ProcessPoolExecutor
from threading import Thread
from typing import Callable
from random import sample
import pygame as pg
import numpy as np
import time
import csv
import sys


from classes import Vec2
from path_finders import AllKnowing, AllKnowing2


# settings
WIDTH: int = 2560
HEIGHT: int = 1440
NODE_RANGE: float = 150
NUMBER_NODES: int = 500
DRAW_ALL_CONNECTIONS: bool = True
WRITE_DATA: bool = True
SLEEP_TIME: float = .0
LOOP: bool = False
THREADS: int = 100


# set recursion limit
sys.setrecursionlimit(NUMBER_NODES**2)


def generate_nodes(n, n_threads: int = 1) -> list[Vec2]:
    """
    generate the nodes to test the path finding algorythm

    :param n: number of nodes
    :param n_threads: the number of threads to use
    """
    per_thread = n // n_threads
    threads: list[Thread] = []
    nodes: list[Vec2] = []

    def _generate_nodes(_n):
        xs = np.random.randint(0, WIDTH, _n)
        ys = np.random.randint(0, HEIGHT, _n)

        for i in range(_n):
            nodes.append(Vec2.from_cartesian(xs[i], ys[i]))

    # start generation threads
    for _ in range(n_threads-1):
        threads.append(Thread(target=_generate_nodes, args=[per_thread]))
        threads[-1].start()

    # last thread per_thread + rest
    threads.append(Thread(
        target=_generate_nodes,
        args=[n - per_thread * (n_threads-1)]
    ))
    threads[-1].start()

    # wait for threads
    for t in threads:
        t.join()

    return nodes


def connections_for_nodes(nodes_to_handle: list[Vec2], nnodes: list[Vec2]):
    nnode_connections: dict[int, list] = {}
    ppaths: list[set[Vec2, Vec2]] = []

    for node in nodes_to_handle:
        in_range: list[Vec2] = []

        # get all nodes in range
        for other_node in nnodes:
            if not other_node == node:
                # check if node is in range
                if (node - other_node).length <= NODE_RANGE:
                    in_range.append(other_node)

        nnode_connections[hash(node)] = in_range

        # append to paths
        for other_node in in_range:
            pair: set[Vec2, Vec2] = {node, other_node}

            if pair not in ppaths:
                ppaths.append(pair)

    return nnode_connections, ppaths


def main():
    shortest_n = [0, 0, 0]
    times = [0, 0, 0]

    pg.init()

    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    clock = pg.time.Clock()

    pool = ProcessPoolExecutor()

    def recalculate():
        """
        generate new nodes and redraw on screen
        """
        s = time.perf_counter()
        nodes = generate_nodes(NUMBER_NODES, 1)
        print(f"generated: {time.perf_counter() - s}s")

        # choose two nodes that need to be connected
        to_connect: list[Vec2] = sample(nodes, 2)
        visible_nodes: list[Vec2] = to_connect.copy()

        # calculate paths
        paths: list[set[Vec2, Vec2]] = []
        node_connections: dict[int, list] = {}
        s = time.perf_counter()

        per_thread = len(nodes) // THREADS
        futures: list = []

        # start generation threads
        for n_thread in range(THREADS - 1):
            start = per_thread * n_thread
            end = per_thread * (n_thread + 1)
            if end - start < 1:
                continue

            futures.append(pool.submit(
                connections_for_nodes,
                nodes[start:end],
                nodes
            ))

        # last thread per_thread + rest
        futures.append(pool.submit(
            connections_for_nodes,
            nodes[per_thread * (THREADS-1):],
            nodes
        ))

        # wait for threads
        for f in futures:
            n, p = f.result()
            node_connections.update(n)
            paths.extend(p)

        print(f"connections took {time.perf_counter() - s}s")

        def redraw():
            screen.fill((0, 0, 0))

            # draw connections
            if DRAW_ALL_CONNECTIONS:
                for connection in paths:
                    connection = list(connection)

                    # how good the connection is based on distance
                    quality = 1 - ((
                                           connection[0] - connection[1]
                                   ).length / NODE_RANGE)

                    col = (255 * (1 - quality), 255 * quality, 0)
                    pg.draw.line(screen, col, connection[0].xy, connection[1].xy)

            # draw nodes
            for node in visible_nodes:
                # if the node is a target node, it should have another color
                if node in to_connect:
                    if node == to_connect[0]:
                        col = (255, 0, 255)

                    else:
                        col = (255, 255, 0)

                else:
                    col = (255, 255, 255)

                radius = 10 if node in to_connect else 5
                pg.draw.circle(screen, col, (node.x, node.y), radius)

        def draw_path(path, color: tuple[int, int, int] = ...):
            if color is ...:
                color = (0, 0, 255)

            for i in range(len(path)):
                if i != len(path) - 1:
                    pg.draw.line(screen, color, path[i].xy, path[i + 1].xy, width=2)

                node = path[i]
                pg.draw.circle(screen, (0, 50, 0), (node.x, node.y), NODE_RANGE, width=1)

        def shorten_path(path: list[Vec2]) -> list[Vec2]:
            """
            shorten a given path
            """
            if len(path) < 3:
                return path

            node = path[0]

            # filter all nodes below
            better_connections = list(reversed(path[2:]))

            # remove all out-of-range nodes
            better_connections = list(filter(lambda n: (node - n).length <= NODE_RANGE, better_connections))

            if better_connections:
                # choose the highest value node
                r_node = better_connections[0]

                # remove all not-needed nodes
                try:
                    new_path = [node] + path.copy()[path.index(r_node):]

                except ValueError:
                    print(r_node.xy, [p.xy for p in path])
                    raise

                redraw()
                draw_path(new_path)
                pg.display.flip()

                path = new_path

            try:
                time.sleep(SLEEP_TIME / 10)
                return [node] + shorten_path(path[1:])

            except RecursionError:
                print("recursion error")
                return path

        # calculator = PathCalculator(
        #     node_connections,
        #     visible_nodes,
        #     SLEEP_TIME,
        #     redraw,
        #     draw_path,
        # )

        def request_nodes(key):
            return node_connections[hash(key)]

        finder = AllKnowing(
            node_connections,
            visible_nodes,
            SLEEP_TIME,
            redraw,
            draw_path,
            request_nodes,
        )

        finder2 = AllKnowing2(
            node_connections,
            visible_nodes,
            SLEEP_TIME,
            redraw,
            draw_path,
            request_nodes,
        )

        def calc(func: Callable, color):
            redraw()
            connection = func(*to_connect)

            if issubclass(type(connection), tuple):
                connection = connection[0]

            redraw()
            if connection:
                # try to shorten path
                connection = shorten_path(connection)
                draw_path(connection, color)

            pg.display.flip()
            return connection

        def path_length(path) -> float:
            """
            calculates the length of a path
            """

            s = 0
            for j in range(len(path) - 1):
                s += (path[j] - path[j - 1]).length

            return s

        def winner(paths) -> tuple[list[int], float]:
            """
            determines which of the paths is the best
            """
            distances = [0] * len(paths)
            for i in range(len(paths)):
                current_path = paths[i]
                distances[i] += path_length(current_path)

            shortest = min(distances)
            # check if multiple wins

            out = []
            for i in range(len(distances)):
                if distances[i] == shortest:
                    out.append(i)
            return out, shortest

        def test():
            redraw()
            ts = time.perf_counter()
            p1 = calc(finder.calculate, (255, 0, 0))
            t1 = time.perf_counter()
            p2 = calc(finder2.calculate, (0, 255, 0))
            t2 = time.perf_counter()

            if p1:
                draw_path(p1, (255, 0, 0))

            if p2:
                draw_path(p2, (0, 255, 0))

            # append times
            d1 = d2 = None
            if p1 is not None:
                d1 = t1 - ts
                times[0] += d1

            if p2 is not None:
                d2 = t2 - t1
                times[1] += d2

            if not p1 or not p2:
                return

            # winner declaration
            all_paths = [p1, p2]
            winner_ids, shortest_l = winner(all_paths)

            shortest = all_paths[winner_ids[0]]

            draw_path(shortest, (255, 255, 255))

            if WRITE_DATA:
                if all([d1 is not None, d2 is not None]):
                    with open("results.csv", "a") as out:
                        writer = csv.writer(out)
                        writer.writerow([
                            d1, int(all_paths.index(p1) in winner_ids),
                            d2, int(all_paths.index(p2) in winner_ids),
                        ])

            if shortest == p1:
                shortest_n[0] += 1

            elif shortest == p2:
                shortest_n[1] += 1

        test()

        pg.display.flip()

        events = pg.event.get()
        for event in events:
            match event.type:
                case pg.QUIT:
                    exit(0)

                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            return False
        return LOOP

    try:
        while True:
            events = pg.event.get()
            for event in events:
                match event.type:
                    case pg.QUIT:
                        exit(0)

                    case pg.KEYDOWN:
                        match event.key:
                            case pg.K_SPACE:
                                res = True
                                while res:
                                    res = recalculate()

                                # raise SystemExit

                            case pg.K_ESCAPE:
                                raise SystemExit

            pg.display.flip()

            clock.tick(30)

    finally:
        print(shortest_n)
        print(times)


if __name__ == '__main__':
    main()
