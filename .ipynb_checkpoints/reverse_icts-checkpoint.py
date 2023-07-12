from single_agent_planner import compute_heuristics, a_star
from reverse_ict import ReverseIncreasingCostTree
from suboptimal_ict import SuboptimalIncreasingCostTree

from mdd import MDD, find_solution_in_joint_mdd, is_solution_in_joint_mdd
from map_utils import find_number_of_open_spaces
from performance_tracker import PerformanceTracker
import collections
import time as timer
import numpy as np
import itertools
import time
class ReverseICTSSolver(object):
    """A high-level ICTS search."""

    def __init__(self, map_details):
        """my_map   - list of lists specifying obstacle positions
        starts      - [(x1, y1), (x2, y2), ...] list of start locations
        goals       - [(x1, y1), (x2, y2), ...] list of goal locations
        """

        self.my_map = map_details.map_instance
        self.starts = map_details.starting_loc
        self.goals = map_details.goal_loc
        self.num_of_agents = len(map_details.goal_loc)

        self.stat_tracker = PerformanceTracker("ICTS")
        self.stat_tracker.set_map_name(map_details.name)
        self.stat_tracker.set_results_file_name(map_details.result_file_name)

        self.open_list = []

        # compute heuristics for the low-level search
        self.heuristics = []
        self.stat_tracker.time("heuristic_time", lambda: self.calculate_heuristics())

        self.ict = self.stat_tracker.time("time", lambda: self.create_ict())
        self.upper_bound = self.calculate_upper_bound_cost()
        self.possible_pairs = {}
        self.reverse_ict = None
    def calculate_heuristics(self):
        h = [dict() for g in range(len(self.goals))]
        for x, row in enumerate(self.my_map):
            for y, col in enumerate(row):
                if not col:
                    for g, goal in enumerate(self.goals):
                        h[g][(x,y)] = self.manhattan_distance((x,y), goal)
        self.heuristics = h

    def true_distance_bfs(self, my_map, goal):
        h = dict()
        q = collections.deque()
        indiv_ops = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        q.append((goal, 0))
        visited = set()
        visited.add(goal)
        while q:
            (x,y), this_h = q.popleft()
            h[(x,y)] = this_h
            children = []
            for op in indiv_ops:
                new_child = (x+op[0], y+op[1])
                if not my_map[new_child[0]][new_child[1]] and new_child not in visited:
                    visited.add(new_child)
                    children.append((new_child, this_h+1))
            if children:
                q.extend(children)
        return h

    def manhattan_distance(self, my_loc, goal):
        return abs(my_loc[0] - goal[0]) + abs(my_loc[1] - goal[1])

    def find_solution(self, start_time, time_limit):
        """ Finds paths for all agents from their start locations to their goal locations
        """
        #print("\nFinding ICTS Solution...")
        ######### Fill in the ICTS Algorithm here #########
        result = self.stat_tracker.time("time", lambda: self.bfs(start_time, time_limit))
        if result == -1:
            self.stat_tracker.stats['time'] = -1
            return []
        self.stat_tracker.write_stats_to_file(self.stat_tracker.get_results_file_name())
        return result
        ###################################################

    def calculate_upper_bound_cost(self):
        number_of_open_spaces = find_number_of_open_spaces(self.my_map)
        upper_bound = (self.num_of_agents ** 2) * number_of_open_spaces
        return upper_bound

    def bfs (self, start_time, time_limit):
        ict = self.ict
        open_list = ict.get_open_list()
        mdd_cache = {}
        nodes_expanded = 0
        while(len(open_list) != 0):
            current_node = ict.get_next_node_to_expand()
            node_cost = current_node.get_cost()
            if timer.time() - start_time > time_limit:
                return -1
            self.print_sanity_track(start_time, nodes_expanded)
            if not self.node_has_exceeded_upper_bound(current_node, self.upper_bound):
                solution_paths = self.find_paths_for_agents_for_given_cost(node_cost, mdd_cache, start_time, time_limit)
                #print(solution_paths)
                if(self.solution_exists(solution_paths)):
                    #print('node costs:', node_cost)
                    if sum(node_cost) > sum(self.initial_estimate):
                        dfs_res = self.depth_bounded_dfs(sum(node_cost), nodes_expanded, start_time, mdd_cache, time_limit)
                        if dfs_res:
                            return dfs_res
                    return solution_paths
                else:
                    self.stat_tracker.count('expanded nodes', lambda: ict.expand_next_node())
                    self.stat_tracker.record_max('max_open_list_length', len(open_list))
                    nodes_expanded += 1
            ict.pop_next_node_to_expand()
            #print(sum(node_cost))
        return []

    def cost_partitions(self, sum_of_costs, min_costs, index=0, path=None):
        #print('sum of min costs: ', np.sum(min_costs))
        #print('sum of costs: ', sum_of_costs)
        if path is None:
            path = [0] * len(min_costs)

        if index == len(min_costs):
            if sum(path) == sum_of_costs:
                yield path
        else:
            for cost in range(min_costs[index], sum_of_costs - sum(path[:index]) + 1):
                new_path = path.copy()
                new_path[index] = cost
                yield from self.cost_partitions(sum_of_costs, min_costs, index + 1, new_path)

    def depth_bounded_dfs(self, best_cost, nodes_expanded, start_time, mdd_cache, time_limit=60):
        best_solution = None
        cur_cost = None
        costs = self.cost_partitions(best_cost-1, self.initial_estimate)
        #print('costs:', list(self.cost_partitions(best_cost-1, self.initial_estimate)))
        #print(list(self.cost_partitions(best_cost-1, self.initial_estimate)))
        for cost in costs:
            if timer.time()-start_time > time_limit:
                return best_solution
            if self.reverse_ict and tuple(cost) in self.reverse_ict.closed_list:
                continue
            #print('cost:', cost)
            cur_cost, solution, nodes_expanded = self.dfs_inner(cost, nodes_expanded, start_time, mdd_cache, time_limit)
            if cur_cost == sum(self.initial_estimate):
                #print('Cost is inital estimate:', cur_cost)
                return solution
            elif cur_cost < best_cost:
                best_solution = solution
                break
        if cur_cost and cur_cost < best_cost:
            best_cost = cur_cost
            dfs_res = self.depth_bounded_dfs(best_cost, nodes_expanded, start_time, mdd_cache, time_limit)
            if dfs_res:
                return dfs_res
            else:
                return best_solution
        return best_solution


    def dfs_inner(self, cost, nodes_expanded, start_time, mdd_cache, time_limit):
        new_tree = self.stat_tracker.time("time", lambda: self.create_reverse_ict(cost))
        if self.reverse_ict:
            new_tree.closed_list = self.reverse_ict.closed_list
        ict = self.reverse_ict = new_tree
        min_cost = np.inf
        open_list = self.reverse_ict.get_open_list()
        best_solution = None
        while (len(open_list) != 0):
            current_node = ict.get_next_node_to_expand()
            node_cost = current_node.get_cost()
            if np.sum(node_cost) < min_cost:
                if timer.time() - start_time > time_limit:
                    #print('Minimum cost found:', best_cost)
                    return min_cost, best_solution, nodes_expanded
                self.print_sanity_track(start_time, nodes_expanded)
                if not self.node_has_exceeded_upper_bound(current_node, self.upper_bound):
                    #print(start_time)
                    solution_paths = self.find_paths_for_agents_for_given_cost(node_cost, mdd_cache, start_time, time_limit)
                    if (self.solution_exists(solution_paths)):
                        # print('node costs:', node_cost)
                        # print('node cost sums:', np.sum(node_cost))
                        min_cost = np.sum(node_cost)
                        best_solution = solution_paths
                        self.stat_tracker.count('expanded nodes', lambda: ict.expand_next_node())
                        self.stat_tracker.record_max('max_open_list_length', len(open_list))
                        nodes_expanded += 1
                    else:
                        self.stat_tracker.count('expanded nodes', lambda: ict.expand_next_node())
                        self.stat_tracker.record_max('max_open_list_length', len(open_list))
                        nodes_expanded += 1
                # ict.pop_next_node_to_expand()
            else:
                self.stat_tracker.count('expanded nodes', lambda: ict.expand_next_node())
                self.stat_tracker.record_max('max_open_list_length', len(open_list))
                nodes_expanded += 1
                # ict.pop_next_node_to_expand()
        #print(f'Minimum cost found: {min_cost}')
        return min_cost, best_solution, nodes_expanded

    def node_has_exceeded_upper_bound(self, node, upper_bound):
        agent_costs = node.get_cost()
        summed_agent_costs = sum(agent_costs)

        return summed_agent_costs > upper_bound

    def solution_exists(self, paths):
        return paths != None

    def find_paths_for_agents_for_given_cost(self, agent_path_costs, mdd_cache, start_time, time_limit):
        mdds = []
        for i in range(len(agent_path_costs)):
            paths_time = timer.time()
            agent_depth_key = (i, agent_path_costs[i])
            if agent_depth_key not in mdd_cache:
                agent_prev_depth_key = (i, agent_path_costs[i]-1)
                #agent_prev_depth_key_plus = (i, agent_path_costs[i]+1)
                t1 = timer.time()
                if agent_prev_depth_key in mdd_cache:
                    new_mdd = MDD(self.my_map, i, self.starts[i], self.goals[i], agent_path_costs[i], last_mdd = mdd_cache[agent_prev_depth_key])
                # elif agent_prev_depth_key_plus in mdd_cache:
                #     new_mdd = MDD(self.my_map, i, self.starts[i], self.goals[i], agent_path_costs[i], last_mdd = mdd_cache[agent_prev_depth_key_plus])
                else:
                    new_mdd = MDD(self.my_map, i, self.starts[i], self.goals[i], agent_path_costs[i])
                t2 = timer.time()
                mdd_cache[agent_depth_key] = new_mdd
            else: # Already cached
                new_mdd = mdd_cache[agent_depth_key]
            mdds.append(new_mdd)
            #print(f'paths time: {timer.time() - paths_time}')
        t1 = timer.time()
        for pair in itertools.combinations([mdd.agent for mdd in mdds], 2):
            pair = tuple(sorted(pair))
            pair = ((agent, agent_path_costs[agent]) for agent in pair)
            if pair not in self.possible_pairs:
                self.possible_pairs[pair] = is_solution_in_joint_mdd([mdds[agent] for agent, cost in pair], self.stat_tracker, start_time, time_limit)
            if not self.possible_pairs[pair]:
                return None
        solution_path = find_solution_in_joint_mdd(mdds, self.stat_tracker, start_time, time_limit)
        t2 = timer.time()
        return solution_path


    def create_ict(self):
        self.initial_estimate = self.find_cost_of_initial_estimate_for_root()
        #print(self.initial_estimate)
        if not self.initial_estimate:
            return None
        ict = SuboptimalIncreasingCostTree(self.my_map, self.starts, self.goals, self.initial_estimate)

        return ict

    def create_reverse_ict(self, suboptimal_costs):
        #suboptimal_costs = [cost+self.num_of_agents for cost in suboptimal_costs]
        ict = ReverseIncreasingCostTree(self.my_map, self.starts, self.goals, suboptimal_costs, self.initial_estimate)
        #ict = ReverseIncreasingCostTree(self.my_map, self.starts, self.goals, suboptimal_costs, [118, 85, 76])

        return ict


    def find_cost_of_initial_estimate_for_root(self):
        optimal_paths = self.find_most_optimal_paths()
        optimal_costs = []

        for i in range(len(optimal_paths)):
            if not optimal_paths[i]:
                return []
            optimal_costs.append(max(len(optimal_paths[i]) - 1, 0))

        return optimal_costs

    def find_most_optimal_paths(self):
        optimal_paths = []
        for agent in range(self.num_of_agents):
            optimal_paths.append(a_star(self.my_map, self.starts[agent], self.goals[agent], self.heuristics[agent], agent, []))
        return optimal_paths

    def print_sanity_track(self, start_time, num_expanded):
        elapsed = "{:.5f}".format(round(timer.time()-start_time, 3))
        print("\r[ Time elapsed: " + elapsed + "s | Nodes expanded: " + str(num_expanded), end=" ]", flush=True)