import math
import multiprocessing as mp
import time

result_1 = []
result_2 = []
result_3 = []


def make_calc_1(numbers):
    for number in numbers:
        result_1.append(math.sqrt(number ** 3))


def make_calc_2(numbers):
    for number in numbers:
        result_2.append(math.sqrt(number ** 4))


def make_calc_3(numbers):
    for number in numbers:
        result_3.append(math.sqrt(number ** 5))


if __name__ == '__main__':
    number_list = list(range(20000000))

    p1 = mp.Process(target=make_calc_1, args=(number_list, ))
    p2 = mp.Process(target=make_calc_2, args=(number_list,))
    p3 = mp.Process(target=make_calc_3, args=(number_list,))

    start = time.time()

    p1.start()

    p2.start()

    p3.start()
    p1.join()
    p2.join()
    p3.join()

    finish = time.time()

    print(finish - start)

    # time.sleep(1)

    start = time.time()
    make_calc_1(number_list)
    make_calc_2(number_list)
    make_calc_3(number_list)
    finish = time.time()
    print(finish - start)
