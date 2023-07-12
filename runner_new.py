from map_utils import MapDetails, import_mapf_instance
from icts import ICTSSolver
from reverse_icts2 import ReverseICTSSolver
from time import time
import maze_map_generator
import numpy as np
import csv
import pandas as pd
import os

if __name__ == '__main__':
    time_limits = [5 * i for i in range(40)]  # 1 minute, 2 minutes, and 5 minutes in seconds

    files = ['mazes/maze100x100_3_37.txt',
    'mazes/maze50x50_3_34.txt',
    'mazes/maze50x50_3_56.txt',
    'mazes/maze50x50_3_190.txt',
    'mazes/maze25x25_3_196.txt',
    'mazes/maze50x50_3_114.txt',
    'mazes/maze25x25_3_50.txt',
    'mazes/maze25x25_3_88.txt']

    # files = ['mazes/' + file for file in os.listdir('mazes') if file.endswith('.txt') and file.startswith('maze')]

    all_results = []

    for file in files:
        print(file)
        my_map, starts, goals = import_mapf_instance(file)
        map_details = MapDetails('instance', file, my_map, starts, goals)

        result = {"map": file}

        start_time = time()
        reps = 1

        # optimal_paths_real = [497, False, 340, 214, 117, 205, 95, 109]
        # for num in range(reps):
        #     icts = ICTSSolver(map_details)
        #     optimal_paths = icts.find_solution()
        # regular_time = (time() - start_time) / reps
        #
        # result['regular_time'] = regular_time

        # if optimal_paths:
        #     for path in optimal_paths:
        #         while path[-1] == path[-2]:
        #             path.pop()
        #         optimal_paths_real.append(len(path))
        #     result['regular_sum_of_costs'] = np.sum(optimal_paths_real)
        # else:
        #     result['regular_sum_of_costs'] = False

        last_paths = None
        last_time = 0
        last_time_lim = 0

        for i, time_lim in enumerate(time_limits):
            if i == 0 or last_time >= last_time_lim - 5:
                start_time = time()
                for num in range(reps):
                    icts = ReverseICTSSolver(map_details)
                    paths = icts.find_solution(start_time, time_lim)
                reverse_time = (time() - start_time) / reps
                last_time = reverse_time
                last_paths = paths
            else:
                paths = last_paths
                reverse_time = last_time

            result[f'reverse_time_{time_lim}'] = reverse_time

            reverse_paths = []
            if paths:
                for path in paths:
                    while path[-1] == path[-2]:
                        path.pop()
                    reverse_paths.append(len(path))
                result[f'reverse_sum_of_costs_{time_lim}'] = np.sum(reverse_paths)
            else:
                result[f'reverse_sum_of_costs_{time_lim}'] = False

            last_time_lim = time_lim

        all_results.append(result)

        # Save intermediate results to csv
        pd.DataFrame(all_results).to_csv('result_of_time_steps_experiment.csv')
