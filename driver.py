from code.chain import Chain
from code.sqlite import SQLite



address_db = SQLite('addresses')


#comment out chains you don't need
#to get the cookie, login into appropriate scanner (i.e. etherscan.io), press F12 in your browser, go to [scanner url]/labelcloud
#assuming you are using Chrome, go to Network -> Doc -> labelcloud -> Headers -> Request Headers -> cookie, right click on it and "Copy value"

eth_cookie = 'YOUR ETHERSCAN COOKIE HERE'
eth_api_key = 'YOUR ETHERSCAN API KEY'
ignore_labels = ['Eth2 Depositor','Blocked','User Proxy Contracts','Upbit Hack','Phish / Hack']
eth_chain = Chain(address_db,'ETH', 'etherscan.io', 'ETH', eth_api_key,eth_cookie, primary_swap='uniswap', ignore_labels=ignore_labels)

bsc_cookie = 'YOUR BSCSCAN COOKIE HERE'
bsc_api_key = 'YOUR BSCSCAN API KEY'
bsc_chain = Chain(address_db,'BSC', 'bscscan.com', 'BNB', bsc_api_key, bsc_cookie, primary_swap='pancakeswap' )

heco_cookie = 'YOUR HECOINFO COOKIE HERE'
heco_api_key = 'YOUR HECOINFO API KEY'
heco_chain = Chain(address_db,'HECO', 'hecoinfo.com', 'HT', heco_api_key, heco_cookie)

polygon_cookie = 'YOUR POLYGONSCAN COOKIE HERE'
polygon_api_key = 'YOUR POLYGONSCAN API KEY'
polygon_chain = Chain(address_db,'POLYGON', 'polygonscan.com', 'MATIC', polygon_api_key, polygon_cookie)

fantom_cookie = 'YOUR FTMSCAN COOKIE HERE'
fantom_api_key = 'YOUR FTMSCAN API KEY'
fantom_chain = Chain(address_db,'FANTOM', 'ftmscan.com', 'FTM', fantom_api_key, fantom_cookie)

hoo_cookie = 'YOUR HOOSCAN COOKIE HERE'
hoo_api_key = 'YOUR HOOSCAN API KEY'
hoo_chain = Chain(address_db,'HSC', 'hooscan.com', 'HOO', hoo_api_key, hoo_cookie)


chain = hoo_chain

#page scrapes labelcloud for list of labels, then downloads all addresses for each label
#if crashes, can restart where left off using start parameter
chain.store_all_labels_to_db()

#finds all deployers in the downloaded labels
deployer_dict = chain.load_from_db_by_label('Contract Deployer')
factory_dict = chain.load_from_db_by_label('Factory Contract')
unlabeled_dict = chain.find_unlabeled_deployers()
deployer_dict.update(factory_dict)
deployer_dict.update(unlabeled_dict)

#downloads children of each deployer using API. If crashes, can restart where left off using start parameter
chain.get_all_spawns_by_dict(deployer_dict)


address_db.disconnect()