import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel
import time
from fastapi.staticfiles import StaticFiles
from fastapi import Query, File, UploadFile,HTTPException
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import requests, json, uuid
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Set, Tuple, Dict
from models.db import db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def isContract(hash: str) -> bool:
    """
    Checks if a given hash corresponds to a smart contract on the Blockscout platform.

    Args:
        hash (str): The hash of the contract to verify.

    Returns:
        bool: Returns True if the hash corresponds to a smart contract, otherwise False.
    """
    url = f'https://opencampus-codex.blockscout.com/api/v2/smart-contracts/{hash}'
    response = requests.get(url)
    return response.status_code == 200

def maxValue(num: float) -> int:
    """
    Adjusts the input number to ensure it falls within the range of 1 to 20.

    Args:
        num (float): The input number to adjust.

    Returns:
        int: The adjusted number, constrained to be between 1 and 20.
    """
    num = max(1, min(num, 20))
    return int(num)

def jsonTx(Tx: dict) -> dict:
    """
    Processes a transaction dictionary and returns a formatted JSON object with relevant transaction details.

    Args:
        Tx (dict): The input transaction dictionary to process.

    Returns:
        dict: A dictionary containing formatted transaction details, including value, fee, width, 
            addresses, and contract information.
    """
    AAA = Tx
    try:
        base_sal = {
            "value": float(AAA["value"]) / 10**18,
            "width": maxValue(float(AAA["value"]) / 10**18),
            "fee": float(AAA['fee']['value']) / 10**18,
            'tx_types': AAA['tx_types'],
            'timestamp': AAA['timestamp'],
            'block': AAA['block'],
            'token_transfers': AAA['token_transfers'],
            "from_ens": AAA['from']['ens_domain_name'],
            "from_wallet": AAA['from']['hash'],
            "from_iscontract": AAA['from']['is_contract'],
            "id": str(uuid.uuid4())
        }

        if 'contract_creation' in AAA['tx_types']:
            base_sal["to_wallet"] = AAA['created_contract']['hash']
        else:
            base_sal["to_ens"] = AAA['to']['ens_domain_name']
            base_sal["to_wallet"] = AAA['to']['hash']
            base_sal["to_iscontract"] = AAA['to']['is_contract']
        
        return base_sal

    except Exception as e:
        print("Fail:", e)
        return {}

def AllTx(Txs: str, Out: List[dict]) -> Tuple[List[dict], Set[str]]:
    """
    Processes multiple transactions, appends their formatted details to the output list, 
    and collects unique wallet addresses involved in the transactions.

    Args:
        Txs (str): A JSON string containing multiple transactions.
        Out (List[dict]): A list where processed transaction details will be appended.

    Returns:
        Tuple[List[dict], Set[str]]: A tuple containing the updated list of transaction details 
                                    and a set of unique wallet addresses.
    """
    wallets = set()
    for i in json.loads(Txs)['items']:
        Temp = jsonTx(i)
        Out.append(Temp)
        wallets.add(Temp["from_wallet"])
        wallets.add(Temp.get("to_wallet", Temp.get("from_wallet")))  # Handle cases with missing "to_wallet"
    
    return Out, wallets
    
def TxsWallet(wallet: str) -> Tuple[List[Dict], Set[str], bool]:
    """
    Retrieves and processes transactions associated with a given wallet address.

    Args:
        wallet (str): The wallet address to retrieve transactions for.

    Returns:
        Tuple[List[Dict], Set[str], bool]: 
            - A list of processed transaction details.
            - A set of unique wallet addresses involved in the transactions.
            - A boolean indicating if the wallet is a smart contract.
    """
    Contract = isContract(wallet)
    if Contract:
        return {"message": "Is contract"}, set(), Contract

    Out = []

    # Fetch transactions where the wallet is the recipient (to)
    towallet = requests.get(f'https://opencampus-codex.blockscout.com/api/v2/addresses/{wallet}/transactions?filter=to')
    Out, walletsto = AllTx(towallet.content, Out)

    # Fetch transactions where the wallet is the sender (from)
    fromwallet = requests.get(f'https://opencampus-codex.blockscout.com/api/v2/addresses/{wallet}/transactions?filter=from')
    Out, walletsfrom = AllTx(fromwallet.content, Out)

    # Combine wallets from both transactions
    all_wallets = walletsto.union(walletsfrom)

    return Out, all_wallets, Contract

def colorContract(test: bool) -> str:
    """
    Returns a specific color code based on whether the input is a contract.

    Args:
        test (bool): A boolean indicating if the entity is a contract.

    Returns:
        str: The color code '#FF5733' if it's a contract, otherwise '#000000'.
    """
    return '#FF5733' if test else '#000000'

