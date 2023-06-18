import copy
import collections

class ReverseIncreasingCostTree:
    def __init__(self, my_map, starts, goals, initial_cost, min_cost):
        """my_map   - list of lists specifying obstacle positions
        starts      - [(x1, y1), (x2, y2), ...] list of start locations
        goals       - [(x1, y1), (x2, y2), ...] list of goal locations
        """

        self.initial_cost = initial_cost
        self.my_map = my_map
        self.starts = starts
        self.goals = goals
        self.num_of_agents = len(goals)
        self.root = TreeNode(self.initial_cost, min_cost)

        self.open_list = collections.deque()
        self.open_list.append(self.root)
        self.closed_list = set(initial_cost)
        self.max_depth = 0

    def get_open_list(self):
        return self.open_list

    def get_next_node_to_expand(self):
        return self.open_list[-1]

    def pop_next_node_to_expand(self):
        return self.open_list.pop()

    def add_node_to_open_list(self, node):
        self.open_list.append(node)

    def add_unexplored_node_to_open_list(self, node):
        if node.get_cost() == (50, 69, 48, 101, 110):
            print("here")
            if node.get_cost() in self.closed_list:
                print("why")
        node_cost = node.get_cost()
        node_has_been_visited = node_cost in self.closed_list

        if not node_has_been_visited:
            self.closed_list.add(node_cost)
            self.open_list.append(node)

    def expand_next_node(self):
        next_node = self.pop_next_node_to_expand()
        next_node.expand_node()
        children = next_node.get_all_children()
        for child in children:
            self.add_unexplored_node_to_open_list(child)

class TreeNode:
    def __init__(self, agent_path_costs, min_cost):
        self.agent_path_costs = agent_path_costs
        self.child_nodes = []
        self.min_cost = min_cost

    def get_cost(self):
        return self.agent_path_costs

    def get_ith_child(self, i):
        return self.child_nodes[i]

    def get_all_children(self):
        return self.child_nodes

    def add_child(self, new_agent_path_costs):
        new_child = TreeNode(new_agent_path_costs, self.min_cost)
        self.child_nodes.append(new_child)

    def expand_node(self):
        for i in range(len(self.agent_path_costs)):
            new_costs = list(copy.deepcopy(self.agent_path_costs))
            new_costs[i] = new_costs[i] - 1
            if new_costs[i] < self.min_cost[i]:
                continue
            self.add_child(tuple(new_costs))
