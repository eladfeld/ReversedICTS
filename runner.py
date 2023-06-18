from map_utils import MapDetails, import_mapf_instance
from icts import ICTSSolver
from reverse_icts import ReverseICTSSolver
from time import time
import maze_map_generator
import numpy as np


if __name__ == '__main__':

    #file = 'mazes/maze12x12_3_72.txt'
    file = 'our_mazes/maze_75_75_5_0.25.txt'
    my_map, starts, goals = import_mapf_instance(file)
    map_details = MapDetails('instance', file, my_map, starts, goals)

    start_time = time()
    reps = 1
    for num in range(reps):
        icts = ReverseICTSSolver(map_details)
        paths = icts.find_solution()
    print('Time taken reverse: ', (time() - start_time) / reps)

    start_time = time()

    for num in range(reps):
        icts = ICTSSolver(map_details)
        optimal_paths = icts.find_solution()
    print('Time taken regular: ', (time() - start_time)/reps)

    print(optimal_paths[0])

    print(paths[0])

    print(optimal_paths[1])
    print(paths[1])
    print(optimal_paths[2])
    print(paths[2])

