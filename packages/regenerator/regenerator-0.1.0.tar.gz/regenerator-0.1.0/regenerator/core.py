
from itertools import chain

class Generator:
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self.copy()

    def __list__(self):
        return list(self.copy())

    def copy(self):
        generator1 = empty_generator()
        generator2 = empty_generator()
        for item in self.generator:
            generator1 = chain(generator1, [item])
            generator2 = chain(generator2, [item])
        self.generator = generator1
        return generator2
 


def empty_generator():
    return
    yield


if __name__ == "__main__":
    generator = Generator((x for x in range(5)))
    for item in generator.copy():
        print(item)
