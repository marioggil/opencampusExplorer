# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import Query, File, UploadFile,HTTPException
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import requests, json, uuid
from markupsafe import Markup
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Set, Tuple, Dict
from models.db import db
import private.modelcontract as LLMC
from config.parameters import recaptcha_site_key, recaptcha_secret_key

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

#Index


def BlocksIndex(items):
    list_data=[]
    for item in items["items"]:
        data=  {"hash":item['hash'],
        'height':item['height'],
        'size':item['size'],
        'miner':item['miner']['hash'],
        'difficulty':item['difficulty'],
        'burnt_fees':item['burnt_fees'],
        'base_fee_per_gas':item['base_fee_per_gas'],
        'parent_hash':item['parent_hash'],
        'total_difficulty':item['total_difficulty'],
            'tx_count':item['tx_count'],
            'timestamp':item['timestamp'],
            "gas_used":int(item['gas_used']),
        'gas_limit':item['gas_limit'],
        'tx_fees':int(item['tx_fees'])
        }
        list_data.append(data)
    df=pd.DataFrame(list_data)
    mean_size=int(df["size"].mean())
    mean_tx_count=int(df['tx_count'].mean())
    mean_tx_fees=int(df['tx_fees'].mean())
    mean_gas_used=int(df["gas_used"].mean())

    output={"items":list_data,"mean_size":mean_size,"mean_tx_count":mean_tx_count,"mean_tx_fees":mean_tx_fees,"mean_gas_used":mean_gas_used}
    return output

def metricsBlocks():
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/blocks?type=block").content)
    return BlocksIndex(response)

def stadistics_index(items):
    output={'network_utilization_percentage':items['network_utilization_percentage'],
            'total_blocks':items['total_blocks'],
            'total_transactions':items['total_transactions'],
            'transactions_today':items['transactions_today'],
            'total_addresses':items['total_addresses'],
            'gas_used_today':items['gas_used_today'],
            'average_block_time':int(items['average_block_time'])
    }
    return output



def stadistics_blockchain():
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/stats").content)
    return stadistics_index(response)


def TxIndex(items):
    list_data=[]
    for item in items["items"]:
        try:
            Tto=item["to"]["hash"]
        except:
            Tto=""
        try:
            Tfrom=item["from"]["hash"]
        except:
            Tfrom=""
        data=  {'timestamp':item['timestamp'],
        "fee":int(item["fee"]["value"]),
        'block':item["block"],
        'method':item["method"],
        "to":Tto,
        "from":Tfrom,
        'tx_burnt_fee':item['tx_burnt_fee'],
        "hash":item["hash"],
        'priority_fee':item['priority_fee'],
        'tx_types':item['tx_types'],
        'gas_used':int(item['gas_used']),
        'created_contract':item['created_contract'],
        }
        list_data.append(data)
    df=pd.DataFrame(list_data)
    mean_fee=int(df["fee"].mean())
    mean_gas_used=int(df["gas_used"].mean())
    output={"items":list_data,"mean_fee":mean_fee,"mean_gas_used":mean_gas_used}
    return output 

def metricsTx():
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/transactions?filter=validated").content)
    return TxIndex(response)

