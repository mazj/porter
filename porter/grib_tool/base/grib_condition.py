# coding: utf-8


class GribCondition(object):
    def __init__(self, name, value_string):
        self.name = name
        self.values = value_string.split('|')
        # check values
        if self.values[0].isdigit():
            self.value_type = float
            self.values = [float(v) for v in self.values]
        else:
            self.values = [v.encode('utf-8') for v in self.values]
            self.value_type = str

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def is_fit(self, grib_message):
        if self.value_type == float:
            value = grib_message.getDouble(self.name)
        else:
            value = grib_message.getString(self.name)
        return value in self.values
