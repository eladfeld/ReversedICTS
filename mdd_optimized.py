def cost_partitions(sum_of_costs, min_costs, index=0, path=None):
    if path is None:
        path = [0] * len(min_costs)

    if index == len(min_costs):
        if sum(path) == sum_of_costs:
            yield path
    else:
        for cost in range(min_costs[index], sum_of_costs - sum(path[:index]) + 1):
            new_path = path.copy()
            new_path[index] = cost
            yield from cost_partitions(sum_of_costs, min_costs, index + 1, new_path)

costs = cost_partitions(20, [1, 4, 1, 5, 2])

for cost in costs:
    print(cost)