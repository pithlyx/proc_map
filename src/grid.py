class Grid:
    """Grid of nodes with dynamic generation."""
    def __init__(self, seed):
        self.grid = {}
        self.node_count = 0
        self.seed = seed
        self.create_node(0, 0, type = 'empty')

    def get_node(self, x, y):
        return self.grid.get((x, y))

    def create_node(self, x, y, type = None):
        from src.node import Node
        self.node_count += 1
        node = Node(x, y, self.node_count, self.seed, type = type)
        self.grid[(x, y)] = node
        return node

    def get_radius(self, x, y, radius):
        """Get nodes within a radius from (x, y)."""
        return [[self.get_node(x + i, y + j) for j in range(-radius, radius + 1)] for i in range(-radius, radius + 1)]

    def generate_nodes_in_range(self, x, y, range):
        """Generate nodes within a range from (x, y)."""
        queue = [(x, y, 0)]
        visited = {(x, y)}
        nodes_in_range = []

        while queue:
            current_x, current_y, depth = queue.pop(0)
            if depth > range:
                break
            node = self.get_node(current_x, current_y) or self.create_node(current_x, current_y)
            nodes_in_range.append(node)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_x, next_y = current_x + dx, current_y + dy
                if (next_x, next_y) not in visited:
                    queue.append((next_x, next_y, depth + 1))
                    visited.add((next_x, next_y))

        return nodes_in_range
