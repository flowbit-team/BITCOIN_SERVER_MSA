from app.infra.db.mongodb.mongodb_handler import MongoDBHandler

class ChartMachine:

    def get_analysis_chart(self, database_name="BTC"):
        """
        1. actual_data 가지고 오기 - 14개
        2. predicted_data 가지고 오기 - 15개
        """
        db = MongoDBHandler(mode="remote", db_name=database_name, collection_name="actual_data")
        actual_data = db.find_items_for_chart( db_name=database_name, collection_name="actual_data", limit=14)
        predicted_data = db.find_items_for_chart(db_name=database_name, collection_name="predicted_data", limit=15)

        actual_data_list = []
        predicted_data_list = []

        actual_data_str = ''
        predicted_data_str = ''

        for i in actual_data:
            # print("일단 여기까지 옴...")
            i["_id"] = str(i["_id"])
            actual_data_str += str(i["close_price"]) + ","

        for i in predicted_data:
            i["_id"] = str(i["_id"])
            predicted_data_str += str(i["predicted_price"]) + ","
        
        return actual_data_str, predicted_data_str

    def get_basic_chart(self, db_name="BTC"):

        db = MongoDBHandler(mode="remote", db_name=db_name, collection_name="actual_data")
        actual_data = db.find_items_for_chart( db_name=db_name, collection_name="actual_data", limit=14)
        predicted_data = db.find_items_for_chart(db_name=db_name, collection_name="predicted_data", limit=15)

        actual_data_list = []
        predicted_data_list = []
        lables = []

        for i in actual_data:
            actual_data_list.append(i["close_price"])

        for i in predicted_data:
            lables.append(i["timestamp"][5:])
            predicted_data_list.append(i["predicted_price"])

        chart_data = {}
        actual_data_list.reverse()
        predicted_data_list.reverse()
        lables.reverse()

        max_value = max(actual_data_list + predicted_data_list)
        min_value = min(actual_data_list + predicted_data_list)

        blank = (min_value + max_value) / 30
        chart_data["max"] = max_value + blank
        chart_data["min"] = min_value - blank
        chart_data["label"] = lables[::2][1:]
        chart_data["datas"] = [
            {"label" : "실제 BTC", "datas" : actual_data_list}, 
            {"label" : "예측 BTC", "datas" : predicted_data_list}]

        return chart_data
    
    def get_all_chart(self, db_name="BTC"):

        db = MongoDBHandler(mode="remote", db_name=db_name, collection_name="actual_data")
        actual_data = db.find_items(db_name=db_name, collection_name="actual_data")
        predicted_data = db.find_items(db_name=db_name, collection_name="predicted_data")
        multiple_predicted_data = db.find_last_item(db_name=db_name, collection_name="multiple_predicted_data")

        actual_data_list = []
        predicted_data_list = []
        lables = []

        for i in actual_data:
            actual_data_list.append(i["close_price"])

        for i in predicted_data:
            lables.append(i["timestamp"])
            predicted_data_list.append(i["predicted_price"])

        for i in multiple_predicted_data.get("predicted_data"):
            print(i)
            lables.append(i["timestamp"])
            predicted_data_list.append(i["predicted_price"])


        chart_data = {}

        max_value = max(actual_data_list + predicted_data_list)
        min_value = min(actual_data_list + predicted_data_list)

        blank = (min_value + max_value) / 30
        chart_data["max"] = max_value + blank
        chart_data["min"] = min_value - blank
        chart_data["label"] = lables

        start_index = len(actual_data_list) - len(predicted_data_list)

        print(len(actual_data_list))
        print(len(predicted_data_list))

        chart_data["datas"] = [
            {"label" : "실제 " + db_name, "datas" : actual_data_list[start_index + 1:]},
            {"label" : "예측 " + db_name, "datas" : predicted_data_list}
        ]

        return chart_data

    def get_all_multiple_chart(self, db_name="BTC"):

        db = MongoDBHandler(mode="remote", db_name=db_name, collection_name="actual_data")
        actual_data = db.find_items(db_name=db_name, collection_name="actual_data")
        predicted_data = db.find_items(db_name=db_name, collection_name="predicted_data")
        multiple_predicted_data = db.find_last_item(db_name=db_name, collection_name="multiple_predicted_data")

        actual_data_list = []
        predicted_data_list = []
        lables = []

        for i in actual_data:
            actual_data_list.append(i["close_price"])

        for i in predicted_data:
            lables.append(i["timestamp"])
            predicted_data_list.append(i["predicted_price"])

        for i in multiple_predicted_data.get("predicted_data"):
            # print(i)
            lables.append(i["timestamp"])
            predicted_data_list.append(i["predicted_price"])


        chart_data = {}

        max_value = max(actual_data_list + predicted_data_list)
        min_value = min(actual_data_list + predicted_data_list)

        blank = (min_value + max_value) / 30
        chart_data["max"] = max_value + blank
        chart_data["min"] = min_value - blank
        chart_data["label"] = lables

        start_index = len(actual_data_list) - len(predicted_data_list)

        print(len(actual_data_list))
        print(len(predicted_data_list))

        chart_data["datas"] = [
            {"label" : "실제 BTC", "datas" : actual_data_list[start_index + 1:]},
            {"label" : "예측 BTC", "datas" : predicted_data_list}
        ]

        return chart_data

    def get_all_single_chart(self, db_name="BTC"):

        db = MongoDBHandler(mode="remote", db_name=db_name, collection_name="actual_data")
        actual_data = db.find_items(db_name=db_name, collection_name="actual_data")
        predicted_data = db.find_items(db_name=db_name, collection_name="predicted_data")

        actual_data_list = []
        predicted_data_list = []
        lables = []

        for i in actual_data:
            actual_data_list.append(i["close_price"])

        for i in predicted_data:
            lables.append(i["timestamp"])
            predicted_data_list.append(i["predicted_price"])


        chart_data = {}

        max_value = max(actual_data_list + predicted_data_list)
        min_value = min(actual_data_list + predicted_data_list)

        blank = (min_value + max_value) / 30
        chart_data["max"] = max_value + blank
        chart_data["min"] = min_value - blank
        chart_data["label"] = lables

        start_index = len(actual_data_list) - len(predicted_data_list)

        print(len(actual_data_list))
        print(len(predicted_data_list))

        chart_data["datas"] = [
            {"label" : "실제 " + db_name, "datas" : actual_data_list[start_index + 1:]},
            {"label" : "예측 " + db_name, "datas" : predicted_data_list}
        ]

        return chart_data