from __future__ import print_function
import sys
import os
from pprint import pprint
import sys, getopt

# print = pprint

import matplotlib.pyplot as plt
import platform
from pylab import *

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

sysstr = platform.system()
if sysstr == "Windows":
    # prefix = "C:\\Users\\Leo\\Dropbox\\shared\\RL R-trees\\figures\\"
    prefix = "C:\\Users\\Leo\\Dropbox\\figures\\RLRtrees\\"
    figure_name_template_window = prefix + '%s_window_%d_dim_%d_%s'
    figure_name_template_dataset = prefix + '%s_dataset_%d_dim_%d_%s'
else:
    # prefix = "/Users/guanli/Dropbox/shared/RL\ R-trees/figures/"
    prefix = "/Users/guanli/Dropbox/figures/RLRtrees/"
    figure_name_template_window = prefix + '%s_window_%d_dim_%d_%s'
    figure_name_template_dataset = prefix + '%s_dataset_%d_dim_%d_%s'


def get_file_dir():
    sysstr = platform.system()
    if sysstr == "Windows":
        file_dir_window = "C:\\Users\\Leo\\Dropbox\\records\\RLRtree\\window\\"
        separator = "\\"
    elif sysstr == "Darwin":
        file_dir_window = "/Users/guanli/Dropbox/records/RLRtree/window/"
        separator = '/'
    return file_dir_window, separator


class Record:
    def __init__(self):
        self.name = ''
        self.algorithm = ''
        self.distribution = ''
        self.dataset_size = 0
        self.window = 0
        self.time = 0
        self.page_access = 0
        self.skewness = 0
        self.dim = 0

    def get_algorithm(self):
        return self.name + "_" + self.algorithm

    def __str__(self):
        return self.name + ' ' + self.distribution + ' ' + self.dataset_size + ' ' + self.skewness + ' ' \
               + self.dim + ' ' + self.algorithm + ' ' + self.window + ' ' + self.time + ' ' + self.page_access


markers = ['o', '*', 'v', 'x', '+', 's', '1', 'P']
linestyles = ['-.', '--', '-', ':', '-.', '--', '-', ':']
labels = ['DQN-ZRR', 'DQN-HRR', 'DDPG-ZRR', 'DDPG-HRR', 'ZRR', 'HRR', 'Random-ZRR', 'Random-HRR']
distributions = ['uniform', 'normal', 'skewed']
windows = [156, 625, 2500, 10000, 40000]
datasizes = [10000, 20000, 40000, 80000, 160000]
algorithms = {
    'Z_DQN': 'DQN-ZRR',
    'H_DQN': 'DQN-HRR',
    'Z_DDPG': 'DDPG-ZRR',
    'H_DDPG': 'DDPG-HRR',
    'Z_null': 'ZRR',
    'H_null': 'HRR',
    'Z_random': 'Random-ZRR',
    'H_random': 'Random-HRR',
}
types = ['time', 'pageaccess']
dims = [2, 3]
lw = 2  # linewidth=3
ms = 15  # markersize=15
fs = 15  # font size


def get_window_exp_info():
    file_dir_window, separator = get_file_dir()
    file_list = os.listdir(file_dir_window)  # 列出文件夹下所有的目录与文件
    record_list = []
    #     algorithms = {'model':'RL-ZRR','RStarTree':'RStar', 'ZRtreeOld':'ZR', 'ZRtree':'ZRR'}
    for i in range(0, len(file_list)):
        file_path = os.path.join(file_dir_window, file_list[i])
        paths = file_path.split(separator)
        file_name = paths[len(paths) - 1]
        file_name = file_name.split('.')[0]
        names = file_name.split('_')
        if len(names) < 3:
            continue
        exp_record = Record()
        exp_record.name = names[0]
        exp_record.distribution = names[1]
        exp_record.dataset_size = int(names[2])
        exp_record.skewness = int(names[3])
        exp_record.dim = int(names[4])
        exp_record.algorithm = names[5]
        exp_record.window = int(names[6])
        file = open(file_path)
        for line in file.readlines():
            line = line.strip('\n')
            if 'time' in line:
                exp_record.time = int(line.split('=')[1]) / 1000
            if 'pageaccess' in line:
                exp_record.page_access = int(line.split('=')[1])
        record_list.append(exp_record)
    return record_list


