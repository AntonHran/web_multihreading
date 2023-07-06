from multiprocessing import Process, Pool, current_process, cpu_count
from time import time, sleep
import logging


logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

cores = cpu_count()


def factorize(*numbers) -> list:
    total_list = []
    for number in numbers:
        current_list = []
        for i in range(1, number+1):
            if number % i == 0:
                current_list.append(i)
        total_list.append(current_list)
    return total_list


def factorize_number(num: int) -> list:
    current_list: list = []
    for i in range(1, num+1):
        if num % i == 0:
            current_list.append(i)
    logger.debug(f'process: {current_process().name}, number: {num}, res: {current_list}')
    return current_list


def factorize_process(*numbers: list | int) -> None:
    process_list: list = []
    for number in numbers:
        process: Process = Process(target=factorize_number, args=(number, ))
        process.start()
        process_list.append(process)
    [pr.join() for pr in process_list]


if __name__ == '__main__':
    start = time()
    numbers_: tuple = (128128, 255255, 20000000, 20651000)
    factorize_process(*numbers_)
    finish = time()
    print(f'Time of calculations with processes: {finish - start} sec.')
    sleep(1)

    start = time()
    with Pool(processes=cores) as pool:
        results = list(pool.map(factorize_number, (128128, 255255, 20000000, 20651000)))
    logging.debug(results)
    finish = time()
    print(f'Time of calculations with pool of processes: {finish - start} sec.')
    sleep(1)

    start = time()
    a, b, c, d = factorize(128128, 255255, 20000000, 20651000)
    finish = time()
    print(f'Time of synchron calculations: {finish - start} sec.')

# Бо при тих значеннях що були запропоновані у завданні ми не побачимо ніякого приросту у швидкості обчислень!!!
# Тим паче для таких незначних чисел, де синхронна програма справляється краще за багатопроцесорну
# А так швидкість зростає майже у два рази

    assert a == [1, 2, 4, 7, 8, 11, 13, 14, 16, 22, 26, 28, 32, 44, 52, 56, 64, 77, 88, 91, 104,
                 112, 128, 143, 154, 176, 182, 208, 224, 286, 308, 352, 364, 416, 448, 572, 616,
                 704, 728, 832, 896, 1001, 1144, 1232, 1408, 1456, 1664, 2002, 2288, 2464, 2912,
                 4004, 4576, 4928, 5824, 8008, 9152, 9856, 11648, 16016, 18304, 32032, 64064, 128128]
    assert b == [1, 3, 5, 7, 11, 13, 15, 17, 21, 33, 35, 39, 51, 55, 65, 77, 85, 91, 105, 119,
                 143, 165, 187, 195, 221, 231, 255, 273, 357, 385, 429, 455, 561, 595, 663, 715,
                 935, 1001, 1105, 1155, 1309, 1365, 1547, 1785, 2145, 2431, 2805, 3003, 3315,
                 3927, 4641, 5005, 6545, 7293, 7735, 12155, 15015, 17017, 19635, 23205, 36465,
                 51051, 85085, 255255]
    assert c == [1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 80, 100, 125, 128, 160, 200, 250,
                 256, 320, 400, 500, 625, 640, 800, 1000, 1250, 1280, 1600, 2000, 2500, 3125,
                 3200, 4000, 5000, 6250, 6400, 8000, 10000, 12500, 15625, 16000, 20000, 25000,
                 31250, 32000, 40000, 50000, 62500, 78125, 80000, 100000, 125000, 156250, 160000,
                 200000, 250000, 312500, 400000, 500000, 625000, 800000, 1000000, 1250000, 2000000,
                 2500000, 4000000, 5000000, 10000000, 20000000]
    assert d == [1, 2, 4, 5, 8, 10, 20, 25, 40, 50, 100, 107, 125, 193, 200, 214, 250, 386, 428,
                 500, 535, 772, 856, 965, 1000, 1070, 1544, 1930, 2140, 2675, 3860, 4280, 4825,
                 5350, 7720, 9650, 10700, 13375, 19300, 20651, 21400, 24125, 26750, 38600, 41302,
                 48250, 53500, 82604, 96500, 103255, 107000, 165208, 193000, 206510, 413020, 516275,
                 826040, 1032550, 2065100, 2581375, 4130200, 5162750, 10325500, 20651000]
