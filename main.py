from io import BytesIO
from flask import Flask, send_file, render_template, make_response, request
import matplotlib
import matplotlib.pyplot as plt
import psutil
from functools import wraps, update_wrapper
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
matplotlib.use('Agg')

date = []
cpu = []
memory = []

graphs = [['cpu', 1]]
triggers = []

def cron():
    now_date = datetime.now().strftime("%H:%M:%S")
    date.append(now_date)

    now_cpu = psutil.cpu_percent()
    cpu.append(now_cpu)

    now_mem = psutil.virtual_memory().percent
    memory.append(now_mem)

    for trigger in triggers:
        if trigger[1] == 'cpu' and now_cpu >= trigger[2]:
            print('CPU 사용량이 너무 높습니다. 프로세스를 확인해주세요.')
        if trigger[1] == 'memory' and now_mem >= trigger[2]:
            print('Memory 사용량이 너무 높습니다. 프로세스를 확인해주세요.')

scheduler = BackgroundScheduler()
scheduler.add_job(cron, 'interval', minutes=1, next_run_time=datetime.now())
scheduler.start()

def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response      
  return update_wrapper(no_cache, view)

@app.route("/")
@nocache
def home():
    return render_template("index.html", graphs=graphs, triggers=triggers)

@app.route("/monitor", methods=['POST'])
@nocache
def monitor():
    body = request.get_json()
    types = body["types"]
    periods = body["periods"]

    plt.figure(figsize=(12, 5))

    graphs.clear()
    cont = '5' in periods
    for stype,period in zip(types, periods):
        nperiod = int(period)
        graphs.append([stype, nperiod])
        adate = date[::nperiod]
        limit = 10
        if stype == 'cpu':
            acpu = cpu[::nperiod]
            if cont and nperiod == 5: limit = 2
            plt.plot(adate[-limit:], acpu[-limit:], 'bo-', label="CPU Utilization")
            for ndate, ncpu in zip(adate, acpu):
                plt.annotate(str(ncpu), (ndate, ncpu), textcoords="offset points", xytext=(0,10), ha='center')
        if stype == 'memory':
            amem = memory[::nperiod]
            if cont and nperiod == 5: limit = 2
            plt.plot(adate[-limit:], amem[-limit:], 'ro-', label="Memory Usage")
            for ndate, nmem in zip(adate, amem):
                plt.annotate(str(nmem), (ndate, nmem), textcoords="offset points", xytext=(0,10), ha='center')

    for trigger in triggers:
        if trigger[1] == 'cpu': color = 'b'
        if trigger[1] == 'memory': color = 'r'
        plt.axhline(y = trigger[2], color = color, linestyle = '--')

    plt.xlabel("Time")
    plt.ylabel("Percent")
    plt.ylim([0, 100])
    plt.legend()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    return send_file(img, mimetype='image/png')

@app.route("/trigger", methods=['POST'])
@nocache
def trigger():
    body = request.get_json()
    types = body["types"]
    metrics = body["metrics"]
    thresholds = body["thresholds"]

    triggers.clear()
    for stype, metric, threshold in zip(types, metrics, thresholds):
        triggers.append([stype, metric, int(threshold)])

    return {"status": "ok"}

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)