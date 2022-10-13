from typing import Callable, TypedDict
from classes import Vec2
import pygame as pg
import time


DRAW_STEPS: bool = False


class Node(TypedDict):
    name: Vec2
    hops: int
    connections: list[Vec2]


class PathCalculator:
    def __init__(
            self,
            node_connections: dict[Vec2, list],
            visible_nodes: list[Vec2],
            sleep_time: float,
            redraw_func: Callable,
            draw_path_func: Callable,
    ):
        self.node_connections = node_connections
        self.visible_nodes = visible_nodes
        self.draw_path = draw_path_func
        self.sleep_time = sleep_time
        self.redraw = redraw_func

    def calculate_path_1(
            self,
            origin: Vec2,
            target: Vec2,
            path: list[Vec2] = ...,
            to_avoid: set[Vec2] = ...,
    ) -> tuple[list[Vec2], bool]:
        if path is ...:
            path = [origin]

        if to_avoid is ...:
            to_avoid = set()

        to_avoid.add(origin)

        # tweaks
        connections = self.node_connections[origin]

        # purely for visuals
        for node in connections:
            if node not in self.visible_nodes:
                self.visible_nodes.append(node)

        # if target is directly adjacent, return that
        if target in connections:
            path.append(target)
            return path, True

        for r_node in connections:
            if r_node not in to_avoid:
                time.sleep(self.sleep_time)
                path.append(r_node)

                if DRAW_STEPS:
                    self.redraw()
                    self.draw_path(path, (255, 0, 0))
                    pg.display.flip()

                if r_node == target:
                    return path, True

                to_avoid.add(r_node)
                res = self.calculate_path_1(r_node, target, path.copy(), to_avoid)
                if not res[1]:
                    continue

                return res

        return path, False

    def calculate_path_2(
            self,
            origin: Vec2,
            target: Vec2,
            path: list[Vec2] = ...,
            to_avoid: set[Vec2] = ...,
    ) -> tuple[list[Vec2], bool]:
        if path is ...:
            path = [origin]

        if to_avoid is ...:
            to_avoid = set()

        to_avoid.add(origin)

        # tweaks
        connections = self.node_connections[origin]

        # purely for visuals
        for node in connections:
            if node not in self.visible_nodes:
                self.visible_nodes.append(node)

        # if target is directly adjacent, return that
        if target in connections:
            path.append(target)
            return path, True

        # prefer shorter paths
        connections = sorted(connections, key=lambda n: (origin - n).length)

        for r_node in connections:
            if r_node not in to_avoid:
                time.sleep(self.sleep_time)
                path.append(r_node)

                if DRAW_STEPS:
                    self.redraw()
                    self.draw_path(path, (0, 255, 0))
                    pg.display.flip()

                if r_node == target:
                    return path, True

                to_avoid.add(r_node)
                res = self.calculate_path_2(r_node, target, path.copy(), to_avoid)
                if not res[1]:
                    continue

                return res

        return path, False

    def calculate_path_3(
            self,
            origin: Vec2,
            target: Vec2,
            path: list[Vec2] = ...,
            to_avoid: set[Vec2] = ...,
    ) -> tuple[list[Vec2], bool]:
        if path is ...:
            path = [origin]

        if to_avoid is ...:
            to_avoid = set()

        to_avoid.add(origin)

        # tweaks
        connections = self.node_connections[origin]

        # purely for visuals
        for node in connections:
            if node not in self.visible_nodes:
                self.visible_nodes.append(node)

        # if target is directly adjacent, return that
        if target in connections:
            path.append(target)
            return path, True

        # prefer shorter paths
        connections = sorted(connections, key=lambda n: (origin - n).length)

        # # prefer longer paths
        connections = list(reversed(connections))

        for r_node in connections:
            if r_node not in to_avoid:
                time.sleep(self.sleep_time)
                path.append(r_node)

                if DRAW_STEPS:
                    self.redraw()
                    self.draw_path(path, (0, 0, 255))
                    pg.display.flip()

                if r_node == target:
                    return path, True

                to_avoid.add(r_node)
                res = self.calculate_path_3(r_node, target, path.copy(), to_avoid)
                if not res[1]:
                    continue

                return res

        return path, False


class AllKnowing:
    points: list[Vec2]
    connections: dict[Vec2, Node]
    connections_from_target: dict[Vec2, Node]

    def __init__(
            self,
            node_connections: dict[Vec2, list],
            visible_nodes: list[Vec2],
            sleep_time: float,
            redraw_func: Callable,
            draw_path_func: Callable,
            request_node_connections: Callable,

    ):
        self._draw_path_func = draw_path_func
        self._connection_requester = request_node_connections
        self.visible_nodes = visible_nodes
        self._redraw_func = redraw_func

        self.connections_from_target = {}
        self.connections = {}
        self.points = []

    def calculate(self, origin: Vec2, target: Vec2) -> list[Vec2] | None:
        """
        calculate the path
        """
        self.request_all(self.connections, origin)
        self.request_from_target(target, origin, self.connections_from_target)

        if target not in self.connections:
            return  # target was not found

        # calculate path
        def node_finder(origin: Vec2, target: Vec2, path: list[Vec2], ignore: list[Vec2]) -> list[Vec2] | None:
            ignore.append(origin)
            this_node = self.connections_from_target[origin] if origin in self.connections_from_target else self.connections[origin]

            connections = this_node["connections"]

            if target in connections:
                return path + [target]

            # remove already pinged nodes
            connections = list(filter(lambda e: (e not in ignore) and (e in self.connections_from_target), connections))

            if len(connections) < 1:
                return None

            # sort by furthest along the line
            connections = list(sorted(connections, key=lambda e: self.connections_from_target[e]["hops"]))

            next_node = connections[0]

            path.append(next_node)

            self._redraw_func()
            self._draw_path_func(path)
            pg.display.flip()

            return node_finder(next_node, target, path, ignore)

        return node_finder(origin, target, [origin], [])

    def request_from_target(self, target: Vec2, origin: Vec2, to_append: dict, max_iterations: int = 300) -> None:
        layers: dict[int, list[Vec2]] = {
            0: [target]
        }
        all_points: list[Vec2] = [target]
        current_layer: int = 0
        while current_layer < max_iterations:
            if origin in layers[current_layer]:
                break

            layers[current_layer + 1] = []
            for node in layers[current_layer]:
                new_nodes = self._connection_requester(node)
                new_nodes = list(filter(lambda e: e not in all_points, new_nodes))
                layers[current_layer + 1] += new_nodes
                all_points += new_nodes

            current_layer += 1

        for layer in layers:
            nodes = layers[layer]
            for node in nodes:
                to_append[node] = {
                    "name": nodes,
                    "hops": layer,
                    "connections": self._connection_requester(node)
                }

    def request_all(self, to_append: dict, origin: Vec2, ignore: list[Vec2] = ..., n=0) -> None:
        """
        request all possible node connections
        """
        if ignore is ...:
            ignore = []

        ignore.append(origin)
        if origin not in self.visible_nodes:
            self.visible_nodes.append(origin)

        points = self._connection_requester(origin)

        for point in points:
            if point not in self.visible_nodes:
                self.visible_nodes.append(point)

            if point not in to_append:
                to_append[point] = {
                    "name": point,
                    "hops": n+1,
                    "connections": [],
                }
        if origin in to_append:
            to_append[origin]["connections"] = points

        # request all points from each point
        for point in points:
            if point not in ignore:
                self.request_all(to_append, point, ignore, n+1)
