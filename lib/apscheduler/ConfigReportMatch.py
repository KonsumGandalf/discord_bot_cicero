class ConfigReportMatch:
    """App configuration."""
    JOBS = [
        {
            "id": "job1",
            "func": "jobs:job1",
            "args": (1, 2),
            "trigger": "interval",
            "seconds": 10,
        }
    ]
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/Berlin"

"""def job1(var_one, var_two):
    print(str(var_one) + " " + str(var_two))
    https://stackoverflow.com/questions/69776414/pytzusagewarning-the-zone-attribute-is-specific-to-pytzs-interface-please-mig
    
    
from flask import Flask
from flask_apscheduler import APScheduler
from lib.apscheduler.ConfigReportMatch import ConfigReportMatch
    """