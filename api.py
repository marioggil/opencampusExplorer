import fastapi
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel
import time
from fastapi.staticfiles import StaticFiles
from fastapi import Query, File, UploadFile,HTTPException
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import requests, json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import uuid
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
    Tot=len(Aw)
    for TxT in Aw: 
        if TxT["from_wallet"] not in listWallet:
            Sal1.append({ "id": TxT["from_wallet"], "url": "https://opencampus-codex.blockscout.com/address/"+TxT["from_wallet"], "color": colorContract(isContract(TxT["from_wallet"])) } )
        if TxT["to_wallet"] not in listWallet:
            Sal1.append({ "id": TxT["to_wallet"], "url": "https://opencampus-codex.blockscout.com/address/"+TxT["to_wallet"], "color": colorContract(isContract(TxT["to_wallet"])) } )
        Sal2.append({"id": TxT["id"], "source": TxT["from_wallet"], "target": TxT["to_wallet"], "width":TxT["width"] } )
        counter+=1
        print("%s de %s"%(counter, Tot))
    Sal=Sal1+Sal2
    return Sal

def Ranking(Aw,Bw):
    AllWallets=set()
    for data in Bw:
        if data["color"]=='#000000' or data["color"]=='#27ae60':
            AllWallets.add(data["id"])
    df=pd.DataFrame(Aw)
    A1=pd.pivot_table(df, values="value",index=["to_wallet"],aggfunc="sum").sort_values(by=['value'],ascending=False)
    A2=pd.pivot_table(df, values="value",index=["to_wallet"],aggfunc="count").sort_values(by=['value'],ascending=False)
    B1=pd.pivot_table(df, values="value",index=["from_wallet"],aggfunc="sum").sort_values(by=['value'],ascending=False)
    B2=pd.pivot_table(df, values="value",index=["from_wallet"],aggfunc="count").sort_values(by=['value'],ascending=False)
    Temp=0
    Sal={"To_Sum":[],"To_Count":[],"From_Sum":[],"From_Count":[]}
    for j in [A1,A2,B1,B2]:
        Temp+=1
        Temp3=[]
        for i in range(10):
            Temp2={}
            if j.iloc[i].name in AllWallets:
                Temp2["type"]="Wallet"
            else:
                Temp2["type"]="Contract"
            Temp2["name"]=j.iloc[i].name
            Temp2["value"]=int(j.iloc[i].value)
            Temp3.append(Temp2)
        if Temp==1:
            Sal["To_Sum"]=Temp3
        if Temp==2:
            Sal["To_Count"]=Temp3
        if Temp==3:
            Sal["From_Sum"]=Temp3
        if Temp==4:
            Sal["From_Count"]=Temp3
    return Sal

def search_data(IDwallet):
    Resultado = []
    
    wallet = db(db.wallets.wallet_id == IDwallet).select().last()
    if wallet:
        search = db(db.datas.wallet == wallet.id).select()
        Resultado = []
        for i in search:
            data = {}
            if i.uuid.startswith('0x'):
                data = {'data':{'id':i.uuid,'url':i.url,'color':i.color}}
            else:
                data = {'data':{'id':i.uuid,'source':i.source,'target':i.target,'width':i.width}}
            
            Resultado.append(data)
            
    return Resultado



@app.get("/wallet/{IDwallet}")
def read_items(IDwallet:str,request: Request):
    
    Resultado = search_data(IDwallet)   
    
    if Resultado:        
        Resultado = json.dumps(Resultado)
    else:
        Aw,Bw=TxAllWallets(IDwallet)#"0x907fC0C7E6b84F0229c13F57D413F72D33Ff3bAf")
        Resultado=makeData(Aw,Bw)
        wallet = db.wallets.insert(wallet_id = IDwallet)
        db.commit()
        for i in Resultado:            
            db.datas.insert(
                wallet = wallet,
                uuid = i['id'],
                url = i['url'] if 'url' in i else None,
                color = i['color'] if 'color' in i else None,
                source = i['source'] if 'source' in i else None,
                target = i['target'] if 'target' in i else None,
                width = i['width'] if 'width' in i else None,
            )
        db.commit()
    
        Resultado = search_data(IDwallet)
        Resultado = json.dumps(Resultado)

        Ranks=Ranking(Aw,Bw)
    
    
    return templates.TemplateResponse("index.html", {"request": request, "IDwallet": IDwallet, "Resultado":Resultado})