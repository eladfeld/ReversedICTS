from map_utils import MapDetails, import_mapf_instance
from reverse_icts import ReverseICTSSolver
import maze_map_generator
from time import time

if __name__ == '__main__':
    start_time = time()
    file = 'maps_11agents/arena.txt'
    my_map, starts, goals = import_mapf_instance(file)
    map_details = MapDetails('instance', file, my_map, starts, goals)
    icts = ReverseICTSSolver(map_details)
    paths = icts.find_solution()
    print(paths[0])
    print(paths[1])
    print(paths[2])
    print("Time taken: ", time() - start_time)



