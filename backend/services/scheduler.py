import schedule
import time
from services.monitoring_service import MonitoringService
from services.config_service import ConfigService

def collect_data_job():
    config = ConfigService.get_monitoring_config()
    schedule.every(config.interval).seconds.do(MonitoringService.collect_and_store_ont_data)

def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)