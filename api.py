import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel
import time
from fastapi.staticfiles import StaticFiles
from fastapi import Query, File, UploadFile,HTTPException
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import requests
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
#app.mount("/statics", StaticFiles(directory="statics"), name="statics")
templates = Jinja2Templates(directory="templates")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def isContract(hash):
    A=requests.get('https://opencampus-codex.blockscout.com/api/v2/smart-contracts/%s'%(hash))
    if A.status_code==200:
        return True
    else:
        return False

def jsonTx(Tx):
    AAA=Tx 
    if  'contract_creation' in AAA['tx_types']:
        try:
            Sal={
                "value":float(AAA["value"])/10**18,
                "fee":float(AAA['fee']['value'])/10**18,
                'tx_types':AAA['tx_types'],
                'timestamp':AAA['timestamp'],
                'block':AAA['block'],
                'token_transfers':AAA['token_transfers'],
                "from_ens":AAA['from']['ens_domain_name'],
                "from_wallet":AAA['from']['hash'],
                "from_iscontract":AAA['from']['is_contract'],
                "to_wallet":AAA['created_contract']['hash'],            
            }
        except:
            print("Fail")
        return Sal
    else:
        try:  
            Sal={
            "value":float(AAA["value"])/10**18,
            "fee":float(AAA['fee']['value'])/10**18,
            'tx_types':AAA['tx_types'],
            'timestamp':AAA['timestamp'],
            'block':AAA['block'],
            'token_transfers':AAA['token_transfers'],
            "to_ens":AAA['to']['ens_domain_name'],
            "to_wallet":AAA['to']['hash'],
            "to_iscontract":AAA['to']['is_contract'],
            "from_ens":AAA['from']['ens_domain_name'],
            "from_wallet":AAA['from']['hash'],
            "from_iscontract":AAA['from']['is_contract'],
            }
        except:
            print("Fail")
        return Sal

def AllTx(Txs,Out):
    wallets=set()
    for i in json.loads(Txs)['items']:
        Temp=jsonTx(i)
        Out.append(Temp)
        wallets.add(Temp["from_wallet"])
        wallets.add(Temp["to_wallet"])
    return Out,wallets


    
def TxsWallet(wallet):
    if isContract(wallet):
        return {"message":"Is contract"},0
    Out=[]
    towallet=requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=to'%(wallet))
    Out,walletsto=AllTx(towallet.content,Out)
    fromwallet=requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=from'%(wallet))
    Out,walletsfrom=AllTx(fromwallet.content,Out)
    walletsto.union(walletsfrom)

    return Out,walletsto.union(walletsfrom)

def TxAllWallets(wallet):
    if isContract(wallet):
        return {"message":"Is contract"}
    Out,newwallets=TxsWallet(wallet)

    for aw in newwallets:
        print(aw)
        
        Out2,temp=TxsWallet(aw)
        if temp!=0:
            Out3=Out+Out2
            Out=Out3
    return Out


@app.get("/{IDwallet}")
def read_items(IDwallet:str,request: Request):
    print(IDwallet)
    return templates.TemplateResponse("index.html", {"request": request})

    