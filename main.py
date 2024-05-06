from flask import Flask, request
from app.domain.chart_machine import ChartMachine
import app.domain.cron_ai as soda
from apscheduler.schedulers.background import BackgroundScheduler
from app.infra.db.mongodb.mongodb_handler import MongoDBHandler
import os
from app.infra.machine.chatGPT_machine import ChatMachine
from app.domain.init_coin_data import init_code

rest_port= port = int(os.getenv("PORT", 5000))

# eureka_client.init(eureka_server="http://flowbit-discovery:8761/eureka/",
#                    app_name="bitcoin-service",
#                    instance_port=rest_port)
app = Flask(__name__)

@app.route("/")
def home():
    html = """
    <html>
        <head><meta charset="utf-8"></head>
        <body>
            <h1>MAIN PAGE</h1>
        </body>
    </html>
    """
    return html
@app.route("/get_predict_value")
def get_predict_value():
    ret = {}
    mongodbMachine = MongoDBHandler(db_name="AI", collection_name="actual_data")

    data = mongodbMachine.find_last_item(db_name="AI", collection_name="predicted_data")
    del data["_id"]

    data["predicted_krw"] = data["predicted_price"]
    del data["predicted_price"]

    ret["predicted_data"] = data
    data = mongodbMachine.find_last_item(db_name="AI", collection_name="actual_data")
    del data["_id"]

    ret["actual_data"] = data

    return ret

@app.route("/get_basic_chart")
def get_basic_chart():
    chart_machine = ChartMachine()

    return chart_machine.get_basic_chart()

@app.route("/get_all_chart")
def get_all_chart():
    chart_machine = ChartMachine()

    return chart_machine.get_all_chart()

@app.route("/get_chart_analysis")
def get_chart_analysis():

    mongodbMachine = MongoDBHandler(db_name="BTC", collection_name="analysis_data")
    data = mongodbMachine.find_last_item(db_name="BTC", collection_name="analysis_data")
    
    del data["_id"]
    
    return data

@app.route("/chart")
def get_chart():
    arg = request.args.get('currency')
    print(arg)
    chart_machine = ChartMachine()
    result = {}
    if arg == "BTC":
        result = chart_machine.get_all_multiple_chart(db_name=arg)
    else:
        result = chart_machine.get_all_single_chart(db_name=arg)

    return result

@app.route("/test_cron")
def test_cron():
    soda.save_one_day_data()

    return "this is my name"

if __name__ == "__main__":
    init_code()
    chat_machine = ChatMachine()
    port = int(os.getenv("PORT", 5000))

    sched = BackgroundScheduler(daemon=True)
    sched.remove_all_jobs()
    sched.add_job(soda.save_one_day_data, 'cron', hour=0, minute=1)
    sched.start()
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)