def TxAllWallets(wallet: str, maxloop: int = 1000) -> Tuple[List[Dict], List[Dict]]:
    """
    Retrieves and processes transactions for a wallet and related wallets up to a specified limit.

    Args:
        wallet (str): The initial wallet address to start processing transactions for.
        maxloop (int, optional): The maximum number of iterations to process wallets. Defaults to 1000.

    Returns:
        Tuple[List[Dict], List[Dict]]: 
            - A list of processed transaction details for all relevant wallets.
            - A list of dictionaries containing wallet information and their respective color codes.
    """
    wallets = []
    if isContract(wallet):
        return {"message": "Is contract"}, []

    Out, newwallets, contract = TxsWallet(wallet)
    wallets.append({"id": wallet, "url": f"https://opencampus-codex.blockscout.com/address/{wallet}", "color": "#27ae60"})
    print(wallets)

    counter = 0
    Tot = len(newwallets)
    Doit = set()

    for aw in newwallets:
        counter += 1
        if counter >= maxloop:
            break
        print(f"{counter} of {Tot}")

        Out2, temp, Contract = TxsWallet(aw)

        if aw not in Doit:
            wallets.append({"id": aw, "url": f"https://opencampus-codex.blockscout.com/address/{aw}", "color": colorContract(Contract)})
            Doit.add(aw)

        if temp:
            Out += Out2

    return Out, wallets

def makeData(Aw: List[Dict], Bw: List[Dict]) -> List[Dict]:
    """
    Generates a combined data structure from wallet and transaction information.

    Args:
        Aw (List[Dict]): A list of transactions with details like wallet addresses, IDs, and widths.
        Bw (List[Dict]): A list of wallet information with IDs, URLs, and colors.

    Returns:
        List[Dict]: A combined list of wallet and transaction data, each represented as a dictionary.
    """
    listWallet = set()
    Sal1 = []

    # Process the initial list of wallets (Bw)
    for walletT in Bw:
        Sal1.append({"id": walletT["id"], "url": walletT["url"], "color": walletT["color"]})
        listWallet.add(walletT["id"])

    Sal2 = []
    counter = 1
    Tot = len(Aw)

    # Process transactions (Aw) and add wallets if they are not already in listWallet
    for TxT in Aw:
        if TxT["from_wallet"] not in listWallet:
            Sal1.append({
                "id": TxT["from_wallet"],
                "url": f"https://opencampus-codex.blockscout.com/address/{TxT['from_wallet']}",
                "color": colorContract(isContract(TxT["from_wallet"]))
            })
            listWallet.add(TxT["from_wallet"])
        
        if TxT["to_wallet"] not in listWallet:
            Sal1.append({
                "id": TxT["to_wallet"],
                "url": f"https://opencampus-codex.blockscout.com/address/{TxT['to_wallet']}",
                "color": colorContract(isContract(TxT["to_wallet"]))
            })
            listWallet.add(TxT["to_wallet"])

        Sal2.append({
            "id": TxT["id"],
            "source": TxT["from_wallet"],
            "target": TxT["to_wallet"],
            "width": TxT["width"]
        })
        
        print(f"{counter} of {Tot}")
        counter += 1

    Sal = Sal1 + Sal2
    return Sal

