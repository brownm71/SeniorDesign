import matplotlib.pyplot as plt
from fileIO import *
from flaw import *


def std_div_check(actual : Teams_and_Meta, constructed : Teams_and_Meta):
    res = {}
    count = 0
    for i in range(len(actual.teams)):
        for j in range(len(actual.teams[i].list_of_players)):
            for time in actual.teams[i].list_of_players[j].times_to_pos.keys():
                if constructed.teams[i].list_of_players[j].times_to_pos[time] is None or len(constructed.teams[i].list_of_players[j].times_to_pos[time]) == 0:
                            continue
                ax,ay = actual.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
                cx, cy = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
                # stdDiv = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['SD']
                stdDiv = float(constructed.meta.get('net_standard_deviation',0))
                count += 1
                if (abs(cx-ax) > stdDiv):
                    res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]
                elif (abs(cy-ay) > stdDiv):
                    res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]

    return res,count

def calc_avrg_conf(actual):
    conf = []
    for i in range(len(actual.teams)):
        for j in range(len(actual.teams[i].list_of_players)):
            for time in actual.teams[i].list_of_players[j].times_to_pos.keys():
                if actual.teams[i].list_of_players[j].times_to_pos[time] is None or len(actual.teams[i].list_of_players[j].times_to_pos[time]) == 0:
                            continue
                conf.append(actual.teams[i].list_of_players[j].times_to_pos[time][0]["CONFIDENCE"])
    return (sum(conf)/len(conf))    



def randomThing():
    return random.randint(20, 40) / 100

# if __name__ == "__main__":
#     import multiprocessing as mp
#     file = readJson(r"jimJson.json")

#     result = {}
#     r2 = {}

#     for i in range(1, 15):
#         random.seed(42)
#         r = create_reconstructed(file,i+1,33,15,75,randomThing, True)
#         writeJson("jimmy.json", r)
#         result[i+1] = calc_avrg_conf(r)
#         std_check_res, std_count = std_div_check(file, r)


#         r2[i+1] = ((1 - (len(std_check_res)/std_count)))

#     x_values = list(result.keys())
#     y_values = list(result.values())

#     y_val_2 = list(r2.values())

#     plt.figure(figsize=(10, 6))
#     plt.plot(x_values, y_values,label = 'Confidence', marker='o', linestyle='-')
#     plt.plot(x_values, y_val_2 ,label = 'Actual % Pass', marker='x', linestyle='--')
#     plt.title('Average Confidence and Pass Rate vs. Number of Combined Files')
#     plt.xlabel('Number of Flawed Files Combined')
#     plt.ylabel('Value / Percentage')
#     plt.xticks(x_values)
#     plt.legend()
#     plt.grid(True)
#     plt.show()

def process_iteration(i, file_data, random_thing):
    """
    Worker function executed by each core. 
    It must be at the top level of the script.
    """
    # Setting the seed inside the worker replicates your original logic
    random.seed(42) 
    
    index = i + 1
    
    # 1. Run the heavy reconstruction
    r = create_reconstructed(file_data, index, 25, 15, 75, random_thing, True)
    
    # 2. Prevent Race Conditions
    # Appending the index ensures cores aren't writing over each other.
    # writeJson(f"jimmy_{index}.json", r)
    
    # 3. Calculate Metrics
    avg_conf = calc_avrg_conf(r)
    std_check_res, std_count = std_div_check(file_data, r)
    pass_rate = 1 - (len(std_check_res) / std_count)
    
    # Return the data so the main process can plot it
    return index, avg_conf, pass_rate


if __name__ == "__main__":
    import multiprocessing as mp
    file = readJson(r"jimJson.json")

    result = {}
    r2 = {}

    # Pack the arguments for the worker pool
    # Assuming randomThing is defined in your global scope
    tasks = [(i, file, randomThing) for i in range(1, 15)]

    # Initialize a pool of workers using all available CPU cores
    with mp.Pool(processes=mp.cpu_count()) as pool:
        # starmap unpacks our tuple of arguments and feeds them to the worker
        results = pool.starmap(process_iteration, tasks)

    # Unpack the returned results into your original dictionary format
    for index, avg_conf, pass_rate in results:
        result[index] = avg_conf
        r2[index] = pass_rate

    # IMPORTANT: Multiprocessing can return results out of order!
    # We must sort the x_values so the matplotlib lines draw correctly from left to right.
    x_values = sorted(result.keys())
    y_values = [result[x] for x in x_values]
    y_val_2 = [r2[x] for x in x_values]

    # Plotting code remains exactly the same
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label='Confidence', marker='o', linestyle='-')
    plt.plot(x_values, y_val_2, label='Actual % Pass', marker='x', linestyle='--')
    plt.title('Average Confidence and Pass Rate vs. Number of Combined Files')
    plt.xlabel('Number of Flawed Files Combined')
    plt.ylabel('Value / Percentage')
    plt.xticks(x_values)
    plt.legend()
    plt.grid(True)
    plt.show()