@app.get("/", response_class=HTMLResponse)
def index2(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    BlocksToIndex=metricsBlocks()

    Data_general=stadistics_blockchain()
    TxtoIndex=metricsTx()
        

    return templates.TemplateResponse("indexV2.html", 
                                        {
                                            "request": request,
                                            "Data_general":Data_general,
                                            "BlocksToIndex":BlocksToIndex["items"],
                                            "TxtoIndex":TxtoIndex["items"],
                                            "mean_fee_tx":TxtoIndex["mean_fee"],
                                            "mean_gas_used_tx":TxtoIndex["mean_gas_used"],
                                            "mean_size_Bl":BlocksToIndex["mean_size"],
                                            "mean_tx_count_Bl":BlocksToIndex["mean_tx_count"],
                                            "mean_tx_fees_Bl":BlocksToIndex["mean_tx_fees"],
                                            "mean_gas_used_Bl":BlocksToIndex["mean_gas_used"],
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

#Blocks


@app.get("/block/{number}", response_class=HTMLResponse)
def Blockhtml(request: Request, number:str):
    """
    Renders a page with metrics of blocks.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'index.html' template with metrics .
    """
    baseurl=str(request.base_url)
    height=int(number)
    s = db(db.blocks.height == height)
    if s.count()==0:
        requests.post(baseurl+"/block/%s"%(height))
    Block = db(db.blocks.height == height).select().last()
    Tx=json.loads(requests.get(baseurl+"/block/%s/tx?style=html"%(number)).content)
    
    return templates.TemplateResponse("block.html", {"request": request,"Block":Block,"Tx":Tx,"recaptcha_site_key":recaptcha_site_key})

@app.get("/block/{number}/tx")
def txperblockfind(request: Request,number:str,style:str="json",max:int=-1):
    output=[]
    txs=db(db.txs.block == number).select()
    
    if max<1:
        for tx in txs:
            output.append(tx.as_dict())
    else:
        counter=0
        for tx in txs:
            if counter > max:
                break
            output.append(tx.as_dict())
            counter=counter+1
    if style=="json":
        return json.dumps(output)
    if style=="html":
        htmlout="""<section class='section'>
    <div class='container'>
        <div class='columns is-centered'>
            <div class='column is-full-mobile is-half-tablet is-full-desktop'>
                <div class='box'>
                    <table class='table is-fullwidth is-striped is-hoverable is-fullwidth'>
                        <thead>
                            <tr>
                                <th>Hash</th>
                                <th>Fee</th>
                                <th>Block</th>
                                <!--<th>Method</th> -->
                                <th>To</th>
                                <th>From</th>
                                <!-- <th>Tx burnt fee</th>-->
                                <th>Timestamp</th>
                                <!--<th>Tx types</th>-->
                                <!--<th>Gas limit</th>-->
                                <th>Gas used</th>
                                <!--<th>Priority fee</th>-->
                                <!--<th>Created contract</th>-->
                            </tr>
                        </thead>
                        
                        <tbody>
                            """
        for tx in output:
            htmlout=htmlout+"""<tr>                                
            <th><a href='/tx/%s' title='%s' class='card-footer-item'>%s&nbsp; <img src='/static/link-solid.svg' alt=''></a> </th>
                                <td> %s </td>
                                
                                <td><a href=/wallet/%s title='%s' class='card-footer-item'>%s&nbsp; <img src='/static/link-solid.svg' alt=''></a></td>
                                <td><a href='/wallet/%s' title='%s' class='card-footer-item'>%s&nbsp; <img src='/static/link-solid.svg' alt=''></a></td>
                                
                                <td>%s </td>
                            </tr>    
                            """%(tx["hash"],tx["hash"],tx["hash"],tx["fee"],tx["tow"],tx["tow"],tx["tow"],tx["fromw"],tx["fromw"],tx["fromw"],tx["gas_used"])
            htmlout=htmlout+"""
                            
                        </tbody>
                    </table>
                </div>
            </div>  
        </div>
    </div>
</section>
"""




        return htmlout
        


@app.post("/block/{number}/tx")
def txperblock(request: Request,number:str):
    response=json.loads(requests.get('https://edu-chain-testnet.blockscout.com/api/v2/blocks/%s/transactions'%(number)).content)
    for item in response["items"]:
        TxDetail(item["hash"])


@app.post("/block/{number}")
def Block2db(request: Request,number:str):
    baseurl=str(request.base_url)
    
    if number=="last":
        response=json.loads(requests.get("https://edu-chain-testnet.blockscout.com/api/v2/blocks?type=block").content)
        number=response["items"][0]["height"]
    try:
        number=int(number)
        if db((db.blocks.height==number)).count()==0:
            BlockDetail(number)
            requests.post(baseurl+"/block/%s/tx"%(number))
        if db((db.blocksbach.block_heightOCS==number)).count()==0:
            requests.post(baseurl+"/block/%s/batch"%(number))
    except:
        error={"table":"txs","block":number}
        db.errors.insert(**error)
        db.commit()
    return {"message":"OK"}

def selectItemsBlock(item):
    data={}
    for key in ["hash",'height','size','miner','difficulty','burnt_fees','base_fee_per_gas','parent_hash','total_difficulty','tx_count','timestamp',"gas_used",'tx_fees','gas_limit']:
        if item[key] is None:
            pass
        else:
            if key=='miner':
                data[key]=item[key]["hash"]
            elif key=='height' or key=='tx_count' or key=='tx_fees' or key=="gas_used" or key=='tx_count' or key== 'gas_limit' or key=='total_difficulty' or key=='base_fee_per_gas' or key=='difficulty' or key=="burnt_fees":
                data[key]=int(item[key])
            else:
                data[key]=item[key]
    return data



def BlockDetail(block):
    try:
        response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/blocks/%s"%(block)).content)
        data=selectItemsBlock(response)
        db.blocks.insert(**data)
        db.commit()
        return {"message":"OK"}
    except:
        error={"table":"blocks","block":block}
        db.errors.insert(**error)
        db.commit()
        return {"message":"Error"}

#Blockbach
def bachOCS2ARB(block):
    keys=[['batch_numberOCS','batch_number'],['l1_block_heightARB','l1_block_height']]
    output={}
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/blocks/%s"%(block)).content)
    if 'arbitrum' in response.keys():
        data=response['arbitrum']
        output['block_heightOCS']=block
        output["hash"]=response["hash"]
        for key in keys:
            output[key[0]]=data[key[1]]
    return output
def bachARB2ETH(output):
    response=json.loads(requests.get("https://arbitrum-sepolia.blockscout.com/api/v2/blocks/%s"%(output['l1_block_heightARB'])).content)
    data=response['arbitrum']
    datatot=response
    output['batch_numberARB']=data['batch_number']
    output["priority_feeARB"]=datatot["priority_fee"]
    output["total_difficultyARB"]=datatot["total_difficulty"]
    output["transaction_feesARB"]=datatot["transaction_fees"]
    output["burnt_feesARB"]=datatot["burnt_fees"]
    output["difficultyARB"]=datatot["difficulty"]
    output["gas_limitARB"]=datatot["gas_limit"]
    output["gas_usedARB"]=datatot["gas_used"]
    output['l1_block_heightETH']=data['l1_block_height']
    return output
def bachETH2ETH(output):
    response=json.loads(requests.get("https://eth-sepolia.blockscout.com/api/v2/blocks/%s"%(output['l1_block_heightETH'])).content)
    datatot=response
    output["total_difficultyETH"]=datatot["total_difficulty"]
    output["transaction_feesETH"]=datatot["transaction_fees"]
    output["burnt_feesETH"]=datatot["burnt_fees"]
    output["difficultyETH"]=datatot["difficulty"]
    output["gas_limitETH"]=datatot["gas_limit"]
    output["gas_usedETH"]=datatot["gas_used"]
    output["status"]="OK"
    return output

@app.post("/block/{number}/batch")
def Blockbatch(request: Request,number:str):
    try:
        output=bachOCS2ARB(number)
        output=bachARB2ETH(output)
        output=bachETH2ETH(output)
        db.blocksbach.insert(**output)
        db.commit()
        return {"message":"OK"}
    except:
        output['block_heightOCS']=number
        output["status"]="Incomplete"
        db.blocksbach.insert(**output)
        error={"table":"blocksbach","block":number}
        db.errors.insert(**error)
        db.commit()
        return {"message":"Error"}
    

#Tx

def selectItemsTx(item):
    data={}
    for key in ['timestamp',"fee",'block','method',"from",'tx_burnt_fee',"hash",'priority_fee','tx_types','gas_used','created_contract',"to",'result','revert_reason','transaction_tag','has_error_in_internal_transactions']:
        if item[key] is None:
            pass
        else:
            if key=="to": 
                data["tow"]=item[key]["hash"]
            elif key=="from": 
                data["fromw"]=item[key]["hash"]
            elif key=='created_contract':
                data[key]=item[key]["hash"]
            elif key=="fee":
                data[key]=int(item[key]["value"])
            else:
                data[key]=item[key]
    return data


def TxVerif(hash):
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/transactions/%s"%(hash)).content)
    item=response
    tx=selectItemsTx(item)
    return {"message":"OK","block":tx["block"]}

def TxDetail(hash):
    try:
        response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/transactions/%s"%(hash)).content)
        item=response
        tx=selectItemsTx(item)
        db.txs.insert(**tx)
        db.commit()
        return {"message":"OK","block":tx["block"]}
    except:
        error={"table":"txs","hash":tx[hash]}
        db.errors.insert(**error)
        db.commit()
        return {"message":"Error"}
    
@app.get("/tx/{hash}", response_class=HTMLResponse)
def Txhtml(request: Request,hash: str):
    """
    Renders a page with metrics of Transactions.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'index.html' template with metrics.
    """
    baseurl=str(request.base_url)

    s = db(db.txs.hash == hash)
    if s.count()==0:
        Tx=TxVerif(hash)
    else:
        Tx=s.select().last().as_dict()


    height=int(Tx["block"])
    s = db(db.blocks.height == height)
    if s.count()==0:
        requests.post(baseurl+"/block/%s"%(height))
    
    return templates.TemplateResponse("tx.html", {"request": request,"Tx":Tx,"recaptcha_site_key":recaptcha_site_key})


#Wallet
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

def contractInfo(item):
    data={"is_vyper_contract":item['is_vyper_contract'],
            'is_fully_verified':item['is_fully_verified'],
            'is_blueprint':item['is_blueprint'],
            'source_code':item['source_code'],
            'verified_at': item['verified_at'],
            'is_verified': item['is_verified'],
            'name': item['name'],
            'language': item['language'],
            'compiler_version':item['compiler_version'],
            'evm_version':item['evm_version']
    }
    return data

def contractsDetail(hash):
    response=json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/smart-contracts/%s"%(hash)).content)
    data=contractInfo(response)
    DetailContract=LLMC.AnalysisContract(data["source_code"])
    try:
        DetailContract=json.loads(DetailContract)
    except:
        DetailContract=json.loads(DetailContract[DetailContract.find("{"):DetailContract.find("}")+1])
    data["functionality"]=DetailContract["Functionality Analysis"]
    data["sectoruse"]=DetailContract["Sector and Use Classification"]
    data["issues"]=DetailContract["Identification of Potential Issues"]
    data["summary"]=DetailContract["Summary and Recommendations"]
    data["hash"]=hash
    db.contracts.insert(**data)
    db.commit() 
    return {"message":"OK"}

@app.post("/wallet/{hash}/tx")
def TxsWallet(request: Request,hash: str) :#-> Tuple[List[Dict], Set[str], bool]:
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
    baseurl=str(request.base_url)
    towallet = requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=to'%(hash))
    fromwallet = requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=from'%(hash))
    for source in [towallet,fromwallet]:
        for item in json.loads(source.content)["items"]:
            height=int(item["block"])
            s = db(db.blocks.height == height)
            if s.count()==0:
                requests.post(baseurl+"/block/%s"%(height))
    return {"message":"OK"}


@app.post("/wallet/{wallet}")
def getwalletorcontract2db(request: Request,wallet:str):
    output={}
    hash=wallet
    baseurl=str(request.base_url)
    if not isContract(hash):
        output['hash']=hash
        output['is_contract']=False
        db.wallets.insert(**output)
        db.commit()
        return {"message":"OK"}
    else:
        output['hash']=hash
        output['is_contract']=True
        db.wallets.insert(**output)
        db.commit()
        contractsDetail(hash) 
        requests.post(baseurl+"/wallet/%s/tx"%(hash))
        return {"message":"OK"}
    
@app.get("/wallet/{wallet}", response_class=HTMLResponse)
def wallethtml(request: Request,wallet: str):
    """
    Renders a page with metrics of Transactions.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'index.html' template with metrics.
    """
    baseurl=str(request.base_url)

    s = db(db.wallets.hash == wallet)
    if s.count()==0:
        requests.post(baseurl+"/wallet/%s"%(wallet))
    requests.post(baseurl+"/wallet/%s/tx"%(wallet))
    Tx=[]
    data={}
    s = db(db.wallets.hash == wallet).select().last()
    data["hash"]=wallet

    if s["is_contract"]=="True":
        data["Type"]="Contract"
        contract = db(db.contracts.hash == wallet).select().last()
        data["Vyper contract"]=contract['is_vyper_contract']
        data["Is fully verified"]=contract['is_fully_verified']
        data["Blueprint"]=contract['is_blueprint']
        data["Verified at:"]=contract['verified_at']
        data["Verified"]=contract['is_verified']
        data["Name"]=contract['name']
        data["Language"]=contract['language']
        data["Compiler version"]=contract['compiler_version']
        data["Evm version"]=contract['evm_version']
        data["Funtionality"]=contract['functionality']
        data["Sector Use"]=contract['sectoruse']
        data["Issues"]=contract['issues']
        data["summary"]=contract['summary']

    else:
        data["Type"]="Wallet"
        
    Tx=requests.get(baseurl+"/wallet/%s/tx"%(wallet)).content
    


    return templates.TemplateResponse("wallet.html", {"request": request,"Tx":Tx,"data":data,"recaptcha_site_key":recaptcha_site_key})

@app.get("/wallet/{wallet}/tx")
def TxsInOut(request: Request,wallet: str):
    txs = db((db.txs.fromw == wallet) or (db.txs.tow == wallet) )
    alltx=[]
    for tx in txs.select():
        alltx.append(tx.as_dict())
    return alltx


