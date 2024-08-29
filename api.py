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

def maxValue(num):
    if num<1:
        num=1
    if num > 20:
        num=20
    return int(num)

def jsonTx(Tx):
    AAA=Tx 
    if  'contract_creation' in AAA['tx_types']:
        try:
            Sal={
                "value":float(AAA["value"])/10**18,
                "width":maxValue(float(AAA["value"])/10**18),
                "fee":float(AAA['fee']['value'])/10**18,
                'tx_types':AAA['tx_types'],
                'timestamp':AAA['timestamp'],
                'block':AAA['block'],
                'token_transfers':AAA['token_transfers'],
                "from_ens":AAA['from']['ens_domain_name'],
                "from_wallet":AAA['from']['hash'],
                "from_iscontract":AAA['from']['is_contract'],
                "to_wallet":AAA['created_contract']['hash'],  
                "id" : str(uuid.uuid4())  
            }
        except:
            print("Fail")
        return Sal
    else:
        try:  
            Sal={
            "value":float(AAA["value"])/10**18,
            "fee":float(AAA['fee']['value'])/10**18,
            "width":maxValue(float(AAA["value"])/10**18),
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
            "id" : str(uuid.uuid4())
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
    Contract=isContract(wallet)
    if Contract:
        return {"message":"Is contract"},0,0
    Out=[]
    towallet=requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=to'%(wallet))
    Out,walletsto=AllTx(towallet.content,Out)
    fromwallet=requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=from'%(wallet))
    Out,walletsfrom=AllTx(fromwallet.content,Out)
    walletsto.union(walletsfrom)

    return Out,walletsto.union(walletsfrom),Contract

def colorContract(test):
    if test:
        return '#FF5733'
    else:
        return "#000000"
def TxAllWallets(wallet,maxloop=1000):
    wallets=[]
    if isContract(wallet):
        return {"message":"Is contract"}
    Out,newwallets,contract=TxsWallet(wallet)
    wallets.append({"id":wallet,"url":"https://opencampus-codex.blockscout.com/address/"+wallet,"color" : "#27ae60"})
    print(wallets)
    counter=0
    Tot=len(newwallets)
    Doit=set()
    for aw in newwallets:
        counter=counter+1
        if counter>maxloop-1:
            break
        print("%s de %s"%(counter, Tot))
        Out2,temp,Contract=TxsWallet(aw)
        if aw not in Doit:
            wallets.append({"id":aw,"url":"https://opencampus-codex.blockscout.com/address/"+aw,"color" : colorContract(isContract(aw))})
            Doit.add(aw)
        if temp!=0:
            Out3=Out+Out2
            Out=Out3

    return Out, wallets

def makeData(Aw,Bw):
    listWallet=set()
    Sal1=[]
    for walletT in Bw:
        Sal1.append( { "id": walletT["id"], "url": walletT["url"], "color": walletT["color"] } )
        listWallet.add(walletT["id"])
    Sal2=[]
    counter=1
    for TxT in Aw: 
        if TxT["from_wallet"] not in listWallet:
            Sal1.append({ "id": TxT["from_wallet"], "url": "https://opencampus-codex.blockscout.com/address/"+TxT["from_wallet"], "color": colorContract(isContract(TxT["from_wallet"])) } )
        if TxT["to_wallet"] not in listWallet:
            Sal1.append({ "id": TxT["to_wallet"], "url": "https://opencampus-codex.blockscout.com/address/"+TxT["to_wallet"], "color": colorContract(isContract(TxT["to_wallet"])) } )
        Sal2.append({" id": TxT["id"], "source": TxT["from_wallet"], "target": TxT["to_wallet"], "width":TxT["width"] } )
        counter+=1
    Sal=Sal1+Sal2
    return Sal



@app.get("/{IDwallet}")
def read_items(IDwallet:str,request: Request):
    print(IDwallet)
    Aw,Bw=TxAllWallets("0x907fC0C7E6b84F0229c13F57D413F72D33Ff3bAf")
    Resultado=makeData(Aw,Bw)
    return templates.TemplateResponse("index.html", {"request": request})

    