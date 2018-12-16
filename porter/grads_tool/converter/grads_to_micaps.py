"""
GrADS data to micaps data converter.
"""

from __future__ import print_function, absolute_import
import struct
import os

from porter.grads_parser.grads_ctl_parser import GradsCtl, GradsCtlParser
from porter.grads_parser.grads_data_parser import GradsDataParser


class GradsToMicaps(object):
    """
    Convert GrADS data to micaps data
    """

    def __init__(self, grads_ctl=GradsCtl()):
        self.grads_ctl = grads_ctl
        self.grads_ctl_parser = GradsCtlParser(grads_ctl)
        self.grads_data_parser = GradsDataParser(grads_ctl)

    def set_grads_ctl_path(self, ctl_path):
        self.grads_ctl_parser.parse(ctl_path)

    def convert(self, a_config_record):
        a_name = a_config_record['name']
        a_level = a_config_record.get('level', '0')
        a_level_type = a_config_record.get('level_type', 'multi')
        an_output_dir = a_config_record.get('output_dir', '.')
        a_time_index = a_config_record.get('time_index', 0)
        a_value_func = eval("lambda x: "+a_config_record.get('value', 'x'))
        record_target_type = a_config_record.get('target_type','')

        if record_target_type == "micaps.4":
            self.convert_record_to_type_4(a_name,
                                          a_level,
                                          a_level_type,
                                          a_time_index,
                                          an_output_dir,
                                          a_value_func)
        else:
            print("TYPE: {record_target_type} has not implemented!".format(record_target_type=record_target_type))

    def convert_record_to_type_4(self, name,
                                 level=0.0,
                                 level_type='multi',
                                 time_index=0,
                                 output_dir=".",
                                 value_func=lambda x: x):
        """
        convert a record with name, level and time index in GrADS data file.
        """

        micaps_data_type = "4"

        a_forecast_hour = self.grads_ctl.forecast_time.seconds / 3600
        comment = name + '_'+self.grads_ctl.start_time.strftime("%Y%m%d%H") + "_%03d" % a_forecast_hour

        output_file_name = self.grads_ctl.start_time.strftime("%Y%m%d%H") + ".%03d" % a_forecast_hour
        output_file_dir = output_dir + os.sep + name + "_" + micaps_data_type
        if not level_type == 'single':
            output_file_dir += os.sep + str(int(level))
            a_level = float(level)
        else:
            a_level = 0

        record_index = self.grads_data_parser.get_record_index(name, level, level_type, time_index)
        offset = self.grads_data_parser.get_record_offset_by_record_index(record_index)

        with open(self.grads_ctl.dset, 'rb') as data_file:
            if 'sequential' in self.grads_ctl.options:
                offset += 4
            x_count = self.grads_ctl.xdef['count']
            y_count = self.grads_ctl.ydef['count']

            if self.grads_ctl.data_endian == 'big':
                data_format = '>f'
            elif self.grads_ctl.data_endian == 'little':
                data_format = '<f'
            else:
                print("Data endian is not found. Use local endian to unpack values.")
                if sys.byteorder == "big":
                    data_format = '>f'
                else:
                    data_format = '<f'

            # load data from file
            data_file.seek(offset)

            if hasattr(self.grads_ctl, "yrev") and self.grads_ctl.yrev is True:
                var_yrev = True
            else:
                var_yrev = False

            var_list = [struct.unpack(data_format, data_file.read(4))[0] for i in range(0, y_count*x_count)]

            # process yrev
            if var_yrev:
                new_var_list = list()
                for i in range(0, y_count):
                    new_var_list.extend(var_list[(y_count-1-i)*x_count:(y_count-i)*x_count])
                del var_list
                var_list = new_var_list

            if not os.path.isdir(output_file_dir):
                os.makedirs(output_file_dir)

            with open(output_file_dir + os.sep + output_file_name, 'w') as output_file:
                output_file.write("diamond ")
                output_file.write("%s " % micaps_data_type)
                output_file.write("%s \n" % comment)
                output_file.write(str(self.grads_ctl.start_time.year)[-2:] + " ")
                output_file.write("%02d " % self.grads_ctl.start_time.month)
                output_file.write("%02d " % self.grads_ctl.start_time.day)
                output_file.write("%02d " % self.grads_ctl.start_time.hour)
                output_file.write("%03d " % a_forecast_hour)
                output_file.write("%d " % a_level)
                output_file.write("%.2f " % self.grads_ctl.xdef['step'])
                output_file.write("%.2f " % self.grads_ctl.ydef['step'])
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.xdef['values'][-1])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][0])
                output_file.write("%.2f " % self.grads_ctl.ydef['values'][-1])
                output_file.write("%d " % x_count)
                output_file.write("%d " % y_count)
                output_file.write("%.2f " % 4.00)
                output_file.write("%.2f " % value_func(min(var_list)))
                output_file.write("%.2f " % value_func(max(var_list)))
                output_file.write("%d " % 2)
                output_file.write("%.2f " % 0.00)
                output_file.write("\n")

                var_list_str = ["%.2f" % (value_func(a_var)) for a_var in var_list]
                output_file.write(" ".join(var_list_str))


if __name__ == "__main__":
    import getopt
    import sys
    optlist, args = getopt.getopt(sys.argv[1:], 'h')
    if len(args) < 2:
        print("""Usage: %s ctl_file_path output_dir
        """ % os.path.basename(sys.argv[0]))
        sys.exit()

    grads_2_micaps = GradsToMicaps()
    grads_2_micaps.set_grads_ctl_path(args[0])
    grads_2_micaps.convert_record_to_type_4("t", level=850.0, output_dir=args[1], value_func=lambda x: x-273.16)