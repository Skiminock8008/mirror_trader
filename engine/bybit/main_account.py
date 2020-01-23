import sys
import threading,keyboard
from tkinter import Entry, Label,Tk, scrolledtext,Button
import bybit
import 

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')

from modules.helper import *

list_clients(get_clients(), 'bybit')

print("Bybit copy trader started!")

f=open('main_account.txt','r')
lines=f.readlines()
f.close()
if len(lines)==0:
    print("No main api key!")
    sys.exit()
if(len(lines[0].split())<3):
    print("Main api key info is less!")
    sys.exit()
main_key=lines[0].split()[0]
main_secret=lines[0].split()[1]
if(lines[0].split()[2]=='testnet'):
    test_flag=True
else:
    test_flag=False
main_client  = bybit.bybit(test=test_flag, api_key=main_key, api_secret=main_secret)

f=open('copy_clients.txt','r')
lines=f.readlines()
f.close()
if len(lines)==0:
    print("No client api keys!")
    sys.exit()
slave_keys=lines
slave_clients=[]
accounts=[]
for key in slave_keys:
    if len(key.split())<4:
            continue
    api=key.split()[0]
    secret=key.split()[1]
    accounts.append(key.split()[3])
    if(lines[0].split()[2]=='testnet'):
        test_flag=True
    else:
        test_flag=False
    clt=bybit.bybit(test=test_flag, api_key=api, api_secret=secret)
    slave_clients.append(clt)    
id_list=[]

pre_result=main_client.Order.Order_getOrders(limit=5).result()

if pre_result[0]['ret_msg']!='ok':
    print('Main API key problem: '+pre_result[0]['ret_msg'])
    sys.exit()
    
pre_orders=pre_result[0]['result']['data']

def getPrice(client,symbol):
    price=client.Market.Market_symbolInfo(symbol='BTCUSD').result()[0]['result'][0]['last_price']
    return price;

def getCoinBalance(client,symbol):
    this_currency=symbol[0:3]
    balance=client.Wallet.Wallet_getRecords(currency=this_currency,limit='1').result()[0]['result']['data'][0]['wallet_balance']
    return balance;

def getUsdBalance(client,symbol):
    price=getPrice(client, symbol);
    balance=getCoinBalance(client, symbol);
    return int(float(price)*float(balance))

