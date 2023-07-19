

# Сети, откуда МОЖНО ТОЛЬКО СМИНТИТЬ - ethereum / arbitrum / polygon / optimism / bsc / fantom / avalanche / nova / polygon_zk / zksync
# Сети, откуда МОЖНО БРИДЖИТЬ - ethereum / arbitrum / polygon / bsc / fantom / avalanche

# api - api моралиса можно найти здесь https://admin.moralis.io/settings#secret-keys

NETWORK_FROM = 'bsc'     # Откуда минтим или бриджим нфт
NETWORK_TO   = 'nova'    # Куда бриджим нфт

MODUL_MINT = True        # Если не нужен бридж, поставить False
MODUL_BRIDGE = True      # Если не нужен бридж, поставить False

WAIT_WALLETS = 30        # Задержка между кошельками

MAX_LZ_FEE = 1           # максимальная комиссия LZ (НЕ ГАЗ, А ИМЕННО КОМСА LZ)

API_KEY_MORALIS = ''     # сюда вставить ваш API Moralis