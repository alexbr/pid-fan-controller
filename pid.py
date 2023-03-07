import math
import subprocess
import time
from logger import Logger
from utils import clamp

logger = Logger()


class Fan():
    """ Simple class representing a fan. """

    def __init__(self,
                 min_rpm,
                 max_rpm,
                 set_cmd,
                 get_cmd):
        assert min_rpm >= 0
        assert max_rpm >= 0
        assert max_rpm >= min_rpm

        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.set_cmd = set_cmd
        self.get_cmd = get_cmd

    def duty_to_rpm(self, percent):
        range = self.max_rpm - self.min_rpm
        return math.floor(self.min_rpm +
                          (range * percent / 100))

    def get_current_duty(self):
        fan_duty = int(subprocess.run(self.get_cmd,
                                      text=True,
                                      shell=True,
                                      check=True,
                                      executable='bash',
                                      capture_output=True).stdout)

        logger.debug(f'fan duty: {fan_duty}%')
        fan_rpm = self.duty_to_rpm(fan_duty)
        logger.debug(f'fan speed: {fan_rpm} RPM')

        return fan_duty

    def set_fan_duty(self, percent):
        duty_hex = f'0x{percent:02x}'
        logger.debug(f'set fan duty: {duty_hex}')

        cmd = self.set_cmd.format(duty_hex=duty_hex)
        logger.debug(f'set cmd: {cmd}')
        subprocess.run(cmd,
                       text=True,
                       shell=True,
                       check=True,
                       executable='bash',
                       capture_output=True).stdout


class HeatSource:
    """ A heat source and its desired set point. """

    def __init__(self, name, set_point, temp_cmd):
        self.name = name
        self.set_point = set_point
        self.temp_cmd = temp_cmd

    def get_temp(self):
        logger.debug(f'running: {self.temp_cmd}')
        result = subprocess.run(self.temp_cmd,
                                text=True,
                                shell=True,
                                check=True,
                                executable='bash',
                                capture_output=True)

        return float(result.stdout)


class PID:
    """ A simple PID controller. """

    def __init__(
            self,
            sample_interval,
            Kp,
            Ki,
            Kd,
            output_min,
            output_max):
        assert sample_interval > 0
        assert output_min >= 0
        assert output_max >= 0
        assert output_max >= output_min

        self.sample_interval = sample_interval
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.output_min = output_min
        self.output_max = output_max

        self.integral = 0

        self.previous_error = None
        self.last_run_time = None

    def compute_output(self, input, set_point):
        now = time.monotonic()
        dt = (now - self.last_run_time
              if self.last_run_time is not None else 1e-16)
        error = input - set_point
        logger.debug(f'error: {error}')

        proportional = self.Kp * error
        integral = self.integral + self.Ki * error * dt
        integral_clamped = clamp(integral, self.output_min, self.output_max)
        error_diff = (error - self.previous_error if self.previous_error is not
                      None else 0)
        derivative = self.Kd * error_diff / dt
        logger.debug(
            f'P: {proportional}, I [clamped]: {integral} [{integral_clamped}],'
            ' D: {derivative}')

        output = proportional + integral_clamped + derivative
        output_clamped = clamp(output, self.output_min, self.output_max)
        logger.debug(f'output [clamped]: {output} [{output_clamped}]')

        self.integral = integral_clamped
        self.last_run_time = now
        self.previous_error = error

        return output_clamped

    def run_loop(self, heat_sources: list[HeatSource], fan: Fan):
        while True:
            fan_duty = fan.get_current_duty()
            logger.debug(f'fan duty: {fan_duty}%')

            total_temp = 0
            total_set_point = 0

            for heat_source in heat_sources:
                temp = heat_source.get_temp()
                set_point = heat_source.set_point
                logger.info(
                    f'{heat_source.name} temp: {temp}, target: {set_point}')
                total_temp += temp
                total_set_point += set_point

            # Average the obeserved temp and set points
            avg_temp = total_temp / len(heat_sources)
            avg_set_points = total_set_point / len(heat_sources)

            output = self.compute_output(avg_temp, avg_set_points)

            output_duty = math.floor(100 * output)
            logger.debug(f'target duty: {output_duty}%')

            rpm = fan.duty_to_rpm(output_duty)
            logger.info(f'target RPM: {rpm} RPM')

            fan.set_fan_duty(output_duty)

            time.sleep(self.sample_interval)
