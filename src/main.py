import timeit


class RandomClass:
    is_random = True

    def function(self):
        return 1


def test():
    something = RandomClass()

    for i in range(100):
        if something.is_random:
            continue


if __name__ == "__main__":
    print(timeit.timeit("test()", setup="from __main__ import test", number=100))

