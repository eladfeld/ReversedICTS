from map_utils import MapDetails, import_mapf_instance
from icts import ICTSSolver
import maze_map_generator



if __name__ == '__main__':
    file = 'maps_1agents/arena.txt'
    my_map, starts, goals = import_mapf_instance(file)
    map_details = MapDetails('instance', file, my_map, starts, goals)
    icts = ICTSSolver(map_details)
    paths = icts.find_solution()
    print(paths[0])
    print(paths[1])
    print(paths[2])



