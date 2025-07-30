def 乘法表(a):
    for i in range(1,a+1):
        for j in range(1,i+1):
            print(f"{j}*{i}={i*j}",end="\t")
        print("\n")

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


f = [3,9,1,0]
print(数组排序(f,1))