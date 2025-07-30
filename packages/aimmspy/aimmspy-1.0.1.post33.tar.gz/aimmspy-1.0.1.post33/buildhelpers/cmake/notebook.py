import os
import platform
import re
import subprocess
import matplotlib.pyplot as plt
import json
import graphviz
import numpy as np
import pandas as pd
import traceback

# check if a file is an executable


def is_exe(fpath):

    if (platform.system() == 'Windows' and fpath.endswith('.exe')):
        return True
    elif (platform.system() == 'Linux' and fpath.endswith('')):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    elif (platform.system() == 'Darwin') and fpath.endswith(''):
        return os.access(fpath, os.X_OK)
    else:
        return False

def clean_plot_names(plot_names):
    cleaned_names = []
    for name in plot_names:
        # Remove everything before the /
        name = name.split('/')[-1]
        # Remove _plot_number
        name = re.sub(r'_plot_\d+', '', name)
        cleaned_names.append(name)
    return cleaned_names

def plot_benchmarks(compiler_comparison=True, run_benchmarks=True):
    try:

        # combined dict
        # key: name of the benchmark
        # value: list of the real time of the benchmark
        combined = {}
        combined_line_graph = {}
        # find all executables with benchmarks in the name
        # and run them with the benchmark flag
        # save the result in a json file
        # plot the result

        executables = []
        # recursive search for executables
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if '_benchmarks' in file and (file.endswith('.exe') and platform.system() == 'Windows') or (file.endswith('') and platform.system() != 'Windows'):
                    # if previous folder was Release or RelWithDebInfo run
                    if 'Release' in root or 'RelWithDebInfo' in root:
                        executables.append(os.path.join(root, file))
                        
        # filter out any file that have .cpp or .o in the name
        executables = [x for x in executables if '.cpp' not in x and '.o' not in x]
        #if run benchmarks is true and on windows only allow .exe files
        if run_benchmarks and platform.system() == 'Windows':
            executables = [x for x in executables if '.exe' in x]
        
        for executable in executables:
            cwd = os.path.dirname(executable)

            # split the path to get the compiler name
            compiler = None
            compiler_path_parts = executable.split(os.sep)
            for i in range(len(compiler_path_parts)):
                if compiler_path_parts[i] == 'out':
                    compiler = compiler_path_parts[i + 2]

            if compiler == None:
                print(f"Error: compiler not found for {executable}")
                return

            try:
                if run_benchmarks:
                    print (f"running benchmarks for: { executable }")
                    success = subprocess.run([executable, '--benchmark_out_format=json',
                                             f'--benchmark_out=benchmark_result.json', '--benchmark_min_warmup_time=2'], cwd=cwd, capture_output=True)
                    # get the output of the executable
                    print(success.stderr.decode('utf-8'))
                    print(success.stdout.decode('utf-8'))

                    if success.returncode != 0:
                        print(f"benchmark failed for: { executable }")
                        return

            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                return

            data = {}

            with open(f'{cwd}/benchmark_result.json') as f:
                data = json.load(f)
                
            plots = 1

            dict = {}
            line_graph = {}

            for i in data['benchmarks']:
                name = i['name']
                # if On in than skip 
                if 'BigO' in name or 'RMS' in name:
                    continue

                plot_number = None

                for name_part in name.replace('/', '_').split('_'):
                    if 'plot' in name_part:
                        # next value is the plot number or if next part is line than the plot number is the next value
                        tmp = name.replace(
                            '/', '_').split('_')[name.replace('/', '_').split('_').index(name_part) + 1]
                        if 'line' in tmp:
                            # get the next value
                            plot_number = int(name.replace(
                                '/', '_').split('_')[name.replace('/', '_').split('_').index(name_part) + 2])
                        else:
                            plot_number = int(tmp)

                if plot_number != None:
                    if 'plot_line' in i['name']:
                        # name split on / and get the first part
                        
                        # if there are more than 1 / in than add the first parts to the name and the last part to the count
                        split_array = i['name'].split('/')
                        name = ''
                        count = ''
                        if i['name'].count('/') > 1:
                            
                            # remove the last part from the array and join the rest replacing / with _
                            name = '_'.join(split_array[:-1])
                            count = split_array[-1]
                        else:
                            name = split_array[0]
                            count = split_array[1]
                        line_graph.update(
                            {i['name']: (plot_number, i['real_time'], count)})
                    else:
                        dict.update({name: (plot_number, i['real_time'])})
                        # fill the combined dict
                        if name.replace(f'_plot_{plot_number}', '') not in combined:
                            combined.update({name.replace(f'_plot_{plot_number}', ''): [
                                            (compiler, i['real_time'])]})
                        else:
                            combined[name.replace(f'_plot_{plot_number}', '')].append(
                                (compiler, i['real_time']))

            # make an array of all real times for each plot
            plot = {}
            plot_names = []

            for key, value in dict.items():
                plot_number, real_time = value

                if plot_number not in plot:
                    plot.update(
                        {plot_number: [(real_time, key.replace(f'_plot_{plot_number}', ''))]})
                else:
                    plot[plot_number].append(
                        (real_time, key.replace(f'_plot_{plot_number}', '')))
               
            if len(plot.items()) > 1: 
                plt.subplots(figsize=(20, 5))
                    
            for key, values in plot.items():
                # values.sort(key=lambda x: x[0])
                values = values[:10]
                plot_names = [x[1] for x in values]
                values = [x[0] for x in values]

                # round the values to 4 decimals
                values = [round(x, 2) for x in values]
                
                plt.subplot(1, len(plot), plots)
                for i in range(len(values)):
                    # plot vertical bar chart
                    plt.bar(i, values[i], align='center')
                    # add the value on top of the bar
                    plt.text(i, values[i], str(values[i]),
                             ha='center', va='bottom')

                # for all plot names if contains _plot_number remove it and remove everything before the /
                cleaned_names = clean_plot_names(plot_names)
                
                plt.xticks(np.arange(len(values)),
                           cleaned_names, rotation=45)
                plt.ylabel(f'time in {data["benchmarks"][0]["time_unit"]}')
                plt.title(f'plot {key}')
                plots += 1
            
            plt.show()

            plot = {}
            plot_names = []
            # plot the line graph

            line_graph_dict = {}
            if len(line_graph) > 0:
                for key, value in line_graph.items():
                    plot_number, real_time, count = value

                    # fill line_graph_dict with the plot number as key and after a dict with the name as key and the real time as values
                    if plot_number not in line_graph_dict:
                        line_graph_dict.update(
                            {plot_number: {key.replace('/' + count, ''): [(real_time, count)]}})
                    else:
                        if key.replace('/' + count, '') not in line_graph_dict[plot_number]:
                            line_graph_dict[plot_number].update(
                                {key.replace('/' + count, ''): [(real_time, count)]})
                        else:
                            line_graph_dict[plot_number][key.replace(
                                '/' + count, '')].append((real_time, count))

                # plot the line graph

                for key, value in line_graph_dict.items():
                    plt.subplots(figsize=(20, 5))
                    for name, values in value.items():
                        real_times = []
                        counts = []
                        for i in range(len(values)):
                            real_time, count = values[i]
                            real_times.append(real_time)
                            counts.append(count)

                        # name remove _plot_number
                        name = name.replace(f'_plot_line_{key}', '')
                        combined_line_graph.update(
                            {(compiler, name): (real_times, counts)})
                        plt.plot(counts, real_times, label=name, marker='o',
                                 linestyle='dashed', linewidth=2, markersize=6)

                    plt.legend()
                    plt.ylabel(f'time in {data["benchmarks"][0]["time_unit"]}')
                    plt.xlabel('count')
                    plt.title(f'plot {key}')
                    plt.show()

        if compiler_comparison:
            for key, value in combined.items():
                compilers = []
                if len(value) == 1:
                    continue
                iota = [i for i in range(len(value))]

                for i in range(len(value)):
                    compiler, real_time = value[i]

                    if compiler not in compilers:
                        compilers.append(compiler)

                # if compiler is smaller than iota than probably you used the same name for a benchmark twice
                if len(compilers) < len(iota):
                    print(
                        'error in compiler comparison plot you used the same name for a benchmark twice')

                if len(compilers) > 1:
                    for i in range(len(value)):
                        compiler, real_time = value[i]
                        real_time = round(real_time, 4)
                        plt.text(i, real_time, str(real_time),
                                 ha='center', va='bottom')
                        plt.bar(i, real_time, align='center')

                    plt.xticks(iota, compilers, rotation='horizontal')
                    plt.ylabel(f'time in {data["benchmarks"][0]["time_unit"]}')
                    plt.title(key)
                    plt.show()

            # from combined line graph count the amount of unique names in the key

            unique_names = []
            for key, value in combined_line_graph.items():
                compiler, name = key
                if compiler not in unique_names:
                    unique_names.append(compiler)

            if len(unique_names) > 1:

                line_plot_compiler_comparison = {}
                for key, value in combined_line_graph.items():
                    # if key name is equal but compiler different add to a dict
                    compiler, name = key
                    real_times, counts = value
                    data = (real_times, counts)

                    if name not in line_plot_compiler_comparison:
                        line_plot_compiler_comparison.update(
                            {
                                name:
                                [
                                    {
                                        compiler: {
                                            "real_times": real_times,
                                            "counts": counts
                                        }
                                    }
                                ]
                            }
                        )
                    else:
                        line_plot_compiler_comparison[name].append(
                            {
                                compiler: {
                                    "real_times": real_times,
                                    "counts": counts
                                }
                            }
                        )

                for key, value in line_plot_compiler_comparison.items():
                    plt.subplots(figsize=(20, 5))
                    for i in range(len(value)):
                        compiler = list(value[i].keys())[0]
                        real_times = value[i][compiler]['real_times']
                        counts = value[i][compiler]['counts']
                        plt.plot(counts, real_times, label=key+'_'+compiler,
                                 marker='o', linestyle='dashed', linewidth=2, markersize=6)

                    plt.legend()
                    plt.ylabel(f'time in ns')
                    plt.xlabel('count')
                    plt.title('compiler comparison')
                    plt.show()

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()