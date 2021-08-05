# Blockchain Address Database
The database is in data/addresses.db

This is a SQLite database of addresses from several blockchains. It's obtained by, for lack of a better word, pillaging etherscan's team scanners. I page scraped each labelcloud (i.e. etherscan.io/labelcloud) for all labels, and then got all the addresses for each labels with their name tags. Additionally, I downloaded all addresses created by each labeled contract deployer and factory contract (using the scanner's API)

Exceptions: I didn't download all the million of shitcoin pools from uniswap and pancakeswap, only pools with at least 10 transactions. Also, etherscan-like scanners only allow for first 10000 transactions to be accessed via API, so children addresses will be missing from especially prolific deployers and factories.

The database will not update automatically. I may occasionally update it. You can create your own copy with the code; all it requires is BeautifulSoup for scraping. It will take several hours.

Currently the database has:
* ~160K ETH addresses
* ~77K BSC addresses
* ~9K Polygon addresses
* ~13K HECO addresses
* ~2K Fantom addresses
* ~0.5K HSC addresses
