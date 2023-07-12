def prioritized_planning(self, my_map, agents, starts, goals):
    paths = []
    costs = []
    occupied = set()  # set of (x, y, t) tuples representing occupied cells
    for agent in agents:
        start = starts[agent]
        goal = goals[agent]
        path, cost = self.find_path_for_agent(my_map, agent, start, goal, occupied)
        paths.append(path)
        costs.append(cost)
        # add the cells in the new path to the occupied set
        for t, cell in enumerate(path):
            occupied.add((*cell, t))
    return paths, costs

def find_path_for_agent(self, my_map, agent, start, goal, occupied):
    open_list = [((start, 0), 0)]  # nodes to be explored ((cell, time), cost)
    closed_list = set()  # explored nodes
    came_from = {}  # mapping from node to its predecessor

    while open_list:
        (current, time), cost = min(open_list, key=lambda x: x[1])  # get node with minimum cost
        open_list.remove(((current, time), cost))

        if current == goal:
            return self.reconstruct_path(came_from, (start, 0), (goal, time)), cost

        closed_list.add((current, time))

        for neighbor in self.get_valid_neighbors(my_map, current, time, occupied):
            if (neighbor, time + 1) not in closed_list:
                new_cost = cost + 1  # assuming unit cost for each step
                open_list.append(((neighbor, time + 1), new_cost))
                came_from[(neighbor, time + 1)] = (current, time)

    return None, float('inf')  # return None and infinity if no path is found

def get_valid_neighbors(self, my_map, cell, time, occupied):
    neighbors = []
    for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # up, right, down, left
        neighbor = (cell[0] + direction[0], cell[1] + direction[1])
        if self.is_valid_cell(my_map, neighbor) and (neighbor, time + 1) not in occupied:
            neighbors.append(neighbor)
    return neighbors

def is_valid_cell(self, my_map, cell):
    return 0 <= cell[0] < len(my_map) and 0 <= cell[1] < len(my_map[0]) and my_map[cell[0]][cell[1]] == '.'

def reconstruct_path(self, came_from, start, goal):
    path = [goal]
    cost = 0
    while path[-1] != start:
        path.append(came_from[path[-1]])
        cost += 1
    path.reverse()
    return path, cost
