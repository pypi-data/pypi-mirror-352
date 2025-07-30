from ...interface import IPacker


class ReadPeriodsParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [list(self._obj.InstrumentID), self._obj.DataList]

    def tuple_to_obj(self, t):
        if len(t) >= 2:
            self._obj.InstrumentID = t[0]
            self._obj.DataList = t[1]

            return True
        return False