def Ranking(Aw: List[Dict], Bw: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Generates a ranking of the top 5 wallets and contracts based on transaction value and count.

    Args:
        Aw (List[Dict]): A list of transactions, each containing details like `value`, `from_wallet`, and `to_wallet`.
        Bw (List[Dict]): A list of wallet information, including `id` and `color`.

    Returns:
        Dict[str, List[Dict]]: A dictionary with the top 5 rankings in four categories:
            - `To_Sum`: Top 5 wallets/contracts receiving the most value.
            - `To_Count`: Top 5 wallets/contracts by the number of received transactions.
            - `From_Sum`: Top 5 wallets/contracts sending the most value.
            - `From_Count`: Top 5 wallets/contracts by the number of sent transactions.
    """
    AllWallets: Set[str] = set()

    # Collect wallet IDs based on specific color codes
    for data in Bw:
        if data["color"] == '#000000' or data["color"] == '#27ae60':
            AllWallets.add(data["id"])

    df = pd.DataFrame(Aw)

    # Create pivot tables for the sum and count of values for 'to_wallet' and 'from_wallet'
    A1 = pd.pivot_table(df, values="value", index=["to_wallet"], aggfunc="sum").sort_values(by=['value'], ascending=False)
    A2 = pd.pivot_table(df, values="value", index=["to_wallet"], aggfunc="count").sort_values(by=['value'], ascending=False)
    B1 = pd.pivot_table(df, values="value", index=["from_wallet"], aggfunc="sum").sort_values(by=['value'], ascending=False)
    B2 = pd.pivot_table(df, values="value", index=["from_wallet"], aggfunc="count").sort_values(by=['value'], ascending=False)

    Sal = {"To_Sum": [], "To_Count": [], "From_Sum": [], "From_Count": []}

    # Generate the top 5 rankings for each category
    for idx, j in enumerate([A1, A2, B1, B2], start=1):
        Temp3 = []
        for i in range(5):
            try:
                Temp2 = {}
                wallet_id = j.index[i]
                Temp2["type"] = "Wallet" if wallet_id in AllWallets else "Contract"
                Temp2["name"] = wallet_id
                Temp2["value"] = int(j.iloc[i].value)
                Temp3.append(Temp2)
            except IndexError:
                pass

        if idx == 1:
            Sal["To_Sum"] = Temp3
        elif idx == 2:
            Sal["To_Count"] = Temp3
        elif idx == 3:
            Sal["From_Sum"] = Temp3
        elif idx == 4:
            Sal["From_Count"] = Temp3

    return Sal

def get_wallet_actions(walletsactions: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Retrieves the top 5 wallets based on the number of actions, sorted in descending order.

    Args:
        walletsactions (Dict[str, int]): A dictionary where keys are wallet IDs and values are the number of actions.

    Returns:
        List[Tuple[str, int]]: A list of tuples containing the top 5 wallet IDs and their action counts.
                            If there are fewer than 5 wallets, all of them are returned.
    """
    # Sort wallets by the number of actions in descending order
    sorted_wallets_by_actions = sorted(walletsactions.items(), key=lambda x: x[1], reverse=True)

    # Return the top 5 wallets, or fewer if there aren't that many
    return sorted_wallets_by_actions[:5]

def search_data(IDwallet: str) -> Tuple[List[Dict[str, Dict]], List[Tuple[str, int]], List[Tuple[str, int]]]:
    """
    Searches for data related to a specific wallet ID and ranks the associated wallets by actions.

    Args:
        IDwallet (str): The ID of the wallet to search for.

    Returns:
        Tuple[List[Dict[str, Dict]], List[Tuple[str, int]], List[Tuple[str, int]]]:
            - A list of dictionaries containing data information (either 'id' and 'url' or 'id', 'source', 'target', and 'width').
            - A list of the top 5 wallets ranked by the number of actions as sources.
            - A list of the top 5 wallets ranked by the number of actions as targets.
    """
    Resultado = []
    ranking_to = {}
    ranking_from = {}

    # Retrieve wallet information from the database
    wallet = db(db.wallets.wallet_id == IDwallet).select().last()
    if wallet:
        # Search for related data in the database
        search = db(db.datas.wallet == wallet.id).select()
        for i in search:
            data = {}
            if i.uuid.startswith('0x'):
                data = {'data': {'id': i.uuid, 'url': i.url, 'color': i.color}}
            else:
                data = {'data': {'id': i.uuid, 'source': i.source, 'target': i.target, 'width': i.width}}
                # Update rankings for sources and targets
                ranking_to[i.source] = ranking_to.get(i.source, 0) + 1
                ranking_from[i.target] = ranking_from.get(i.target, 0) + 1
            Resultado.append(data)

    # Get the top wallets by actions as sources and targets
    return Resultado, get_wallet_actions(ranking_to), get_wallet_actions(ranking_from)

@app.get("/wallet", response_class=HTMLResponse)
def read_items(request: Request, IDwallet: str = None):
    """
    Handles the request to retrieve and display wallet data.

    Args:
        request (Request): The request object.
        IDwallet (str, optional): The ID of the wallet to retrieve data for. Defaults to None.

    Returns:
        HTMLResponse: Renders the 'wallet.html' template with the provided data.
    """
    Resultado, ranking_to, ranking_from = search_data(IDwallet)
    
    if Resultado:
        Resultado = json.dumps(Resultado)
    else:
        Aw, Bw = TxAllWallets(IDwallet)
        Resultado = makeData(Aw, Bw)
        wallet = db.wallets.insert(wallet_id=IDwallet)
        db.commit()
        for i in Resultado:
            db.datas.insert(
                wallet=wallet,
                uuid=i['id'],
                url=i.get('url'),
                color=i.get('color'),
                source=i.get('source'),
                target=i.get('target'),
                width=i.get('width')
            )
        db.commit()
        Resultado, ranking_to, ranking_from = search_data(IDwallet)
        Resultado = json.dumps(Resultado)

    return templates.TemplateResponse(
        "wallet.html",
        {
            "request": request,
            "IDwallet": IDwallet,
            "Resultado": Resultado,
            "ranking_to": ranking_to,
            "ranking_from": ranking_from,
            "enumerate": enumerate
        }
    )
    
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Renders the index page.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'index.html' template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get_wallets", response_class=HTMLResponse)
def get_wallets(request: Request):
    """
    Renders a page with a list of wallets retrieved from the database.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'wallets_db.html' template with the list of wallets.
    """
    wallets = db(db.wallets).select()
    return templates.TemplateResponse("wallets_db.html", {"request": request, "wallets": wallets})