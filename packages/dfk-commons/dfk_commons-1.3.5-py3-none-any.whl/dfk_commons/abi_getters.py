import json
from pathlib import Path

current_file_path = Path(__file__).absolute()

ERC20Json_path = current_file_path.parent / "abi/ERC20.json"
ERC721Json_path = current_file_path.parent / "abi/ERC721.json"
HeroCoreJson_path = current_file_path.parent / "abi/HeroCoreDiamond.json"
HeroSaleJson_path = current_file_path.parent / "abi/HeroSale.json"
HeroBridgeJson_path = current_file_path.parent / "abi/HeroBridgeUpgradeable.json"
RouterJson_path = current_file_path.parent / "abi/UniswapV2Router02.json"
QuestCoreJson_path = current_file_path.parent / "abi/QuestCoreV3.json"
BazaarJson_path = current_file_path.parent / "abi/Bazaar.json"
PairJson_path = current_file_path.parent / "abi/UniswapPair.json"

ERC20Json = open(ERC20Json_path)
ERC20ABI = json.load(ERC20Json)

ERC721Json = open(ERC721Json_path)
ERC721ABI = json.load(ERC721Json)

HeroCoreJson = open(HeroCoreJson_path)
HeroCoreABI = json.load(HeroCoreJson)

HeroSaleJson = open(HeroSaleJson_path)
HeroSaleABI = json.load(HeroSaleJson)

HeroBridgeJson = open(HeroBridgeJson_path)
HeroBridgeABI = json.load(HeroBridgeJson)

RouterJson = open(RouterJson_path)
RouterABI = json.load(RouterJson)

QuestCoreJson = open(QuestCoreJson_path)
QuestCoreABI = json.load(QuestCoreJson)

BazaarJson = open(BazaarJson_path)
BazaarABI = json.load(BazaarJson)

PairJson = open(PairJson_path)
PairABI = json.load(PairJson)
