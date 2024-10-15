import requests
import datetime
import os

def make_day_list(start_date, end_date):
    print("start_date:", start_date)
    print("end_date:", end_date)
    
    period = end_date - start_date
    period = int(period.days)
    day_list = []
    for d in range(period + 1):
        day = start_date + datetime.timedelta(days=d)
        day_list.append(day)
    
    return day_list

def make_doc_id_list(day_list):
    securities_report_doc_list = []
    for index, day in enumerate(day_list):
        url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
        params = {"date": day.strftime("%Y-%m-%d"),
                    "type": 2,
                    "Subscription-Key":"your_subscription_key"# Subscription-Keyは自分のAPIキーを使用
                    }
    
        
        
        res = requests.get(url, params=params)
        json_data = res.json()
        print(day)
        
        if "results" in json_data:
            for num in range(len(json_data["results"])):
                ordinance_code = json_data["results"][num]["ordinanceCode"]
                form_code = json_data["results"][num]["formCode"]
                docInfoEditStatus = json_data["results"][num]["docInfoEditStatus"]
                
                if ordinance_code =="010"and form_code =="030000" and docInfoEditStatus !=2:
                    print(json_data["results"][num]["filerName"], json_data["results"][num]["docDescription"],
                        json_data["results"][num]["docID"])
                    securities_report_doc_list.append(json_data["results"][num]["docID"])
                    
    return securities_report_doc_list

def download_xbrl_in_zip(securities_report_doc_list, number_of_lists):
        # ▼ダウンロードする有報を保存しておく場所を指定。もしなければフォルダを作成する。
    save_dir = "/path/to/download/directory/" # あなたの保存先のパスに変更してください。
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for index, doc_id in enumerate(securities_report_doc_list):
        print(doc_id, ":", index + 1, "/", number_of_lists)
        url =f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
        params = {"type": 1, 
                    "Subscription-Key":"your_subscription_key"# Subscription-Keyは自分のAPIキーを使用
                    }
        filename = os.path.join(save_dir, f"{doc_id}.zip")
        res = requests.get(url, params=params, stream=True)
        
    try :
        if res.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in res.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded and Saved: {filename}")
    except Exception as e:
        print(f"Failed to download file {doc_id}, status code: {e}")
        
def main():
    # ▼集める期間
    start_date = datetime.date(2024, 5, 1) # 開始日付
    end_date = datetime.date(2024, 5, 31) # 終了日付
    day_list = make_day_list(start_date, end_date)
    
    securities_report_doc_list = make_doc_id_list(day_list)
    number_of_lists = len(securities_report_doc_list)
    print("number_of_lists: ", number_of_lists)
    print("get_list: ", securities_report_doc_list)
    
    download_xbrl_in_zip(securities_report_doc_list, number_of_lists)
    print("download finish")
    
    
if __name__ == "__main__":
    main()