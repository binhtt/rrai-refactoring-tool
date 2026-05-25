import time


def scalability_test():

    start = time.time()

    for _ in range(100000):
        pass

    end = time.time()

    print("Execution time:", end - start)


if __name__ == "__main__":

    scalability_test()
