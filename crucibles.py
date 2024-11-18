import heapq
import copy


class Node:
    max_x = 0
    max_y = 0

    def __init__(self, in_weight, x_position, y_position):
        self.in_weight = in_weight
        self.edges = []
        self.x_position = x_position
        self.y_position = y_position
        if x_position is not None:
            self.__class__.max_x = max(x_position, self.__class__.max_x)
            self.__class__.max_y = max(y_position, self.__class__.max_y)

    def get_weight(self):
        return self.in_weight

    def add_edge(self, other):
        if other is not None:
            self.edges.append((other, other.get_weight()))

    def get_coords(self):
        return (self.x_position, self.y_position)

    def __repr__(self):
        if self.in_weight == 0:
            if len(self.edges) > 0:
                return "START"
            else:
                return "END"
        return f"x:{self.x_position}, y:{self.y_position}, w:"+str(self.get_weight())

    def __lt__(self, other):
        return self.in_weight < other.in_weight

    def __gt__(self, other):
        return self.in_weight > other.in_weight

    def __eq__(self, other):
        return id(self) == id(other)

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not self > other

    def __hash__(self):
        # a >= b ? a * a + a + b : a + b * b;
        return id(self)
        if self.__repr__() == "START":
            return self.max_x ** 2 + self.max_x + self.max_y
        elif self.__repr__() == "END":
            return (self.max_x + 1) ** 2 + self.max_x + self.max_y + 2
        if self.x_position >= self.y_position:
            return self.x_position ** 2 + self.x_position + self.y_position
        return self.x_position + self.y_position ** 2


class LavaCity:
    def __init__(self, input_map, max_steps):
        self.map = [[int(char) for char in list(line)] for line in input_map.splitlines()]
        self.start_node = Node(0, None, None)
        self.end_node = Node(0, None, None)
        self.graph = self.make_graph(self.map, max_steps)

    def make_graph(self, input_map, max_steps):
        jump = max_steps+1
        height = len(input_map)
        width = len(input_map[0])
        output = [[[[None
                     if (dimension % 2 == 0 and column % jump == step % jump)
                     or (dimension % 2 == 1 and row % jump == step % jump)
                     else Node(input_map[row][column], column, row)
                     for column in range(len(input_map[row]))]
                    for row in range(len(input_map))]
                   for step in range(max_steps)]
                  for dimension in range(2)]
        for dim in range(2):
            for step in range(max_steps):
                for row in range(height):
                    for node in output[dim][step][row]:
                        if node is not None:
                            coord_x, coord_y = node.get_coords()
                            if dim % 2 == 0:
                                if coord_x < width - 1:
                                    node.add_edge(output[dim][step][coord_y][coord_x + 1])
                                if coord_x > 0:
                                    node.add_edge(output[dim][step][coord_y][coord_x - 1])
                                if coord_y < height - 1:
                                    for alt_step in range(max_steps):
                                        node.add_edge(output[(dim+1)%2][alt_step][coord_y + 1][coord_x])
                                if coord_y < 0:
                                    for alt_step in range(max_steps):
                                        node.add_edge(output[(dim+1)%2][alt_step][coord_y - 1][coord_x])
                            else:
                                if coord_y < height - 1:
                                    node.add_edge(output[dim][step][coord_y + 1][coord_x])
                                if coord_y > 0:
                                    node.add_edge(output[dim][step][coord_y - 1][coord_x])
                                if coord_x < width - 1:
                                    for alt_step in range(max_steps):
                                        node.add_edge(output[(dim+1)%2][alt_step][coord_y][coord_x + 1])
                                if coord_x > 0:
                                    for alt_step in range(max_steps):
                                        node.add_edge(output[(dim+1)%2][alt_step][coord_y][coord_x - 1])
                            if coord_x == 0 and coord_y == 0:
                                self.start_node.add_edge(node)
                            elif coord_x == width-1 and coord_y == height-1:
                                node.add_edge(self.end_node)
        return output

    def find_path(self):
        outmap = self.map
        distances, previous_nodes = self.dijkstra(self.start_node)
        path = self.reconstruct_path(previous_nodes, self.start_node, self.end_node)
        for node in path[1:-1]:
            current_x, current_y = node.get_coords()
            try:
                if previous_x > current_x:
                    outmap[current_y][current_x] = "<"
                elif previous_x < current_x:
                    outmap[current_y][current_x] = ">"
                elif previous_y < current_y:
                    outmap[current_y][current_x] = "v"
                elif previous_y > current_y:
                    outmap[current_y][current_x] = "^"
            except:
                pass
            previous_x, previous_y = node.get_coords()
        output = ""
        for line in outmap:
            for char in line:
                output += str(char)
            output += "\n"
        return distances, output, path

    def print_internals(self, output):
        for dim in output:
            for step in dim:
                for line in step:
                    print(line)
                print("\n")
            print("\n")

    def dijkstra(self, start_node):
        # Dictionary to hold the shortest distances to each node
        distances = {start_node: 0}
        # Priority queue for visiting nodes, starting with the source
        priority_queue = [(0, start_node, None)]
        # Dictionary to store the optimal path
        previous_nodes = {}

        while priority_queue:
            current_distance, current_node, previous_coords = heapq.heappop(priority_queue)

            # Skip if we've already found a shorter path
            if current_distance > distances[current_node]:
                continue

            # Explore the neighbors
            for neighbor, weight in current_node.edges:
                distance = current_distance + weight

                # If a shorter path to the neighbor is found
                if neighbor.get_coords() != previous_coords and (neighbor not in distances or distance < distances[neighbor]):
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor, current_node.get_coords()))

        return distances, previous_nodes


# Helper to reconstruct the shortest path
    def reconstruct_path(self, previous_nodes, start_node, target_node):
        path = []
        current_node = target_node
        while current_node != start_node:
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
            if current_node is None:
                return None  # No path exists
        path.append(start_node)
        return path[::-1]  # Reverse the path
