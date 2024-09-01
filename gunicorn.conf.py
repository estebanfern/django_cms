import os

bind = "0.0.0.0:8000"
workers = 3
timeout = 120

#Logs
accesslog = os.getenv('CMS_LOG_FILENAME', '/app/logs/app.log')
errorlog = os.getenv('CMS_LOG_FILENAME', '/app/logs/app.log')
loglevel = os.getenv('CMS_LOG_LEVEL', 'error')
