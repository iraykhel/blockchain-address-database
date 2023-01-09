# Blockchain Address Ownership Database
Update 01/09/2023:
I've rescraped the data and remade the database. It's now too large for github, and can be downloaded from here: https://drive.google.com/file/d/1rEFloDWxmFjdb3SenSvrSsQk3g0-3RNk/view?usp=sharing
Currently the database has:
* ~1.3M ETH addresses
* ~600K BSC addresses
* ~320K Polygon addresses
* ~54K Fantom addresses
* ~5K Arbitrum addresses
* ~3K Optimism addresses
And also some addresses for Cronos, Gnossis, Aurora, Boba, HECO, CELO, Moonbeam, Moonriver

I have not updated the code. The scanners are too finicky and I don't want to spend time maintaining it. Let me know if you have any questions.

[old info below]
The database is in data/addresses.db

This is a SQLite database of addresses from several blockchains. It's obtained by page scraping & API-querying etherscan's team scanners. For each address it has some subset of [name tag, labels, ownership entity]. I page scraped each labelcloud (i.e. etherscan.io/labelcloud) for all labels, and then got all the addresses for each labels with their name tags. Additionally, I downloaded all addresses created by each labeled contract deployer and factory contract (using the scanner's API)

Exceptions: I didn't download all the million of shitcoin pools from uniswap and pancakeswap, only pools with at least 10 transactions. Also, etherscan-like scanners only allow for first 10000 transactions to be accessed via API, so children addresses will be missing from especially prolific deployers and factories.

The database will not update automatically. I may occasionally update it. You can create your own copy with the code; it requires BeautifulSoup for scraping, and cookie and API key from each scanner for the blockchains you want. If you're doing ETH or BSC it will take several hours.

Currently the database has:
* ~160K ETH addresses
* ~77K BSC addresses
* ~9K Polygon addresses
* ~13K HECO addresses
* ~2K Fantom addresses
* ~0.5K HSC addresses

