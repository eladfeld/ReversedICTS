import csv
import numpy as np
import matplotlib.pyplot as plt
import csv


def print_graph():
    path = 'strp15_result_of_time_steps_experiment.csv'
    with open(path, 'r') as file:
        data = csv.reader(file)
        names = []
        times = []
        results = []
        next(data)
        for map_results in data:
            time = []
            result = []
            names.append(map_results[1])
            for i in range(4, len(map_results), 2):
                if map_results[i + 1] != 'False':
                    time.append(float(map_results[i]))
                    result.append(int(map_results[i + 1]))
            times.append(time)
            results.append(result)
        # files_first_graph = [5, 4, 6, 7]
        files_first_graph = [i for i in range(8)]
        for i in files_first_graph:
            plt.plot(times[i], results[i], label=names[i][6:-4])
            # plt.title(name[6:-4])
            plt.xlim(0, 200)
        plt.xlabel('Time cap(seconds)')
        plt.ylabel('All agents cost')
        plt.title('Solution Cost Improvement Over Time')
        plt.legend()
        plt.show()


print_graph()