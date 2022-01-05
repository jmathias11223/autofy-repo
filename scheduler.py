# This program runs the spotify new music application
# every Friday right after music drops

import os
import schedule
import time


def run():
    os.system('python3 driver.py')
    return

schedule.every().friday.at("10:35").do(run)

while True:
    schedule.run_pending()
    time.sleep(60)
