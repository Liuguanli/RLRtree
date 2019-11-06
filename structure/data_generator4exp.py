# !/usr/bin/python
# coding=utf-8

import sys, getopt
import os

import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import configparser
import tensorflow as tf
import time

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def load_csv(fname):
    i = 0
    indexs = []
    latitude = []
    longitude = []
    values = []
    with open(fname, "r") as f:
        for line in f:
            cols = line.split(",")
            latitude.append([float(cols[1])])
            longitude.append([float(cols[0])])
        return latitude, longitude


# def load_csv(fname, label_column):
#     i = 0
#     indexs = []
#     latitude = []
#     longitude = []
#     values = []
#     with open(fname, "r") as f:
#         for line in f:
#             cols = line.split(",")
#             if len(cols) < 2: continue
#             indexs.append([int(cols[label_column].strip())])
#             latitude.append([float(cols[1])])
#             longitude.append([float(cols[0])])
#         return latitude, longitude, indexs

def vis_points(latitudes, longitudes):
    f1 = plt.figure(1)
    plt.scatter(latitudes, longitudes)
    plt.show()


def plotPoints(latitudes, longitudes, indexs):
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111, aspect='equal')
    current_index = 0
    current_latitude = []
    current_longitude = []
    patterns = ['.', '*', 'x', 'o', 'O', '-', '+']
    max_lat = 0
    min_lat = 0
    max_long = 0
    min_long = 0
    # print(indexs)
    for latitude, longitude, index in zip(latitudes, longitudes, indexs):
        if current_index == index[0]:
            current_latitude.append(latitude)
            current_longitude.append(longitude)
        else:
            max_lat = np.max(current_latitude)
            min_lat = np.min(current_latitude)
            max_long = np.max(current_longitude)
            min_long = np.min(current_longitude)

            # p = patches.Rectangle((min_long, min_lat), max_long - min_long, max_lat - min_lat, hatch=patterns[current_index%len(patterns)], fill=False)
            p = patches.Rectangle((min_long, min_lat), max_long - min_long, max_lat - min_lat, fill=False)

            plt.text(min_long, min_lat, current_index, fontsize=10)
            plt.text(max_long, max_lat, current_index, fontsize=10)

            print("index:", current_index, max_lat, min_lat, max_long, min_long)
            ax3.add_patch(p)
            current_index = index[0]
            current_latitude = []
            current_longitude = []

    max_lat = np.max(current_latitude)
    min_lat = np.min(current_latitude)
    max_long = np.max(current_longitude)
    min_long = np.min(current_longitude)

    p = patches.Rectangle((min_long, min_lat), max_long - min_long, max_lat - min_lat, fill=False)

    plt.text(min_long, min_lat, current_index, fontsize=10)
    plt.text(max_long, max_lat, current_index, fontsize=10)

    print("index:", current_index, max_lat, min_lat, max_long, min_long)
    ax3.add_patch(p)

    max_lat = np.max(latitudes)
    min_lat = np.min(latitudes)
    max_long = np.max(longitudes)
    min_long = np.min(longitudes)

    # lat_range = np.arange(min_lat, 0.01, max_lat)
    # long_range = np.arange(min_long, 0.01, max_long)
    # # red dashes, blue squares and green triangles
    # plt.axis([min_long ,max_long, min_lat, max_lat])
    plt.xlim(min_long - 1, max_long + 1)
    plt.ylim(min_lat - 1, max_lat + 1)
    ax3.xaxis.set_major_locator(MultipleLocator(1))
    ax3.yaxis.set_major_locator(MultipleLocator(1))
    # plt.plot(longitude, latitude, '.')

    # rect=patches.Rectangle((200, 600),550,650,linewidth=1,edgecolor='r',facecolor='none')

    plt.show()


def get_skewed_data():
    latitude = []
    longitude = []
    fname = 'd:\\UniMelbourne\\DL_index4R_tree\\dataset\\r_skewed_lati.csv'

    with open(fname, "r") as f:
        for line in f:
            # cols = line.split(",")
            if line.lstrip() == 'x\n':
                continue
            lati = float(line.lstrip())
            if lati < 0 or lati > 10:
                continue
            latitude.append([lati])
        print(len(latitude))

    fname = 'd:\\UniMelbourne\experiment\dataset\\r_skewed_longi.csv'
    with open(fname, "r") as f:
        for line in f:
            if line.lstrip() == 'x\n':
                continue
            longi = float(line.lstrip())
            if longi < 0 or longi > 10:
                continue
            longitude.append([longi])
        print(len(longitude))
    return latitude[0:1000000], longitude[0:1000000]


def get_skeded_Points():
    lati, longi = get_skewed_data()
    result = []
    for i in range(100):
        result.append([])
    for i in range(len(lati)):
        x = longi[i][0]
        y = lati[i][0]
        y_index = int(y)
        x_index = int(x)
        index = x_index + 10 * y_index
        if index < 0 or index > 99:
            print(index)
        result[index].append([x, y])
    for i in range(100):
        with open("../dataset/random_skewed_" + str(i) + "_.csv", "w") as fo:
            for item in result[i]:
                # print(item)
                node_string = str(item[0]) + "," + str(item[1]) + "\n"
                fo.write(node_string)


