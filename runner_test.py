from map_utils import MapDetails, import_mapf_instance
from icts_short import ICTSSolver
from reverse_icts2 import ReverseICTSSolver as ReverseICTSSolver2
from reverse_icts3 import ReverseICTSSolver as ReverseICTSSolver3

from time import time
import numpy as np
import pandas as pd

if __name__ == '__main__':
    time_limits = [30, 60, 120, 300]  # 1 minute, 2 minutes, and 5 minutes in seconds
    files = ['mazes/maze50x50_3_56.txt', 'mazes/maze50x50_3_114.txt', 'mazes/maze25x25_3_50.txt', 'mazes/maze50x50_3_15.txt']

    all_results = []

    reverse_solvers = {
        "solver2": ReverseICTSSolver2,
        "solver3": ReverseICTSSolver3
    }

    for file in files:
        print(file)
        my_map, starts, goals = import_mapf_instance(file)
        map_details = MapDetails('instance', file, my_map, starts, goals)

        result = {"map": file}

        start_time = time()
        reps = 1
        for num in range(reps):
            icts = ICTSSolver(map_details)
            optimal_paths = icts.find_solution()
        regular_time = (time() - start_time) / reps

        result['regular_time'] = regular_time

        optimal_paths_real = []
        if optimal_paths:
            for path in optimal_paths:
                while path[-1] == path[-2]:
                    path.pop()
                optimal_paths_real.append(len(path))
            result['regular_sum_of_costs'] = np.sum(optimal_paths_real)
        else:
            result['regular_sum_of_costs'] = False

        for solver_name, solver_class in reverse_solvers.items():
            last_paths = None
            last_time = 0
            last_time_lim = 0

            for i, time_lim in enumerate(time_limits):
                if i == 0 or last_time >= last_time_lim - 5:
                    start_time = time()
                    for num in range(reps):
                        icts = solver_class(map_details)
                        paths = icts.find_solution(start_time, time_lim)
                    reverse_time = (time() - start_time) / reps
                    last_time = reverse_time
                    last_paths = paths
                else:
                    paths = last_paths
                    reverse_time = last_time

                result[f'{solver_name}_time_{time_lim}'] = reverse_time

                reverse_paths = []
                if paths:
                    for path in paths:
                        while path[-1] == path[-2]:
                            path.pop()
                        reverse_paths.append(len(path))
                    result[f'{solver_name}_sum_of_costs_{time_lim}'] = np.sum(reverse_paths)
                else:
                    result[f'{solver_name}_sum_of_costs_{time_lim}'] = False

                last_time_lim = time_lim

        all_results.append(result)

        # Save intermediate results to csv
        pd.DataFrame(all_results).to_csv('results_test.csv')
