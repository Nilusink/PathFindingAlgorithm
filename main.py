import time
from random import randint, sample
import pygame as pg


from classes import Vec2


# settings
WIDTH: int = 1600
HEIGHT: int = 800
NODE_RANGE: float = 200
NUMBER_NODES: int = 400
DRAW_ALL_CONNECTIONS: bool = False
SLEEP_TIME: float = 0.01


def generate_nodes(n) -> list[Vec2]:
    """
    generate the nodes to test the path finding algorythm

    :param n: number of nodes
    """
    nodes: list[Vec2] = [Vec2.from_cartesian(randint(0, WIDTH), randint(0, HEIGHT)) for _ in range(n)]
    return nodes


def main():
    pg.init()

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()

    def recalculate():
        """
        generate new nodes and redraw on screen
        """
        nodes = generate_nodes(NUMBER_NODES)

        # choose two nodes that need to be connected
        to_connect: list[Vec2] = sample(nodes, 2)

        # calculate paths
        paths: list[set[Vec2, Vec2]] = []
        node_connections: dict[Vec2, list] = {}
        for node in nodes:
            in_range: list[Vec2] = []

            # get all nodes in range
            for other_node in nodes:
                if not other_node == node:
                    # check if node is in range
                    if (node - other_node).length <= NODE_RANGE:
                        in_range.append(other_node)

            node_connections[node] = in_range

            # append to paths
            for other_node in in_range:
                pair: set[Vec2, Vec2] = {node, other_node}

                if pair not in paths:
                    paths.append(pair)

        def redraw():
            screen.fill((0, 0, 0))

            # draw connections
            if DRAW_ALL_CONNECTIONS:
                for connection in paths:
                    connection = list(connection)

                    # how good the connection is based on distance
                    quality: float = 1 - ((connection[0] - connection[1]).length / NODE_RANGE)

                    col = (255 * (1 - quality), 255 * quality, 0)
                    pg.draw.line(screen, col, connection[0].xy, connection[1].xy)

            # draw nodes
            for node in nodes:
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

                # draw ranges
                pg.draw.circle(screen, (0, 69, 0), (node.x, node.y), NODE_RANGE, width=1)

        def draw_path(path):
            for i in range(len(path)):
                if i != len(path) - 1:
                    pg.draw.line(screen, (0, 0, 255), path[i].xy, path[i + 1].xy, width=2)

        def calculate_path(origin: Vec2, target: Vec2, path: list[Vec2] = ..., to_avoid: set[Vec2] = ...) -> tuple[list[Vec2], bool]:
            if path is ...:
                path = [origin]

            if to_avoid is ...:
                to_avoid = set()

            to_avoid.add(origin)

            # tweaks
            connections = node_connections[origin]

            # if target is directly adjacent, return that
            if target in connections:
                path.append(target)
                return path, True

            # prefer shorter paths
            connections = sorted(connections, key=lambda n: (origin - n).length)
            # print([(origin - n).length for n in connections])

            for r_node in connections:
                if r_node not in to_avoid:
                    time.sleep(SLEEP_TIME)
                    path.append(r_node)

                    redraw()
                    draw_path(path)
                    pg.display.flip()

                    if r_node == target:
                        return path, True

                    to_avoid.add(r_node)
                    res = calculate_path(r_node, target, path.copy(), to_avoid)
                    if not res[1]:
                        continue

                    return res

            return path, False

        def shorten_path(path: list[Vec2]) -> list[Vec2]:
            """
            shorten a given path
            """
            if len(path) < 3:
                return path

            print(type(path), len(path))
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

                print(len(path), len(new_path))
                redraw()
                draw_path(new_path)
                pg.display.flip()

                path = new_path

            try:
                time.sleep(SLEEP_TIME)
                return [node] + shorten_path(path[1:])

            except RecursionError:
                print("recursion error")
                return path

        redraw()
        connection, success = calculate_path(to_connect[0], to_connect[1])

        redraw()
        if success:
            # try to shorten path
            connection = shorten_path(connection)
            print("shortened")
            draw_path(connection)
        pg.display.flip()

    recalculate()

    while True:
        events = pg.event.get()
        for event in events:
            match event.type:
                case pg.QUIT:
                    exit(0)

                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_SPACE:
                            recalculate()

        pg.display.flip()

        clock.tick(30)


if __name__ == '__main__':
    main()