def watcher():
    global pre_orders
    global slave_keys
    global main_client
    global slave_clients
    
    def order_exist(order, orders):
        for ord in orders:
            if order['order_id']==ord['order_id']:
                return True
        return False
    def copy_order(from_balance,order,index):
        clt=slave_clients[index]
        od=order['side']
        sb=order['symbol']
        ot=order['order_type']
        qt=order['qty']
        pr=order['price']
        tf=order['time_in_force']
        ##############################################
        from_percent=qt/from_balance
        to_usd_balance=getUsdBalance(clt, sb)
        to_qty=str(int(to_usd_balance*from_percent))
        ##############################################
        ost=order['order_status']
        if ost=="Untriggered":
            bp=order['ext_fields']['base_price']
            tp=order['ext_fields']['trigger_price']
            result=clt.Conditional.Conditional_new(order_type=ot,side=od,symbol=sb,qty=to_qty,price=pr,base_price=bp,stop_px=tp,time_in_force="GoodTillCancel").result()
        else:
            result=(clt.Order.Order_new(side=od,symbol=sb,order_type=ot,qty=to_qty,price=pr,time_in_force=tf).result())
        if result[0]['ret_msg']!='ok':
            print(key[0]+' '+result[0]['ret_msg'])
            print('Bye.. See you again! :)')
            sys.exit()
        print('Order placed into '+accounts[index]+'  New qty is '+to_qty) 
        if ost=="Untriggered":
            return [result[0]['result']['stop_order_id'],to_qty]
        return [result[0]['result']['order_id'],to_qty]
               
    def copy_orders(order,keys):
        print("New order detected!")
        main_usd_balance=getUsdBalance(main_client, order['symbol']);
        o_id=order['order_id']
        ids=[]
        ids.append(o_id)
        index=0
        for key in keys:
            o_id=copy_order(main_usd_balance,order,index)
            index+=1
            ids.append(o_id)
        return ids
    res=main_client.Order.Order_getOrders(limit=5).result()[0]
    if(res['ret_msg']!='ok'):
        return
    orders=res['result']['data']
    #print(orders)
    if orders!=[] :
        for order in orders:
            if order_exist(order, pre_orders)==False:
                ids=copy_orders(order,slave_keys)
                global id_list
                id_list.append(ids)
                continue
            status=order['order_status']
            m_id=order['order_id']
            if(status=='Filled' and len(id_list)>0):
                for ids in id_list:
                    if(m_id==ids[0]):
                        id_list.remove(ids) 
            elif(status=='Cancelled' and len(id_list)>0):
                for ids in id_list:
                    if(m_id==ids[0]):
                        print("Order cancel detected...")
                        id_list.remove(ids)
                        i=0
                        for s_id in ids[1:]:
                            clt=slave_clients[i]
                            clt.Order.Order_cancel(order_id=s_id[0]).result()
                            i+=1
            elif(status=='Deactivated' and len(id_list)>0):
                for ids in id_list:
                    if(m_id==ids[0]):
                        print("Conditional order cancel detected...")
                        id_list.remove(ids)
                        i=0
                        for s_id in ids[1:]:
                            clt=slave_clients[i]
                            clt.Conditional.Conditional_cancel(stop_order_id=s_id[0]).result()
                            i+=1
            elif(len(id_list)>0):
                cur_id=order['order_id']
                cur_price=order['price']
                cur_qty=order['qty']
                od=order['side']
                sb=order['symbol']
                ot=order['order_type']
                tf=order['time_in_force']
                for pre_order in pre_orders:
                    pre_id=pre_order['order_id']
                    pre_price=pre_order['price']
                    pre_qty=pre_order['qty']
                    ost=order['order_status']
                    if ost=="Untriggered":
                        cur_tp=order['ext_fields']['trigger_price']
                    pre_ost=pre_order['order_status']
                    if pre_ost=="Untriggered":
                        pre_tp=pre_order['ext_fields']['trigger_price']
                    if(cur_id==pre_id and (cur_price!=pre_price or cur_qty!=pre_qty or (ost=="Untriggered" and pre_ost=="Untriggered" and pre_tp!=cur_tp))):
                        print("Order change detected!")
                        for ids in id_list:
                            if(cur_id==ids[0]):
                                i=0
                                for s_id in ids[1:]:
                                    clt=slave_clients[i]
                                    #to_qty=cur_qty;
                                    to_qty=float(s_id[1])*cur_qty/pre_qty;
                                    if ost=="Untriggered":
                                        clt.Conditional.Conditional_cancel(stop_order_id=s_id[0]).result()
                                        bp=order['ext_fields']['base_price']
                                        tp=order['ext_fields']['trigger_price']
                                        re=clt.Conditional.Conditional_new(order_type=ot,side=od,symbol=sb,qty=to_qty,price=cur_price,base_price=bp,stop_px=tp,time_in_force="GoodTillCancel").result()
                                    else:
                                        clt.Order.Order_cancel(order_id=s_id[0]).result()
                                        re=(clt.Order.Order_new(side=od,symbol=sb,order_type=ot,qty=to_qty,price=cur_price,time_in_force=tf).result())
                                    if re[0]['ret_msg']!='ok':
                                        print(key[0]+' '+re[0]['ret_msg'])
                                        print('Bye... See you again! :)')
                                        sys.exit()
                                    if ost=="Untriggered":    
                                        new_id=[re[0]['result']['stop_order_id'],to_qty]
                                    else:
                                        new_id=[re[0]['result']['order_id'],to_qty]
                                    id_list[id_list.index(ids)][ids.index(s_id)]=new_id
                                    i+=1
        pre_orders=orders
        print('Not found new order... ...')        

def g_hotkey_process():
    print('g pressed, GUI !')
    
    window = Tk()
    window.title(":)")
    window.geometry('830x250')
    
    ApiLabel=Label(window,text="Main API")
    ApiLabel.grid(column=0,row=0)
    ApiText=Entry(window,width=30)   
    ApiText.grid(column=0,row=1) 
     
    SecretLabel=Label(window,text="Main Secret")
    SecretLabel.grid(column=1,row=0)
    SecretText=Entry(window,width=50)   
    SecretText.grid(column=1,row=1)  
      
    AccountLabel=Label(window,text="Main Account net")
    AccountLabel.grid(column=2,row=0)
    AccountText=Entry(window,width=20)   
    AccountText.grid(column=2,row=1)
    
    SlaveLabel=Label(window,text="Slave API keys ( API, Secret, Account)")
    SlaveLabel.grid(column=0,row=2,columnspan=3)
    SlaveArea = scrolledtext.ScrolledText(window,width=100,height=10)
    SlaveArea.grid(column=0,row=3,columnspan=3)    
    
    def save():
        f=open('main_account.txt','w')
        f.write(ApiText.get()+' '+SecretText.get()+' '+AccountText.get()+'\n')
        f.close()
        f=open('copy_clients.txt','w')
        f.write(SlaveArea.get('1.0','end-1c'))
        f.close()
    
    SaveButton=Button(window,text='Save',command=save)
    SaveButton.config(width=10)
    SaveButton.grid(column=1,row=4)
    
    def load():
        f=open('main_account.txt','r')
        lines=f.readlines()
        f.close()
        ApiText.insert(0, lines[0].split()[0])
        SecretText.insert(0, lines[0].split()[1])
        AccountText.insert(0, lines[0].split()[2])
        f=open('copy_clients.txt','r')
        lines=f.readlines()
        f.close()
        for line in lines:
            SlaveArea.insert('insert',line)
        
    load()
       
    window.mainloop() 
    
def main():
    print('Hello bybit! CopyTrader started!')
    # keyboard.add_hotkey('g', g_hotkey_process)

    while True:
        watcher()
        time.sleep(3)
        
if __name__ == '__main__':
    main()