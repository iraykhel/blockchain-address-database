import json
import requests
import time
from .util import log
import re
from bs4 import BeautifulSoup
import traceback

class Chain:
    def __init__(self,db,name,explorer_domain,main_asset, api_key, cookie, primary_swap=None, ignore_labels=()):
        self.explorer_domain = explorer_domain
        self.api_url = 'https://api.'+explorer_domain+'/api'

        self.main_asset = main_asset
        self.api_key = api_key
        self.cookie = cookie
        self.name=name
        self.db = db
        self.primary_swap = primary_swap
        self.ignore_labels = ignore_labels

        # self.db.create_table(self.name+"_addresses", 'address PRIMARY KEY, deployer, entity', drop=False)
        # self.db.create_index(self.name + "_addresses_idx_1", self.name+"_addresses", 'entity')

        self.db.create_table(self.name + "_addresses", 'address PRIMARY KEY, tag, ancestor_address, entity', drop=False)
        self.db.create_table(self.name + "_labels", 'address, label', drop=False)
        self.db.create_index(self.name + "_addresses_idx_1", self.name+"_addresses", 'entity')
        self.db.create_index(self.name + "_labels_idx_1", self.name + "_labels", 'address, label', unique=True)

        self.load_all_from_db()

    def get_label_list(self):
        url = 'https://' + self.explorer_domain + '/labelcloud'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'cache-control': 'max-age=0',
                   'cookie': self.cookie}
        cont = requests.get(url, headers=headers).content
        html = cont.decode('utf-8')
        soup = BeautifulSoup(html, features="lxml")
        dropdowns = soup.find_all('div',class_='dropdown')

        accounts_labels = []
        for entry in dropdowns:
            label_url = entry.find('button')['data-url']
            label = entry.find('span').contents[0]
            sections = entry.find_all('a')
            # print(label, sections)
            for section in sections:
                tp = section.contents[-1]
                if 'Accounts' in tp:
                    accounts_labels.append((label.strip(),label_url))
                    break
        return accounts_labels




    def extract_entity(self,tag):
        if ':' in tag:
            row_entity = tag[:tag.index(':')].upper()
        else:
            tag_parts = tag.split(' ')
            if tag_parts[-1].isdigit():
                row_entity = ' '.join(tag_parts[:-1]).upper()
            else:
                row_entity = tag.upper()
        return row_entity

    # def download_labeled(self,label, subcatid='undefined',entity=None, page_size=10000):
    #     db_table = self.name+"_addresses"
    #     # self.db.create_table(db_table, 'address PRIMARY KEY, label, tag, entity', drop=False)
    #     # self.db.create_index(self.name+"_"+table+"_idx_1", db_table, 'entity')
    #     offset = 0
    #     page_idx = 0
    #     done = False
    #     while not done:
    #         url = 'https://'+self.explorer_domain+'/accounts/label/'+label+'?subcatid='+subcatid+'&size='+str(page_size)+'&start='+str(offset)+'&col=1&order=asc'
    #         print(page_idx,offset,url)
    #         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    #                    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #                    'cache-control':'max-age=0',
    #                    'cookie':self.cookie}
    #         cont = requests.get(url,headers=headers).content
    #         # print(cont)
    #         html = cont.decode('utf-8')
    #         soup = BeautifulSoup(html,features="lxml")
    #         if subcatid == 'undefined':
    #             table = soup.find("table", class_="table-hover")
    #         else:
    #             table = soup.find("table", id="table-subcatid-"+subcatid)
    #         # print(table)
    #         try:
    #             rows = table.find_all("tr")
    #         except:
    #             print('EXCEPTION',traceback.format_exc())
    #             print(html)
    #             exit(0)
    #         print('rows',len(rows))
    #         for row in rows:
    #             # print(row)
    #             cells = row.find_all("td")
    #             # print(len(cells))
    #             if len(cells) == 4:
    #                 address = cells[0].find("a").contents[0]
    #                 tag = cells[1].contents
    #                 if len(tag) == 1:
    #                     tag = tag[0]
    #                     if entity is None:
    #                         row_entity = self.extract_entity(tag)
    #                     else:
    #                         row_entity = entity
    #                     # print(address,tag,row_entity)
    #                     self.db.insert_kw(db_table,values = [address,tag,None,row_entity])
    #                     self.db.insert_kw(self.name+"_labels", values=[address, label])
    #         self.db.commit()
    #         offset += page_size
    #         page_idx += 1
    #
    #         # done=True
    #         if len(rows) < page_size:
    #             done = True
    #         else:
    #             print("sleeping")
    #             time.sleep(30)


    def download_labeled_post(self,label, label_url):
        db_table = self.name + "_addresses"
        # label_rep = label.lower().replace(' ','-').replace('.','-')
        url = 'https://' + self.explorer_domain + '/accounts/label/' + label_url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
                   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'cache-control': 'max-age=0',
                   'cookie': self.cookie}
        cont = requests.get(url, headers=headers).content
        soup = BeautifulSoup(cont,features="lxml")
        header = soup.find('div',class_='card-header')
        if header is None:
            subcats = ['undefined']
        else:
            subcats = []
            subcat_els = header.find_all('a')
            for subcat_el in subcat_els:
                subcat = subcat_el['val']
                subcats.append(subcat)
        log(label,'subcats',subcats)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
                   'cache-control': 'max-age=0',
                   # 'referer':'https://etherscan.io/accounts/label/balancer-vested-shareholders',
                   'accept': 'application/json, text/javascript, */*; q=0.01',
                   'content-type': 'application/json',
                   'cookie': self.cookie}
        page_size = 100 #it won't give more than 100
        for subcat in subcats:
            log('subcat',subcat)
            done = False
            start = 0
            inserted = 0
            while not done:

                payload = {"dataTableModel":{"draw":2,"columns":[{"data":"address","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"nameTag","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"balance","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}},{"data":"txnCount","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}}],"order":[{"column":3,"dir":"desc"}],"start":start,"length":page_size,"search":{"value":"","regex":False}},
                           "labelModel":{"label":label_url}}
                if subcat != 'undefined':
                    payload['labelModel']['subCategoryId'] = subcat

                url = 'https://' + self.explorer_domain + '/accounts.aspx/GetTableEntriesBySubLabel'
                payload = json.dumps(payload)
                # print(payload)
                time.sleep(0.25)
                resp = requests.post(url, payload, headers=headers)
                js = json.loads(resp.content.decode('utf-8'))
                data = js['d']['data']
                if len(data) < page_size:
                    done = True
                # print(resp.content)
                # pprint.pprint(js)
                txncount = None
                for entry in data:
                    address = entry['address']
                    match = re.search('0x[a-f0-9]{40}',address)
                    address = match.group()
                    if address:

                        txncount = int(entry['txnCount'].replace(',',''))
                        if label.lower() == self.primary_swap and txncount < 10:
                            done = True

                        nametag = None
                        row_entity = None
                        if 'nameTag' in entry and len(entry['nameTag']) > 0:
                            nametag = entry['nameTag']
                            row_entity = self.extract_entity(nametag)

                        self.db.insert_kw(db_table, values=[address, nametag, None, row_entity])
                        self.db.insert_kw(self.name + "_labels", values=[address, label])
                        inserted += 1

                log('label',label,'sub',subcat,'start',start,'inserted',inserted, 'last txncount',txncount)
                self.db.commit()


                start += page_size

    def store_all_labels_to_db(self, start = None):
        label_list = self.get_label_list()
        for label_name, label_url in sorted(label_list):
            if start is not None and label_name < start:
                continue
            if 1:
                if label_name in self.ignore_labels:
                    log("Ignoring label",label_name)
                else:
                    log("Processing label",label_name,label_url)
                    self.download_labeled_post(label_name,label_url)


    def load_all_from_db(self):
        self.addresses = {}
        rows = self.db.select("SELECT * FROM "+self.name+"_addresses")
        log(self.name,str(len(rows))+" addresses currently in the database")
        for row in rows:
            address, tag, ancestor, entity = row
            self.addresses[address] = entity




    def get_spawns(self,address, ancestor, entity, level=0, deep=False):
        time.sleep(0.25)
        offset = '  ' * level
        log(offset, address, entity)
        if deep and level > 0:
            self.db.insert_kw(self.name + "_addresses", values=[address, None, ancestor, entity], ignore=True)
        url = self.api_url + "?module=account&action=txlist&address=" + address + "&page=1&sort=asc&apikey=" + self.api_key + "&offset=10000"
        resp = requests.get(url).json()
        cnt = 0
        cnt_int = 0
        data1 = resp['result']
        for transaction in data1:
            if transaction['to'] == '' and len(transaction['input']) > 2 and transaction['value'] == '0' and transaction['from'].lower() == address and transaction['isError'] == '0':
                spawn = transaction['contractAddress'].lower()
                if spawn not in self.addresses:
                    if deep:
                        cnt_sub_1, cnt_sub_2, _, _ = self.get_spawns(spawn, ancestor, entity, level=level+1, deep=True)
                        cnt += cnt_sub_1
                        cnt_int += cnt_sub_2
                    else:
                        self.db.insert_kw(self.name + "_addresses", values=[spawn, None, address, entity], ignore=True)
                    cnt += 1

        time.sleep(0.25)
        url = self.api_url + "?module=account&action=txlistinternal&address=" + address + "&page=1&sort=asc&apikey=" + self.api_key + "&offset=10000"
        resp = requests.get(url).json()
        data2 = resp['result']
        ld2 = 0
        if data2 is not None:
            ld2 = len(data2)
            for transaction in data2:
                if 'create' in transaction['type'] and transaction['to'] == "":
                    spawn = transaction['contractAddress'].lower()
                    if spawn not in self.addresses:
                        if deep:
                            cnt_sub_1, cnt_sub_2, _, _ = self.get_spawns(spawn, ancestor, entity, level=level+1, deep=True)
                            cnt += cnt_sub_1
                            cnt_int += cnt_sub_2
                        else:
                            self.db.insert_kw(self.name + "_addresses", values=[spawn, None, address, entity])
                        cnt_int += 1

        return cnt, cnt_int, len(data1),ld2
                # if spawn not in self.deployers:
                #     self.get_spawns(spawn, entity, level=level+1)



    def load_from_db_by_label(self,label):
        res = {}
        Q = "select a.* from "+self.name+"_addresses as a, "+self.name+"_labels as l WHERE a.address = l.address and l.label = '"+label+"'"
        # print(Q)
        rows = self.db.select(Q)
        for row in rows:
            address, tag, ancestor, entity = row
            res[address.lower()] = entity
        return res

    def find_unlabeled_deployers(self):
        query = "select a.*, group_concat(label) as labellist " \
                "from "+self.name+"_addresses as a, "+self.name+"_labels as l " \
                "where a.address = l.address and (tag like '%factory%' or tag like '%deployer%') " \
                "group by a.address " \
                "having labellist not like '%contract-deployer%' and labellist not like '%factory%'"
        rows = self.db.select(query)
        res = {}
        for row in rows:
            res[row[0].lower()] = row[3]
        return res


    def get_all_spawns_by_dict(self, addr_dict, start = None):
        for idx, (address, entity) in enumerate(sorted(addr_dict.items())):
            if start is not None and address < start:
                continue
            cnt,  cnt_int, total, total_int = self.get_spawns(address,address,entity)
            log(idx, "Father", address, entity, cnt, cnt_int, total, total_int)
            self.db.commit()



    def test(self):
        # address = '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f' #uniswap factory
        # address = '0xbaf9a5d4b0052359326a6cdab54babaa3a3a9643' #1inch factory
        # url = self.api_url + "?module=account&action=txlistinternal&address=" + address + "&page=1&sort=asc&apikey=" + self.api_key + "&offset=10000"
        # resp = requests.get(url)
        # pprint.pprint(resp.json())
        # res = self.get_spawns('0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f', 'UNISWAP')
        # print(res)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
                   # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'cache-control': 'max-age=0',
                   # 'referer':'https://etherscan.io/accounts/label/balancer-vested-shareholders',
                   'accept':'application/json, text/javascript, */*; q=0.01',
                   'content-type':'application/json',
                   'cookie': self.cookie}
        # payload = {"dataTableModel":{"draw":2,"columns":[{"data":"address","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"nameTag","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"balance","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}},{"data":"txnCount","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}}],"order":[{"column":3,"dir":"desc"}],"start":0,"length":25,"search":{"value":"","regex":False}},"labelModel":{"label":"balancer-vested-shareholders"}}
        # payload = {"dataTableModel":{"draw":2,"columns":[{"data":"address","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"nameTag","name":"","searchable":True,"orderable":False,"search":{"value":"","regex":False}},{"data":"balance","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}},{"data":"txnCount","name":"","searchable":True,"orderable":True,"search":{"value":"","regex":False}}],"order":[{"column":3,"dir":"desc"}],"start":9000,"length":25,"search":{"value":"","regex":False}},"labelModel":{"label":"pancakeswap"}}
        true = True
        false = False
        payload = {"dataTableModel": {"columns": [], "order": [{"column": 1, "dir": "desc"}], "start": 0, "length": 200},
                   # "labelModel": {"label": "factory-contract"}
                   "addressModel": {"address":"0xfc00c80b0000007f73004edb00094cad80626d8d"}
                   }


        payload = json.dumps(payload)
        # url = 'https://etherscan.io/accounts.aspx/GetTableEntriesBySubLabel'
        url = 'https://'+self.explorer_domain+'/accounts.aspx/GetTableEntriesBySubLabel'
        resp = requests.post(url,payload,headers=headers)
        # print(resp)
        print(resp.content.decode('utf-8'))
        # js = json.loads(resp.content.decode('utf-8'))
        # pprint.pprint(js)
