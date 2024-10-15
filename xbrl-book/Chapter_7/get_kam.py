from arelle import ModelManager
from arelle import Cntlr
import os
import glob
import re
from bs4 import BeautifulSoup

def make_edinet_company_info_list(xbrl_files, audit_files):
    edinet_company_info_list = []
    for index, (xbrl_file, audit_file) in enumerate(zip(xbrl_files, audit_files)):
        company_data = {
            "EDINETCODE": "",
            "企業名": "",
            "KAM": "",
        }
        
        ctrl = Cntlr.Cntlr()
        model_manager = ModelManager.initialize(ctrl)
        
        model_xbrl = model_manager.load(xbrl_file)
        model_audit = model_manager.load(audit_file)
        print("XBRLファイルを読み込んでいます", ":", index + 1, "/", len(xbrl_files))

        # 実データを探して取得
        for fact in model_xbrl.facts:
            
            # EDINETコードを探す
            if fact.concept.qname.localName == 'EDINETCodeDEI':
                company_data["EDINETCODE"] = fact.value

            # 企業名を探す
            elif fact.concept.qname.localName == 'FilerNameInJapaneseDEI':
                company_data["企業名"] = fact.value

        # 監査データからKAMを探して取得
        for fact in model_audit.facts:
        
            # KAMを探す
            if fact.concept.qname.localName == 'KeyAuditMattersConsolidatedTextBlock': 
                if fact.contextID == 'FilingDateInstant':
                    company_data["KAM"] = fact.value
                    
                    # BeautifulSoupを使ってHTMLタグを除去
                    soup = BeautifulSoup(company_data["KAM"], "html.parser")
                    company_data["KAM"] = soup.get_text()
        
                    # 空白や改行を取り除く
                    company_data["KAM"] = re.sub(r'\s', '', company_data["KAM"]).strip()    

        # 見つけたデータをリストに入れる
        edinet_company_info_list.append([
            company_data["EDINETCODE"],
            company_data["企業名"],
            company_data["KAM"],
        ])
        
    return edinet_company_info_list

def main():
    xbrl_files = glob.glob(r'*xbrl_zip\*\XBRL\PublicDoc\*.xbrl')
    audit_files = glob.glob(r'*xbrl_zip\*\XBRL\\AuditDoc\*aai*.xbrl')
    
    company_info = make_edinet_company_info_list(xbrl_files, audit_files)
    for info in company_info:
        print(info)

    print("extract finish")

if __name__ == "__main__":
    main()
    