def get_tf_normalrandomPoints(num, length):
    longitudes = tf.truncated_normal([num, 1], mean=95.0, stddev=2.5, dtype=tf.float32)
    latitudes = tf.truncated_normal([num, 1], mean=45.0, stddev=2.5, dtype=tf.float32)
    with tf.Session() as sees:
        lati = sees.run(latitudes)
        longi = sees.run(longitudes)
        with open("../dataset/8M/random_tf_.csv", "w") as fo:
            result = []
            for i in range(length * length):
                result.append([])
            for i in range(num):
                x = longi[i]
                y = lati[i]

                y_index = int(y - 40)
                x_index = int(x - 90)
                index = x_index + length * y_index
                if index < 0 or index > 99:
                    print(index)
                result[index].append([x[0], y[0], str(i)])
                node_string = str(x[0]) + "," + str(y[0]) + "," + str(i) + "\n"
                fo.write(node_string)
            for i in range(length * length):
                with open("../dataset/8M/random_tf_" + str(i) + "_.csv", "w") as fo:
                    for item in result[i]:
                        # print(item)
                        node_string = str(item[0]) + "," + str(item[1]) + "," + str(item[2]) + "\n"
                        fo.write(node_string)


def get_real_dataset():
    # fname = 'C:\\Users\\LEO\\Dropbox\\dataset\\greenland-latest\\nodes.csv'
    fname = 'D:\\UniMelbourne\\experiment\\dataset\\real_greenland_26_.csv'
    with open(fname, "r") as f:
        latitude = []
        longitude = []
        for line in f:
            cols = line.split(",")
            latitude.append(float(cols[0]))
            longitude.append(float(cols[1]))

        max_lati = max(latitude)
        min_lati = min(latitude)
        max_longi = max(longitude)
        min_longi = min(longitude)
        length = len(latitude)
        latitude_interval = (max_lati - min_lati) / 9
        longitude_interval = (max_longi - min_longi) / 9
        result = []
        # print('latitude_interval', latitude_interval)
        # print('longitude_interval', longitude_interval)
        for i in range(100):
            result.append([])
        for i in range(len(latitude)):
            lati = latitude[i]
            longi = longitude[i]
            x_index = int((longi - min_longi) / longitude_interval)
            y_index = int((lati - min_lati) / latitude_interval)
            result[x_index + y_index * 10].append([longi - min_longi, lati - min_lati])
        for x_range in range(10):
            for y_range in range(10):
                with open("../dataset/real_greenland_26_" + str(x_range + y_range * 10) + "_.csv", "w") as fo:
                    for item in result[x_range + y_range * 10]:
                        node_string = str(item[0]) + "," + str(item[1]) + "\n"
                        fo.write(node_string)


def getUniformPoints(num, filename, dim):
    all_result = []
    for i in range(num):
        node_string = ''
        for j in range(dim):
            val = random.uniform(0, 1)
            node_string = node_string + str(val) + ","
        node_string = node_string + str(i) + "\n"
        all_result.append(node_string)

    while num >= 1000000:
        print(num)
        name = filename % (num, dim)
        all_fo = open(name, "w")
        for i in range(num):
            all_fo.write(all_result[i])
        all_fo.close()
        num = int(num / 2)



def getNormalPoints(num, filename, dim):
    locations_tf = []
    for i in range(dim):
        locations_tf.append(tf.random.truncated_normal([num, 1], mean=0.5, stddev=0.25, dtype=tf.float32))
    with tf.compat.v1.Session() as sees:
        locations = []
        for i in range(dim):
            locations.append(sees.run(locations_tf[i]))
        with open(filename, "w") as fo:
            for i in range(num):
                node_string = ''
                for j in range(dim):
                    node_string = node_string + str(locations[j][i][0]) + ","
                node_string = node_string + str(i) + "\n"
                fo.write(node_string)


def getSkewedPoints(num, a, filename, dim):
    locations_tf = []
    for i in range(dim):
        locations_tf.append(tf.random.truncated_normal([num, 1], mean=0.5, stddev=0.25, dtype=tf.float32))
    with tf.compat.v1.Session() as sees:
        locations = []
        for i in range(dim):
            locations.append(sees.run(locations_tf[i]))


    while num >= 1000000:
        print(num)
        name = filename % (num, a, dim)
        with open(name, "w") as fo:
            for i in range(num):
                node_string = ''
                for j in range(dim - 1):
                    node_string = node_string + str(locations[j][i][0]) + ","
                node_string = node_string + str(locations[dim - 1][i][0] ** a) + "," + str(i) + "\n"
                fo.write(node_string)
        num = int(num / 2)

def parser(argv):
    try:
        opts, args = getopt.getopt(argv, "d:s:n:f:m:")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-d':
            distribution = arg
        elif opt == '-s':
            size = int(arg)
        elif opt == '-n':
            skewness = int(arg)
        elif opt == '-f':
            filename = arg
        elif opt == '-m':
            dim = int(arg)
    return distribution, size, skewness, filename, dim

# python C:\Users\Leo\Dropbox\shared\RLR-trees\codes\python\RLRtree\structure\data_generator.py -d uniform -s 16000000 -n 1 -f D:\datasets\RLRtree\raw\uniform_16000000_1_2_.csv -m 2
if __name__ == '__main__':
    # getUniformRandomPoints(80000, 10)
    # get_tf_normalrandomPoints(8000000, 10)
    distribution, size, skewness, filename, dim = parser(sys.argv[1:])
    print(distribution, size, skewness, filename, dim)
    if distribution == 'normal':
        filename = "D:\\datasets\\RLRtree\\raw\\normal_%d_1_%d_.csv"
        getNormalPoints(size, filename, dim)
    elif distribution == 'uniform':
        filename = "D:\\datasets\\RLRtree\\raw\\normal_%d_1_%d_.csv"
        getUniformPoints(size, filename, dim)
    elif distribution == 'skewed':
        filename = "D:\\datasets\\RLRtree\\raw\\normal_%d_%d_%d_.csv"
        getSkewedPoints(size, skewness, filename, dim)
