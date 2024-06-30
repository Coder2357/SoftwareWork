from flask import Flask, render_template, request
import threading
import os
import time

app = Flask(__name__)
cpu_test_thread = None
memory_test_thread = None
stop_threads = False

def cpu_stress_test():
    while not stop_threads:
        _ = 0
        while _ < 10**7:
            _ += 1

def memory_stress_test():
    a = []
    while not stop_threads:
        a.extend([0] * 10**6)
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_cpu_test', methods=['POST'])
def start_cpu_test():
    global cpu_test_thread, stop_threads
    stop_threads = False
    if cpu_test_thread is None or not cpu_test_thread.is_alive():
        cpu_test_thread = threading.Thread(target=cpu_stress_test)
        cpu_test_thread.start()
    return 'CPU stress test started'

@app.route('/stop_cpu_test', methods=['POST'])
def stop_cpu_test():
    global stop_threads
    stop_threads = True
    return 'CPU stress test stopped'

@app.route('/start_memory_test', methods=['POST'])
def start_memory_test():
    global memory_test_thread, stop_threads
    stop_threads = False
    if memory_test_thread is None or not memory_test_thread.is_alive():
        memory_test_thread = threading.Thread(target=memory_stress_test)
        memory_test_thread.start()
    return 'Memory stress test started'

@app.route('/stop_memory_test', methods=['POST'])
def stop_memory_test():
    global stop_threads
    stop_threads = True
    return 'Memory stress test stopped'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
