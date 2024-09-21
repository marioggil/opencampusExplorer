# -*- coding: utf-8 -*-
"""Explorer of blocks clioscan

Returns:
    _type_: null
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import Query, File, UploadFile,HTTPException
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import json
from markupsafe import Markup
import numpy as np
from fastapi.templating import Jinja2Templates
from typing import List, Set, Tuple, Dict
from models.db import db
import private.modelcontract as LLMC
from schema import select_stadistics_index,select_item_block,select_items_tx,select_item_contract,select_item_bachOCS2ARB,select_item_bachARB2ETH,select_item_bachETH2ETH
from config.parameters import recaptcha_site_key, recaptcha_secret_key,url_api_educhain,url_api_arbitrum,url_api_ethereum

import logging
from dataclasses import dataclass
import os
from datetime import datetime
from ast import literal_eval
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
def extractConfig(nameModel="SystemData",relPath=os.path.join("private/experiment_config.json"),dataOut="keygroq"):
    configPath=os.path.join(os.getcwd(),relPath)
    with open(configPath, 'r', encoding='utf-8') as file:
        config = json.load(file)[nameModel]
    Output= config[dataOut]
    return Output
def transform_text2formatedtext(text):
    list_text = literal_eval(text)
    sal=""
    for i in list_text:
        sal=sal+"""
"""+i
    return sal
        
keygroq=extractConfig(nameModel="SystemData",dataOut="keygroq")
baseurl=extractConfig(nameModel="SystemData",dataOut="baseurl")
#Index

def blocks_index(items):
    list_data=[]
    for item in items["items"]:
        data = select_item_block(item)
        list_data.append(data)
    df=pd.DataFrame(list_data)
    mean_size=int(df["size"].mean())
    mean_tx_count=int(df['tx_count'].mean())
    mean_tx_fees=int(df['tx_fees'].mean())
    mean_gas_used=int(df["gas_used"].mean())
    output={"items":list_data,"mean_size":mean_size,"mean_tx_count":mean_tx_count,"mean_tx_fees":mean_tx_fees,"mean_gas_used":mean_gas_used}
    return output

def metricsBlocks():
    response=json.loads(requests.get(url_api_educhain+"api/v2/blocks?type=block").content)
    return blocks_index(response)

def stadistics_blockchain():
    response=json.loads(requests.get(url_api_educhain+"api/v2/stats").content)
    return select_stadistics_index(response)

def TxIndex(items):
    list_data=[]
    for item in items["items"]:
        data=select_items_tx(item)
        list_data.append(data)
        
    df=pd.DataFrame(list_data)
    
    mean_fee=df["fee"].mean()
    mean_gas_used=df["gas_used"].mean()
    output={"items":list_data,"mean_fee":mean_fee,"mean_gas_used":mean_gas_used}
    return output 

def metricsTx():
    response=json.loads(requests.get(url_api_educhain+"api/v2/transactions?filter=validated").content)
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

@app.get("/root_section_1", response_class=HTMLResponse)
def root_section_1(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """

    
    Data_init=stadistics_blockchain()
    Data_general=[]
    equivalence={"network_utilization_percentage":"Network utilization percentage",
                 "total_blocks":"Total blocks",
                 "total_transactions":"Total transactions",
                 "transactions_today":"Transactions today",
                 "total_addresses":"Total addresses",
                 "gas_used_today":"Gas used today",
                 "average_block_time":"Average block time"
    }
    for column in Data_init.keys():
        Data_general.append([equivalence[column],Data_init[column]])

        


        

    return templates.TemplateResponse("root_section_1.html", 
                                        {
                                            "request": request,
                                            "Data_general":Data_general,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })
