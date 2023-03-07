#!/bin/python

import os
import yaml
from logger import Logger
from pid import PID, HeatSource, Fan

logger = Logger()

# Load config and run!
config_file = os.getenv('CONFIG_FILE', './config.yaml')

with open(config_file, 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

    # PID setup
    pid_config = config['pid']
    sample_interval = pid_config['sample_interval'] / 1.0
    pid = PID(sample_interval,
              pid_config['Kd'],
              pid_config['Ki'],
              pid_config['Kd'],
              pid_config['min_output'],
              pid_config['max_output'])

    # Heat source config
    heat_sources_config = config['heat_sources']
    heat_sources = list(map(lambda config: HeatSource(config['name'],
                                                      config['set_point'],
                                                      config['temp_cmd']),
                            heat_sources_config))

    # Fan config
    fan_config = config['fans'][0]
    fan = Fan(fan_config['min_rpm'],
              fan_config['max_rpm'],
              fan_config['set_cmd'],
              fan_config['duty_cmd'])

    try:
        pid.run_loop(heat_sources, fan)
    except BaseException as err:
        logger.error("Exception caught, setting default temp", err)
        fan.set_fan_duty(0)
        exit(1)
