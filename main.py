# import zephyros1938.tsapp as tsapp;
# import zephyros1938.tsappMod as tsappMod;
import threading as th
from zephyros1938.overrides import *


class Main(metaclass=AutoCastMeta):
    t: Int16 = Int16.MAX_VALUE

    def __init__(self, *args, **kwargs):
        print(self.t + 1)
        print(self.t.bit_length())
        print(Int16.MAX_VALUE)


if __name__ == "__main__":
    Main()
