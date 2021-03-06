# coding=utf-8
import os
import time
import datetime
import logging

import yaml

from porter.grads_parser.grads_ctl_parser import GradsCtl, GradsCtlParser
from porter.grads_tool.converter.grads_to_micaps import GradsToMicaps


logger = logging.getLogger(__name__)


class GradsConvert(object):
    def __init__(self):
        pass

    def print_record_info(self, record):
        logger.info("[{class_name}] Converting {name} with level {level} to {target_type}...".format(
            class_name=self.__class__.__name__,
            name=record["name"],
            level=record["level"],
            target_type=record["target_type"]
        ), end='')

    def convert(self, config_file_path):
        with open(config_file_path) as config_file:
            config_object = yaml.load(config_file)

            ctl_file_path = os.path.abspath(config_object['ctl'])
            grads_ctl = GradsCtl()

            # output parser
            output_dir = os.path.abspath(config_object['output_dir'])

            # time parser
            start_time_str = config_object.get('start_time', '')
            forecast_time_str = config_object.get('forecast_time', '')
            if start_time_str != "":
                str_length = len(start_time_str)
                if str_length == 10:
                    start_time = datetime.datetime.strptime(start_time_str, "%Y%m%d%H")
                    grads_ctl.start_time = start_time
                else:
                    logger.error("parser start_time has error: {start_time}".format(start_time=start_time_str))

            if forecast_time_str != "":
                # TODO (windroc, 2014.08.18): use format:
                #   XXXhXXmXXs
                if len(forecast_time_str) == 3:
                    forecast_time = datetime.timedelta(hours=int(forecast_time_str))
                    grads_ctl.forecast_time = forecast_time

            # ctl parser
            grads_ctl_parser = GradsCtlParser(grads_ctl)
            grads_ctl = grads_ctl_parser.parse(ctl_file_path)

            # record parser
            records = config_object['records']
            for a_record in records:
                target_type = a_record["target_type"]

                self.print_record_info(a_record)

                def convert_a_record():
                    if target_type.startswith("micaps"):
                        grads_to_micaps = GradsToMicaps(grads_ctl)
                        a_record['output_dir'] = output_dir
                        grads_to_micaps.convert(a_record)
                    else:
                        raise NotImplemented("Not implemented for %s" % target_type)

                time1 = time.clock()
                convert_a_record()
                time2 = time.clock()
                logger.info("{time_cost:.2f}".format(time_cost=time2 - time1))
