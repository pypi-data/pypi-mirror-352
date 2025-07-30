def 数组排序(b,t):
    if t == 0:
        c = b.copy()
        length = len(c)
        for i in range(length):
            min_index = i
            for j in range(i + 1, length):
                if c[j] < c[min_index]:
                    min_index = j
            c[i], c[min_index] = c[min_index], c[i]
        return c
    else:
        c = b.copy()
        length = len(c)
        for i in range(length):
            min_index = i
            for j in range(i + 1, length):
                if c[j] > c[min_index]:
                    min_index = j
            c[i], c[min_index] = c[min_index], c[i]
        return c