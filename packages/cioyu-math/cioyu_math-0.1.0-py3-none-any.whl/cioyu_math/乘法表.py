def 乘法表(a):
    for i in range(1,a+1):
        for j in range(1,i+1):
            print(f"{j}*{i}={i*j}",end="\t")
        print("\n")
