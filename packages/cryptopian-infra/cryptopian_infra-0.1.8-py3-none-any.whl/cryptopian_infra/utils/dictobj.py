class DictObj:
    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return repr(self)