# names = ["0.06", "0.25","1","4","16"],xlabel="Query window size(%)",ylabel=u"Time ($10^-3$ms)")
def draw(xlabels, ys, xlabel, ylabel, name, type='time'):
    x = range(len(xlabels))
    for index, key in enumerate(ys.keys()):
        if type == 'time':
            plt.plot(x, [item.time for item in ys[key]], marker=markers[index], color='black',
                     linestyle=linestyles[index], mfc='w',
                     label=labels[index], linewidth=lw, markersize=ms)
        elif type == 'pageaccess':
            plt.plot(x, [item.page_access for item in ys[key]], marker=markers[index], color='black',
                     linestyle=linestyles[index],
                     mfc='w', label=labels[index], linewidth=lw, markersize=ms)
    plt.legend(fontsize=fs)  # 让图例生效

    plt.xticks(fontsize=fs)
    plt.yticks(fontsize=fs)
    #     plt.title(title,fontsize=15) #标题
    ax = plt.gca()

    ax.set_xlabel(xlabel=xlabel, fontsize=fs)
    ax.set_ylabel(ylabel=ylabel, fontsize=fs)

    plt.xticks(x, xlabels, rotation=0)
    plt.margins(0.1)
    plt.subplots_adjust(bottom=0.15)

    plt.savefig(name + ".png", format='png', bbox_inches='tight')
    plt.savefig(name + ".eps", format='eps', bbox_inches='tight')

    # plt.show()
    clf()  # 清图。
    cla()  # 清坐标轴。
    close()  # 关窗口
    # plt.close(0)


record_list = get_window_exp_info()


def config_data_vary_window(dataset_size=160000, dim=2, distribution='uniform', type='time'):
    print(dataset_size, dim, distribution, type)
    # make template
    template = {}
    for item in labels:
        template[item] = []
    for record in record_list:
        if distribution == 'skewed' and record.skewness != 9:
            continue
        if record.distribution == distribution:
            if record.dim == dim:
                if record.dataset_size == dataset_size:
                    template[algorithms[record.get_algorithm()]].append(record)
                    # tag dataset_size=160000, vaye

    for k, value in template.items():
        temp = template[k]
        temp.sort(key=lambda x: x.dataset_size)
        template[k] = temp

    xlabels = ['0.0156', '0.0625', '0.25', '1', '4']
    if type == 'time':
        draw(xlabels, template, "Query window size(%)", "Time($(10^-3)$ms)",
             (figure_name_template_dataset % (distribution, dataset_size, dim, type)), type=type)
    else:
        draw(xlabels, template, "Query window size(%)", "Page Access",
             (figure_name_template_dataset % (distribution, dataset_size, dim, type)), type=type)


def config_data_vary_dataset(window=10000, dim=2, distribution='uniform', type='time'):
    # make template
    print(window, dim, distribution, type)
    template = {}
    for item in labels:
        template[item] = []
    for record in record_list:
        if distribution == 'skewed' and record.skewness != 9:
            continue
        if record.distribution == distribution:
            if record.dim == dim:
                if record.window == window:
                    template[algorithms[record.get_algorithm()]].append(record)

    for k, value in template.items():
        temp = template[k]
        temp.sort(key=lambda x: x.window)
        template[k] = temp

    xlabels = ['1', '2', '4', '8', '16']
    if type == 'time':
        draw(xlabels, template, "Data set size $(10^4)$", "Time($(10^-3)$ms)",
             (figure_name_template_window % (distribution, window, dim, type)), type=type)
    else:
        draw(xlabels, template, "Data set size $(10^4)$", "Page Access",
             (figure_name_template_window % (distribution, window, dim, type)), type=type)

if __name__ == '__main__':
    for distribution in distributions:
        for type in types:
            for dim in dims:
                for window in windows:
                    config_data_vary_dataset(window=window, dim=dim, distribution=distribution, type=type)
                for datasize in datasizes:
                    config_data_vary_window(dataset_size=datasize, dim=dim, distribution=distribution, type=type)