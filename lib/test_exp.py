test = str([sec for sec in range(0, 60, 10)])[1:-1]

input_str = '5 *5*   12'
arr_int = [int(ele) for ele in input_str.replace('*', '').split(' ')]
print(arr_int)


if __name__ == '__main__':
    pass