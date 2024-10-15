from arelle import ModelManager
from arelle import Cntlr
import os
import glob
import re
from bs4 import BeautifulSoup
import pandas as pd

def make_edinet_info_list(edinetcodedlinfo_filepath):
    try:
        edinet_info = pd.read_csv(edinetcodedlinfo_filepath, skiprows=1, encoding='cp932')
        edinet_info = edinet_info[["ＥＤＩＮＥＴコード", "提出者業種"]]
        edinet_info_list = edinet_info.values.tolist()
        return edinet_info_list
    
    except Exception as e:
        print(f"EDINET情報の取得に失敗しました: {e}")
        return []

def make_edinet_company_info_list(xbrl_files, edinet_info_list, audit_files):
    edinet_company_info_list = []
    for index, (xbrl_file, audit_file) in enumerate(zip(xbrl_files, audit_files)):
        company_data = {
            "EDINETCODE": None,
            "企業名": None,
            "業種": None,
            "営業利益(IFRS)": None,
            "事業等のリスク": None,
            "KAM": None,
        }
        
        try:
            ctrl = Cntlr.Cntlr()
            model_manager = ModelManager.initialize(ctrl)
            model_xbrl = model_manager.load(xbrl_file)
            model_audit = model_manager.load(audit_file)
            print("XBRLファイルを読み込んでいます", ":", index + 1, "/", len(xbrl_files))
            
        except Exception as e:
            print(f"XBRLファイルの読み込みに失敗しました ({xbrl_file} または {audit_file}): {e}")
            edinet_company_info_list.append(list(company_data.values()))
            continue

        try:
            # 実データを探して取得
            for fact in model_xbrl.facts:
                # EDINETコードを探す
                if fact.concept.qname.localName == 'EDINETCodeDEI':
                    company_data["EDINETCODE"] = fact.value

                    # 業種をEDINETコードに基づいて設定
                    for code_name in edinet_info_list:
                        if code_name[0] == company_data["EDINETCODE"]:
                            company_data["業種"] = code_name[1]
                            break

                # 企業名を探す
                elif fact.concept.qname.localName == 'FilerNameInJapaneseDEI':
                    company_data["企業名"] = fact.value

                # 営業利益(IFRS)を探す
                elif fact.concept.qname.localName == 'OperatingProfitLossIFRS':
                    if fact.contextID == 'CurrentYearDuration':
                        company_data["営業利益(IFRS)"] = fact.value

                # 事業等のリスクを探す
                elif fact.concept.qname.localName == 'BusinessRisksTextBlock':
                    if fact.contextID == 'FilingDateInstant':
                        raw_risk = fact.value
                        # BeautifulSoupを使ってHTMLタグを除去
                        soup = BeautifulSoup(raw_risk, "html.parser")
                        company_data["事業等のリスク"] = re.sub(r'\s', '', soup.get_text()).strip()
                        
        except Exception as e:
            print(f"有報の解析中にエラーが発生しました ({xbrl_file}): {e}")

        try:
            # 監査データからKAMを探して取得
            for fact in model_audit.facts:
                if fact.concept.qname.localName == 'KeyAuditMattersConsolidatedTextBlock':
                    if fact.contextID == 'FilingDateInstant':
                        raw_kam = fact.value
                        # BeautifulSoupを使ってHTMLタグを除去
                        soup = BeautifulSoup(raw_kam, "html.parser")
                        company_data["KAM"] = re.sub(r'\s', '', soup.get_text()).strip()
                        
        except Exception as e:
            print(f"監査報告書の解析中にエラーが発生しました ({audit_file}): {e}")

        # 見つけたデータをリストに入れる
        edinet_company_info_list.append(list(company_data.values()))
        
    return edinet_company_info_list

def write_csv(edinet_company_info_list):
    try:
        xbrl_frame = pd.DataFrame(edinet_company_info_list,
                         columns=['EDINETCODE', '企業名', '業種', '営業利益(IFRS)(円)', '事業等のリスク', 'KAM'])

        # EDINETコードでソート
        xbrl_frame_sorted = xbrl_frame.sort_values(by='EDINETCODE', ascending=True)
				
				# CSVファイルで出力する
        xbrl_frame_sorted.to_csv("xbrl_book.csv", encoding='utf-8-sig', index=False)
    except Exception as e:
        print(f"CSVの書き込み中にエラーが発生しました: {e}")

def main():
    # EDINETコードリストを追加
    edinetcodedlinfo_filepath = r'C:\Users\ユーザー名\Downloads\Edinetcode_20241007\EdinetcodeDlInfo.csv'
    edinet_info_list = make_edinet_info_list(edinetcodedlinfo_filepath)
    
    xbrl_files = glob.glob(r'*xbrl_zip\*\XBRL\PublicDoc\*.xbrl')
    audit_files = glob.glob(r'*xbrl_zip\*\XBRL\AuditDoc\*aai*.xbrl')
    
    edinet_company_info_list = make_edinet_company_info_list(xbrl_files, edinet_info_list, audit_files)
    
    write_csv(edinet_company_info_list)
    print("extract finish")

if __name__ == "__main__":
    main()