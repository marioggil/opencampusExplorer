
from datetime import datetime

def change_date_format(date):
    date=date.split("T")
    date_p1=date[0].split("-")
    date_p2=date[1].split(".")[0].split(":")
    date_final=str(date_p1[0])+"-"+str(date_p1[1])+"-"+str(date_p1[2])+" "+str(date_p2[0])+":"+str(date_p2[1])+":"+str(date_p2[2])
    
    return date_final


def select_stadistics_index(item):
    data={}
    for key in ['network_utilization_percentage','total_blocks','total_transactions',
                'transactions_today','total_addresses','gas_used_today','average_block_time']:
        try:
            if item[key] is None:
                pass
            else:
                if key=='average_block_time':
                    data[key]=int(item['average_block_time'])
                else:
                    data[key]=item[key]
        except:
            print("___________")
            print("select_stadistics_index error", key)
            print("Orig",item.keys() )

    return data


def select_item_block(item):
    data={}
    for key in ["hash",'height','size','miner','difficulty','burnt_fees','base_fee_per_gas','parent_hash','total_difficulty','transaction_count','timestamp',"gas_used",'transaction_fees','gas_limit']:
        try:
            if item[key] is None:
                pass
            else:
                if key=='miner':
                    data[key]=item[key]["hash"]
                elif key=='height'  or key=="gas_used" or key=='tx_count' or key== 'gas_limit' or key=='total_difficulty' or key=='base_fee_per_gas' or key=='difficulty' or key=="burnt_fees":
                    data[key]=int(item[key])
                elif key=="transaction_fees":
                    data['tx_fees']=int(item[key])
                elif key=="transaction_count":
                    data['tx_count']=int(item[key])
                elif key=="timestamp":
                    data[key]=change_date_format(item[key])
                else:
                    data[key]=item[key]
        except:
            print("select_item_block error", key)
            print("Orig",item.keys() )
    date_calcs=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
    data["day_week"]=date_calcs.strftime('%A')
    data["day_month"]=date_calcs.day
    data["hour"]=date_calcs.strftime('%H')
    return data


def select_item_bachOCS2ARB(block,response):
    item=response['arbitrum']
    dataOCS={}
    dataOCS['block_heightOCS']=block
    dataOCS["hash"]=response["hash"]
    dataOCS["status"]="OK"
    for key in ['batch_number','l1_block_height']:
        try:
            if item[key] is None:
                pass
            else:
                if key=='batch_number':
                    dataOCS['batch_numberOCS']=item[key]
                
                elif key=='l1_block_height':
                    dataOCS['l1_block_heightARB']=item[key]
                else:
                    dataOCS[key]=item[key]
        except:
            print("select_item_block error", key)
            print("Orig",item.keys() )
            dataOCS["status"]="incomplete"
    return dataOCS


def select_item_bachARB2ETH(dataOCS,response):
    
    for key in ['arbitrum',"priority_fee","total_difficulty","transaction_fees","burnt_fees","difficulty","gas_limit","gas_used"]:
        try:
            if response[key] is None:
                pass
            else:
                if key=='arbitrum':
                    dataOCS['batch_numberARB']=response['arbitrum']['batch_number']
                    dataOCS['l1_block_heightETH']=response['arbitrum']['l1_block_height']
                else:
                    dataOCS[key+"ARB"]=response[key]
        except:
            print("select_item_block error", key)
            print("Orig",response.keys() )
            dataOCS["status"]="incomplete"
    return dataOCS


def select_item_bachETH2ETH(dataOCS,response):
    for key in ["total_difficulty","transaction_fees","burnt_fees","difficulty","gas_limit","gas_used","priority_fee",]:
        try:
            if response[key] is None:
                pass
            else:
                dataOCS[key+"ETH"]=response[key]
        except:
            print("select_item_block error", key)
            print("Orig",response.keys() )
            dataOCS["status"]="incomplete"
    return dataOCS



def select_items_tx(item):
    data={}
    for key in ['timestamp',"fee",'block_number','method',"from",'tx_burnt_fee',"hash",'priority_fee','transaction_types','gas_used','created_contract',"to",'result','revert_reason','transaction_tag','has_error_in_internal_transactions']:
        try:
            if item[key] is None:
                pass
            else:
                if key=="to": 
                    data["tow"]=item[key]["hash"]
                elif key=="from": 
                    data["fromw"]=item[key]["hash"]
                elif key=='created_contract':
                    data[key]=item[key]["hash"]
                elif key=="block_number":
                    data["block"]=item[key]
                elif key=="tx_types":
                    data["tx_types"]=item[key]
                elif key=="fee" :
                    data[key]=int(item[key]["value"])
                elif key =="gas_used":
                    data[key]=int(item[key])
                elif key=="timestamp":
                    data[key]=change_date_format(item[key])
                else:
                    data[key]=item[key]
        except:
            print("select_items_tx error", key)
            print("Orig",item.keys() )

    date_calcs=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
    data["day_week"]=date_calcs.strftime('%A')
    data["day_month"]=date_calcs.day
    data["hour"]=date_calcs.strftime('%H')
    return data


def select_item_contract(item):
    data={}
    for key in ["is_vyper_contract",'is_fully_verified','is_blueprint','source_code','verified_at','is_verified',
                'name','language','compiler_version','evm_version']:
        try:
            if item[key] is None:
                pass
            else:
                data[key]=item[key]
        except:
            print("select_item_contract error", key)
            print("Orig",item.keys() )
            if key in ["is_vyper_contract",'is_fully_verified','is_blueprint','is_verified']:
                data[key]=False
            else:
                data[key]="No code to analysis"
    return data

    