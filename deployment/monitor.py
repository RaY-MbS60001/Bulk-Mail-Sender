import psutil
import requests
import time
import os
from datetime import datetime

def check_system_resources():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    return {
        'cpu': cpu,
        'memory': memory,
        'disk': disk,
        'timestamp': datetime.now().isoformat()
    }

def check_application_status():
    try:
        response = requests.get('http://localhost:8000/health')
        return response.status_code == 200
    except:
        return False

def log_metrics(metrics):
    with open('app_metrics.log', 'a') as f:
        f.write(f"{metrics['timestamp']}: CPU={metrics['cpu']}%, "
                f"Memory={metrics['memory']}%, Disk={metrics['disk']}%\n")

def main():
    while True:
        metrics = check_system_resources()
        app_status = check_application_status()
        
        log_metrics(metrics)
        
        # Alert if resources are critical
        if metrics['cpu'] > 90 or metrics['memory'] > 90 or metrics['disk'] > 90:
            # Implement your alerting mechanism here
            print("Resource usage critical!")
        
        if not app_status:
            print("Application is not responding!")
        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()