@app.get("/root_section_2", response_class=HTMLResponse)
def root_section_2(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    BlocksToIndex=metricsBlocks()
    
    
   

    return templates.TemplateResponse("root_section_2.html", 
                                        {
                                            "request": request,
                                            "BlocksToIndex":BlocksToIndex["items"],
                                            "mean_size_Bl":BlocksToIndex["mean_size"],
                                            "mean_tx_count_Bl":BlocksToIndex["mean_tx_count"],
                                            "mean_tx_fees_Bl":BlocksToIndex["mean_tx_fees"],
                                            "mean_gas_used_Bl":BlocksToIndex["mean_gas_used"],
                                            "recaptcha_site_key":recaptcha_site_key
                                            })




@app.get("/root_section_3", response_class=HTMLResponse)
def root_section_3(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    TxtoIndex=metricsTx()
    
    
        

    return templates.TemplateResponse("root_section_3.html", 
                                        {
                                            "request": request,
                                            "TxtoIndex":TxtoIndex["items"],
                                            "mean_fee_tx":TxtoIndex["mean_fee"],
                                            "mean_gas_used_tx":TxtoIndex["mean_gas_used"],
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

@app.get("/root_section_4", response_class=HTMLResponse)
def root_section_4(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    formater={"created_on":"Date of metrics in system",
    "n_wallets":"Total wallets",
    "n_contracts":"Total contracts",
    "n_contracts_is_vyper_contract":"Total contracts in vyper",
    "n_contracts_is_verified":"Total contracts verified",
    "n_txs":"Total transactions",
    "n_txs_not_success": "Total transactions not success",
    "n_blocks":"Total blocks",



    }

    to_hist={"n_contracts_language":"Total languages in contracts",
    "n_contracts_evm_version": "Total versions of evm  in contracts",
    "n_blocks_tx_count": "Total transactions in blocks",
    "n_blocks_miner": "Total blocks mine in wallets"}

    data=[]
    sequences = db(db.stadists_site).select().last()
    for column in sequences.keys():
        if column in formater.keys():
            data.append([formater[column],sequences[column]])
        
        
    
        

    return templates.TemplateResponse("root_section_4.html", 
                                        {
                                            "request": request,
                                            "content":data ,
                                            "to_hist": to_hist,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

def list_to_hist(data,limit=0):
    sal=[]
    for d in data.keys():
        if limit==0:
            sal.append({ "range": d, "frequency": data[d] })
        else:
            sal.append({ "range": d[limit:], "frequency": data[d] })

    return sal




@app.get("/root_section_4_hist", response_class=HTMLResponse)
def root_section_4_hist(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """


    to_hist={"n_contracts_language":"Total languages in contracts",
    "n_contracts_evm_version": "Total versions of evm  in contracts",
    "n_blocks_tx_count": "Total transactions in blocks",
    "n_blocks_miner": "Total blocks mine in wallets"}

    data=[]
    sequences = db(db.stadists_site).select().last()
    for column in sequences.keys():
        if column in to_hist.keys():
            if column=="n_blocks_miner":
                data.append([to_hist[column],list_to_hist(json.loads(sequences[column]),-6)])
            else:
                data.append([to_hist[column],list_to_hist(json.loads(sequences[column]))])
    
        

    return templates.TemplateResponse("root_section_4_hist.html", 
                                        {
                                            "request": request,
                                            "content":data ,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

@app.get("/root_section_5", response_class=HTMLResponse)
def root_section_5(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """



    summary = db.blocks.day_week, db.blocks.hour, db.blocks.tx_count.sum()
    rows = db(db.blocks.id > 0).select(*summary, groupby=(db.blocks.day_week, db.blocks.hour))
    summary_blocks_day_week_hour={}
    
    for row in rows:
        summary_blocks_day_week_hour[str(row.blocks.day_week)+"-"+str(row.blocks.hour)]=row[db.blocks.tx_count.sum()]
    data=[]
    for row in summary_blocks_day_week_hour.keys():
        data.append(summary_blocks_day_week_hour[row])
    percentils=[np.percentile(data, 25),np.percentile(data, 50),np.percentile(data, 75)]
    return templates.TemplateResponse("root_section_5.html", 
                                        {
                                            "request": request,
                                            "summary_blocks_day_week_hour":summary_blocks_day_week_hour,
                                            "percentils":percentils,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })



@app.get("/root_section_6", response_class=HTMLResponse)
def root_section_6(request: Request):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    summary = db.blocks.timestamp, db.blocks.tx_count.sum()

    rows = db(db.blocks.id > 0).select(*summary, groupby=db.blocks.timestamp)

    summary_block_day={}

    for row in rows:
        if row[db.blocks.timestamp].strftime('%Y-%m-%d') not in summary_block_day:
            summary_block_day[row[db.blocks.timestamp].strftime('%Y-%m-%d')]= row[db.blocks.tx_count.sum()]
        else:
            summary_block_day[row[db.blocks.timestamp].strftime('%Y-%m-%d')]+= row[db.blocks.tx_count.sum()]
    list_summary_block_day=[]
    data=[]
    for date in summary_block_day.keys():
        count=summary_block_day[date]
        list_summary_block_day.append(
            {"date": date, "count": count }
        )
        data.append(count)
    percentils=[np.percentile(data, 25),np.percentile(data, 50),np.percentile(data, 75)]

    return templates.TemplateResponse("root_section_6.html", 
                                        {
                                            "request": request,
                                            "enumerate": enumerate,
                                            "list_summary_block_day":list_summary_block_day,
                                            "percentils":percentils,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })




@app.get("/version", response_class=HTMLResponse)
def versionhtml(request: Request):
    return "0.0.0"

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
    # baseurl=str("clioscan.com.co")
    height=int(number)
    s = db(db.blocks.height == height)
    if s.count()==0:
        requests.post(baseurl+"/block/%s"%(height))

    return templates.TemplateResponse("block.html", {"request": request,"height":height,"recaptcha_site_key":recaptcha_site_key})

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
        return templates.TemplateResponse("block_section_tx.html", {"request": request,"content":output,"recaptcha_site_key":recaptcha_site_key})


@app.get("/block/section_1/{number}", response_class=HTMLResponse)
def block_section_1(request: Request,number:str):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    
    height=int(number)
    Block = db(db.blocks.height == height).select().last()
    return templates.TemplateResponse("block_section_1.html", 
                                        {
                                            "request": request,
                                            "Block":Block ,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })        


@app.post("/block/{number}/tx")
def txperblock(request: Request,number:str):
    response=json.loads(requests.get(url_api_educhain+'api/v2/blocks/%s/transactions'%(number)).content)
    for item in response["items"]:
        TxDetail(item["hash"])


@app.post("/block/{number}")
def Block2db(request: Request,number:str):
    #baseurl=str(request.base_url)
    
    if number=="last":
        response=json.loads(requests.get(url_api_educhain+"api/v2/blocks?type=block").content)
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

@app.get("/block/section_2/{number}", response_class=HTMLResponse)
def block_section_2(request: Request,number:str):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    
    height=int(number)
    Block = db(db.blocksbach.block_heightOCS == height).select().last()
    print(Block)
    return templates.TemplateResponse("block_section_2.html", 
                                        {
                                            "request": request,
                                            "Block":Block ,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })    


def BlockDetail(block):
    try:
        response=json.loads(requests.get(url_api_educhain+"api/v2/blocks/%s"%(block)).content)
        data=select_item_block(response)
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
    response=json.loads(requests.get(url_api_educhain+"api/v2/blocks/%s"%(block)).content)
    output=select_item_bachOCS2ARB(block,response)
    return output
def bachARB2ETH(output):
    response=json.loads(requests.get(url_api_arbitrum+"api/v2/blocks/%s"%(output['l1_block_heightARB'])).content)
    output=select_item_bachARB2ETH(output,response)
    return output
def bachETH2ETH(output):
    response=json.loads(requests.get(url_api_ethereum+"api/v2/blocks/%s"%(output['l1_block_heightETH'])).content)
    output=select_item_bachETH2ETH(output,response)
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




def TxVerif(hash):
    response=json.loads(requests.get(url_api_educhain+"api/v2/transactions/%s"%(hash)).content)
    item=response
    tx=select_items_tx(item)
    return {"message":"OK","block":tx["block"]}

def TxDetail(hash):
    try:
        response=json.loads(requests.get(url_api_educhain+"api/v2/transactions/%s"%(hash)).content)
        item=response
        tx=select_items_tx(item)
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
    #baseurl=str(request.base_url)

    s = db(db.txs.hash == hash)
    if s.count()==0:
        data=TxVerif(hash)
        height=int(data["block"])
        s = db(db.blocks.height == height)
        if s.count()==0:
            requests.post(baseurl+"/block/%s"%(height))
        s = db(db.txs.hash == hash)
        Tx=s.select().last().as_dict()
    else:
        Tx=s.select().last().as_dict()
    

    return templates.TemplateResponse("tx.html", {"request": request,"Tx":Tx,"recaptcha_site_key":recaptcha_site_key})


#Wallet
def isContract(hash: str,find_online:bool = True) -> int:
    """
    Checks if a given hash corresponds to a smart contract on the Blockscout platform.

    Args:
        hash (str): The hash of the contract to verify.

    Returns:
        int: Returns 1 if the hash corresponds to a smart contract, 0 in is a wallet and 2 if no verificated yet.
    """
    s = db(db.wallets.hash == hash)
    if s.count()==0:
        if find_online:
            url = url_api_educhain+f'api/v2/smart-contracts/{hash}'
            response = requests.get(url)
            if response.status_code == 200:
                return 1
            else: 
                return 0
        else:
            return 2
    else:
        data=s.select().last().as_dict()
        return data["is_contract"]



def contractsDetail(hash):
    response=json.loads(requests.get(url_api_educhain+"api/v2/smart-contracts/%s"%(hash)).content)
    data=select_item_contract(response)
    if "source_code" in data.keys() and data["source_code"]!="No code to analysis":
        
        DetailContract=LLMC.AnalysisContract(keygroq,data["source_code"])
        try:
            DetailContract=json.loads(DetailContract)
        except:
            DetailContract=json.loads(DetailContract[DetailContract.find("{"):DetailContract.find("}")+1])
        data["functionality"]=DetailContract["Functionality Analysis"]
        data["sectoruse"]=DetailContract["Sector and Use Classification"]
        data["issues"]=DetailContract["Identification of Potential Issues"]
        data["summary"]=DetailContract["Summary and Recommendations"]
    else:
        data["functionality"]="No code to analysis"
        data["sectoruse"]="No code to analysis"
        data["issues"]="No code to analysis"
        data["summary"]="No code to analysis"
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
    #baseurl=str(request.base_url)
    towallet = requests.get(url_api_educhain+'api/v2/addresses/%s/transactions?filter=to'%(hash))
    fromwallet = requests.get(url_api_educhain+'api/v2/addresses/%s/transactions?filter=from'%(hash))
    for source in [towallet,fromwallet]:
        for item in json.loads(source.content)["items"]:
            height=int(item["block_number"])
            s = db(db.blocks.height == height)
            if s.count()==0:
                requests.post(baseurl+"/block/%s"%(height))
    return {"message":"OK"}


@app.post("/wallet/{wallet}")
def getwalletorcontract2db(request: Request,wallet:str):
    output={}
    hash=wallet
    #baseurl=str(request.base_url)
    if isContract(hash)==0:
        output['hash']=hash
        output['is_contract']=0
        db.wallets.insert(**output)
        db.commit()
        return {"message":"OK"}
    else:
        output['hash']=hash
        output['is_contract']=1
        db.wallets.insert(**output)
        db.commit()
        contractsDetail(hash) 
        #requests.post(baseurl+"/wallet/%s/tx"%(hash))
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
    #baseurl=str(request.base_url)

    s = db(db.wallets.hash == wallet)
    if s.count()==0:
        requests.post(baseurl+"/wallet/%s"%(wallet))
    requests.post(baseurl+"/wallet/%s/tx"%(wallet))
    Tx=[]
    data={}
    s = db(db.wallets.hash == wallet).select().last()
    data["hash"]=wallet
    if s["is_contract"]==1:
        data["Type"]="Contract"
        contract = db(db.contracts.hash == wallet).select().last()
        data["source code"]=contract['source_code']
        data["Vyper contract"]=contract['is_vyper_contract']
        data["Is fully verified"]=contract['is_fully_verified']
        data["Blueprint"]=contract['is_blueprint']
        data["Verified at:"]=contract['verified_at']
        data["Verified"]=contract['is_verified']
        data["Name"]=contract['name']
        data["Language"]=contract['language']
        data["Compiler version"]=contract['compiler_version']
        data["Evm version"]=contract['evm_version']
        data["Funtionality"]=transform_text2formatedtext(contract['functionality'])
        data["Sector Use"]=contract['sectoruse']
        data["Issues"]=transform_text2formatedtext(contract['issues'])
        data["summary"]=transform_text2formatedtext(contract['summary'])

    else:
        data["Type"]="Wallet"
        
    Tx=requests.get(baseurl+"/wallet/%s/tx"%(wallet)).content
    Result,ranking_to, ranking_from=search_data(wallet)
    len0=[len(Result),len(ranking_to),len(ranking_from)]
    
    if data["Type"]=="Contract":
        if data["source code"] !="No code to analysis":
            return templates.TemplateResponse("wallet_contract.html", {"request": request,
            "Tx":Tx,
            "data":data,
            "res":Result,
            "ranking_to": ranking_to,
            "ranking_from": ranking_from,
            "enumerate": enumerate,
            "Type":data["Type"],
            "len0":len0,
            "recaptcha_site_key":recaptcha_site_key})
        else: 
            return templates.TemplateResponse("wallet_contract_without_source.html", {"request": request,
            "Tx":Tx,
            "data":data,
            "res":Result,
            "ranking_to": ranking_to,
            "ranking_from": ranking_from,
            "enumerate": enumerate,
            "Type":data["Type"],
            "len0":len0,
            "recaptcha_site_key":recaptcha_site_key})
    if data["Type"]=="Wallet":
                return templates.TemplateResponse("wallet_user.html", {"request": request,
        "Tx":Tx,
        "data":data,
        "res":Result,
        "ranking_to": ranking_to,
        "ranking_from": ranking_from,
        "enumerate": enumerate,
        "Type":data["Type"],
        "recaptcha_site_key":recaptcha_site_key})
    
@app.get("/wallet/{wallet}/activityweekhour", response_class=HTMLResponse)
def activity_week_hour(request: Request,wallet: str):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """



    summary = db.txs.day_week, db.txs.hour, db.txs.hash.count()
    rows = db(db.txs.fromw == wallet or db.txs.tow == wallet).select(*summary, groupby=(db.txs.day_week, db.txs.hour))
    summary_blocks_day_week_hour={}
    if len(rows)< 3:
        return templates.TemplateResponse("root_section_5.html", 
                                        {
                                            "request": request,
                                            "summary_blocks_day_week_hour":summary_blocks_day_week_hour,
                                            "percentils":[1,2,3],
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

    
    
    for row in rows:
        summary_blocks_day_week_hour[str(row.txs.day_week)+"-"+str(row.txs.hour)]=row[db.txs.hash.count()]
    data=[]
    for row in summary_blocks_day_week_hour.keys():
        data.append(summary_blocks_day_week_hour[row])
    percentils=[np.percentile(data, 25),np.percentile(data, 50),np.percentile(data, 75)]
    return templates.TemplateResponse("root_section_5.html", 
                                        {
                                            "request": request,
                                            "summary_blocks_day_week_hour":summary_blocks_day_week_hour,
                                            "percentils":percentils,
                                            "enumerate": enumerate,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })






@app.get("/wallet/{wallet}/activity", response_class=HTMLResponse)
def walletactivity(request: Request,wallet: str):
    """
    Renders a page with all  metrics of Educhain.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'indexV2.html' template with metrics.
    """
    summary = db.txs.timestamp, db.txs.hash.count()

    rows = db(db.txs.fromw == wallet or db.txs.tow == wallet).select(*summary, groupby=db.txs.timestamp)

    summary_block_day={}
    if len(rows)< 3:
        return templates.TemplateResponse("root_section_6.html", 
                                        {
                                            "request": request,
                                            "enumerate": enumerate,
                                            "list_summary_block_day":[],
                                            "percentils":[1,2,3],
                                            "recaptcha_site_key":recaptcha_site_key
                                            })

    for row in rows:
        if row[db.txs.timestamp].strftime('%Y-%m-%d') not in summary_block_day:
            summary_block_day[row[db.txs.timestamp].strftime('%Y-%m-%d')]= row[db.txs.hash.count()]
        else:
            summary_block_day[row[db.txs.timestamp].strftime('%Y-%m-%d')]+= row[db.txs.hash.count()]
    list_summary_block_day=[]
    data=[]
    for date in summary_block_day.keys():
        count=summary_block_day[date]
        list_summary_block_day.append(
            {"date": date, "count": count }
        )
        data.append(count)
    percentils=[np.percentile(data, 25),np.percentile(data, 50),np.percentile(data, 75)]

    return templates.TemplateResponse("root_section_6.html", 
                                        {
                                            "request": request,
                                            "enumerate": enumerate,
                                            "list_summary_block_day":list_summary_block_day,
                                            "percentils":percentils,
                                            "recaptcha_site_key":recaptcha_site_key
                                            })


@app.get("/wallet/{wallet}/ranking", response_class=HTMLResponse)
def walletranking(request: Request,wallet: str):
    """
    Renders a page with metrics of Transactions.

    Args:
        request (Request): The request object.

    Returns:
        HTMLResponse: Renders the 'index.html' template with metrics.
    """
    Result,ranking_to, ranking_from=search_data(wallet)
    len0=[len(Result),len(ranking_to),len(ranking_from)]
    return templates.TemplateResponse("wallet_ranking.html", {"request": request,
        "res":Result,
        "ranking_to": ranking_to,
        "ranking_from": ranking_from,
        "enumerate": enumerate,
        "len0":len0,
        "recaptcha_site_key":recaptcha_site_key})


@app.get("/wallet/{wallet}/tx")
def TxsInOut(request: Request,wallet: str):
    txs = db((db.txs.fromw == wallet) | (db.txs.tow == wallet) )
    alltx=[]
    for tx in txs.select():
        
        alltx.append(tx.as_dict())
    return alltx

def sorted_actions(walletsactions: Dict[str, int]) -> List[Tuple[str, int]]:
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

def color_wallet(wallet:str,walletverif:str):
    if wallet==walletverif:
        return "#4b4d4c"
    if isContract(walletverif,find_online=False)==1:
        return "#744b97"
    if isContract(walletverif,find_online=False)==2:
        return "#122fe5"
    if isContract(walletverif,find_online=False)==0:
        return "#808000"


def search_data(wallet: str):
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
    output = []
    temp1=[]
    temp2=[]
    ranking_to = {}
    ranking_from = {}

    # Retrieve wallet information from the database
    txs = db((db.txs.fromw == wallet) | (db.txs.tow == wallet) ).select()
    inserted=set()

    for tx in txs:
        data = {}
        data = {'data': {'id': tx["hash"], 'source': tx["fromw"], 'target': tx["tow"], 'width': 3}}
        ranking_to[tx["tow"]] = ranking_to.get(tx["tow"], 0) + 1
        ranking_from[tx["fromw"]] = ranking_from.get(tx["fromw"], 0) + 1
        if not tx["tow"] in inserted:

            temp2.append({'data': {'id': tx["tow"], 'url': tx["tow"], 'color': color_wallet(wallet,tx["tow"])}})
        if not tx["fromw"] in inserted:
            temp2.append({'data': {'id': tx["fromw"], 'url': tx["fromw"], 'color': color_wallet(wallet,tx["fromw"])}})
        temp1.append(data)
    output=temp2+temp1
    
    # Get the top wallets by actions as sources and targets
    return output,sorted_actions(ranking_to) , sorted_actions(ranking_from)

def categoriedb2json(categoryT="tx_count",tableT="blocks"):
    category=db[tableT][categoryT]
    table=db[tableT]
    query = category.count()
    print(table)
    result = db(table).select(category, query, groupby=category)
    
    return json.dumps({r[tableT][categoryT]: r[query] for r in result})



@app.post("/stadist_site")
def stadist_site():

    data={
    "n_wallets" : db(db.wallets).count(),
    "n_contracts" : db(db.contracts).count()   ,             
    "n_contracts_is_vyper_contract" : db(db.contracts.is_vyper_contract==True).count(),
    "n_contracts_is_verified" : db(db.contracts.is_verified==True).count()  ,
    "n_contracts_language" :categoriedb2json(categoryT="language",tableT="contracts"),         
    "n_contracts_evm_version" :categoriedb2json(categoryT="evm_version",tableT="contracts") ,
    "n_txs" : db(db.txs).count() , 
    "n_txs_not_success" : db(db.txs.result!="success").count(),
    "n_blocks" : db(db.blocks).count() ,
    "n_blocks_tx_count" :categoriedb2json(categoryT="tx_count",tableT="blocks"),
    "n_blocks_miner":categoriedb2json(categoryT="miner",tableT="blocks")
    }
    db.stadists_site.insert(**data)
    db.commit()
    return



@app.get("/verifendpoint")
def Verif_end_point():
    n=0
    Salida={}
    # for i in [json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/blocks?type=block").content)["items"][0],
    #           json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/stats").content),
    #           json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/transactions?filter=validated").content)["items"][0],
    #     json.loads(requests.get('https://edu-chain-testnet.blockscout.com/api/v2/blocks/%s/transactions'%(10)).content)["items"][0],
    #     json.loads(requests.get("https://edu-chain-testnet.blockscout.com/api/v2/blocks?type=block").content)["items"][0],
    #     json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/blocks/%s"%(10)).content),
    #     json.loads(requests.get("https://arbitrum-sepolia.blockscout.com/api/v2/blocks/%s"%(10)).content),
    #     json.loads(requests.get("https://eth-sepolia.blockscout.com/api/v2/blocks/%s"%(10)).content),
    #     json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/transactions/%s"%("0xbEc6E1B3cc11E14c039A998c292147e8610810b4")).content),
    #     json.loads(requests.get("https://opencampus-codex.blockscout.com/api/v2/smart-contracts/%s"%("0xd819d9457F0272e1DAccf52d2DEed44079aeF25A")).content),
    #     json.loads(requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=to'%("0x59F3BfDA995b9235e2a9F126eB2eeA5E0B443428")).content)["items"][0],
    #     json.loads(requests.get('https://opencampus-codex.blockscout.com/api/v2/addresses/%s/transactions?filter=from'%("0x59F3BfDA995b9235e2a9F126eB2eeA5E0B443428")).content)["items"][0]
    #     ]:
        
    monitor = APIMonitor(
    endpoints=[
            url_api_educhain+"api/v2/blocks?type=block",
            url_api_educhain+"api/v2/stats",
            url_api_educhain+"api/v2/transactions?filter=validated",
            url_api_educhain+'api/v2/blocks/%s/transactions'%(10),
            url_api_educhain+"api/v2/blocks?type=block",
            url_api_educhain+"api/v2/blocks/%s"%(10),
            url_api_arbitrum+"api/v2/blocks/%s"%(10),
            url_api_ethereum+"api/v2/blocks/%s"%(10),
            url_api_educhain+"api/v2/transactions/%s"%("0x2e81c3a9d0D58A98C07Ec4D0520AB914C6A1FcEd"),
            url_api_educhain+"api/v2/smart-contracts/%s"%("0x1C0c5190a7528d86496a5D2C78549dA702b74a4E"),
            url_api_educhain+'api/v2/addresses/%s/transactions?filter=to'%("0x2e81c3a9d0D58A98C07Ec4D0520AB914C6A1FcEd"),
            url_api_educhain+'api/v2/addresses/%s/transactions?filter=from'%("0x2e81c3a9d0D58A98C07Ec4D0520AB914C6A1FcEd")
        ]
    )

    changes = monitor.check_changes()

    for change in changes:
        print(f"Cambio detectado en {change.endpoint}:")
        print(f"  Campo: {change.field_name}")
        print(f"  Valor anterior: {change.old_value}")
        print(f"  Valor nuevo: {change.new_value}")
        print(f"  Timestamp: {change.timestamp}")

    
    select_stadistics_index( json.loads(requests.get(url_api_educhain+"api/v2/stats").content))
    select_item_block(json.loads(requests.get(url_api_educhain+"api/v2/blocks?type=block").content)["items"][0])
    dataOCS=select_item_bachOCS2ARB(10,json.loads(requests.get(url_api_educhain+"api/v2/blocks/%s"%(10)).content))
    dataOCS=select_item_bachARB2ETH(dataOCS,json.loads(requests.get(url_api_arbitrum+"api/v2/blocks/%s"%(10)).content))
    dataOCS=select_item_bachETH2ETH(dataOCS,json.loads(requests.get(url_api_ethereum+"api/v2/blocks/%s"%(10)).content))
    select_items_tx(json.loads(requests.get(url_api_educhain+"api/v2/transactions?filter=validated").content)["items"][0])
    select_items_tx(json.loads(requests.get(url_api_educhain+'api/v2/blocks/%s/transactions'%(10)).content)["items"][0])
    select_item_contract(json.loads(requests.get(url_api_educhain+"api/v2/smart-contracts/%s"%("0x1C0c5190a7528d86496a5D2C78549dA702b74a4E")).content))
    return Salida

@dataclass
class APIChange:
    timestamp: str
    field_name: str
    old_value: str
    new_value: str
    endpoint: str

class APIMonitor:
    def __init__(self, endpoints: List[str], cache_file: str = "api_schema_cache.json"):
        """
        Init evaluation of API.
        
        Args:
            endpoints: List of URL
            cache_file: file of status of API
        """
        self.endpoints = endpoints
        self.cache_file = cache_file
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Confg of logging."""
        logger = logging.getLogger('APIMonitor')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('api_changes.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _get_endpoint_schema(self, url: str) -> Dict:
        """
        get schema of a  endpoint.
        
        Args:
            url: URL of endpoint
            
        Returns:
            dict of endpoint
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error al obtener el esquema de {url}: {str(e)}")
            return {}
            
    def _load_cached_schema(self) -> Dict:
        """load schema"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def _save_schema_cache(self, schema: Dict):
        """Save schema in cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(schema, f, indent=2)
            
    def _extract_field_names(self, data: Dict, prefix: str = '') -> Set[str]:
        """
        Extrae recursivamente todos los nombres de campos de un diccionario.
        
        Args:
            data: Diccionario a analizar
            prefix: Prefijo para campos anidados
            
        Returns:
            Conjunto de nombres de campos
        """
        fields = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            fields.add(full_key)
            
            if isinstance(value, dict):
                fields.update(self._extract_field_names(value, full_key))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                fields.update(self._extract_field_names(value[0], full_key))
                
        return fields
        
    def check_changes(self) -> List[APIChange]:
        """
        Verifica cambios en los nombres de campos de la API.
        
        Returns:
            Lista de cambios detectados
        """
        changes = []
        cached_schema = self._load_cached_schema()
        current_schema = {}
        
        for endpoint_url in self.endpoints:
            current_response = self._get_endpoint_schema(endpoint_url)
            if not current_response:
                continue
                
            current_schema[endpoint_url] = current_response
            current_fields = self._extract_field_names(current_response)
            
            if endpoint_url in cached_schema:
                cached_fields = self._extract_field_names(cached_schema[endpoint_url])
                
                
                for field in cached_fields - current_fields:
                    change = APIChange(
                        timestamp=datetime.now().isoformat(),
                        field_name=field,
                        old_value=field,
                        new_value="REMOVED",
                        endpoint=endpoint_url
                    )
                    changes.append(change)
                    self.logger.warning(f"Campo eliminado: {field} en {endpoint_url}")
                
                
                for field in current_fields - cached_fields:
                    change = APIChange(
                        timestamp=datetime.now().isoformat(),
                        field_name=field,
                        old_value="NEW",
                        new_value=field,
                        endpoint=endpoint_url
                    )
                    changes.append(change)
                    self.logger.warning(f"Nuevo campo detectado: {field} en {endpoint_url}")
        
        
        if current_schema:
            self._save_schema_cache(current_schema)
            
        return changes