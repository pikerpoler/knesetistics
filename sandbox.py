import numpy as np
import time

def main():
    all = {}
    for i in range(1000):
        start = time.time()
        tmp = np.full((120, 2), -1, dtype=int)
        all[i] = tmp
        print(f'Iteration {i} took {time.time() - start} seconds')

    print('Done, saving...')
    start = time.time()
    np.save('test.npy', all)
    print(f'Saving took {time.time() - start} seconds')


if __name__ == '__main__':
    main()


