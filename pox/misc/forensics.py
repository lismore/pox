''' Forensics Class for PoX SDN Controller '''
from . import forensicsutil
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
#from __future__ import print_function
import requests, json

mylogger = core.getLogger()

class Forensics (EventMixin):

   def __init__ (self):
    self.listenTo(core.openflow)
    mylogger.debug("Starting Forensics Module")
    print "Forensics instance registered"

   def test(self):
    print "Forensic instance registered"

   def LogEvent(self, message):
    # Login information for my node
    rpc_user = "multichainrpc"
    rpc_password = "78v21ut6APgaDPPfwRDnksDctm3aocKZvXiATWK9nyx1"
    rpc = AuthServiceProxy("http://%s:%s@10.0.0.6:18332/" % (rpc_user, rpc_password))

    first_unspent = rpc.listunspent()[0]
    txid = first_unspent['txid']
    vout = first_unspent['vout']
    input_amount = first_unspent['amount']
    SATOSHI = Decimal("0.01")
    change_amount = input_amount - Decimal("0.01") - SATOSHI
    # Produces a pattern that's easy to search for
    mainnet = 0
    if mainnet:
      dummy_address = "1111111111111111111114oLvT2"
    else:
      dummy_address = "mfWxJ45yp2SFn7UciZyNpvDKrzbhyfKrY8"

    # My change address
    change_address = "mhZuYnuMCZLjZKeDMnY48xsR5qkjq7bAr9"

    tx = rpc.createrawtransaction([{"txid": txid, "vout": vout}], \
                              {change_address: change_amount, \
                               dummy_address: SATOSHI})

    oldScriptPubKey = "1976a914000000000000000000000000000000000000000088ac"

    # Data to insert
    data = message
    if len(data) > 75:
      raise Exception("Can't contain this much data-use OP_PUSHDATA1")

    newScriptPubKey = "6a" + hexlify(chr(len(data))) + hexlify(data)

    #Append int of length to start
    newScriptPubKey = hexlify(chr(len(unhexlify(newScriptPubKey)))) + newScriptPubKey


    if oldScriptPubKey not in tx:
       raise Exception("Something broke!")

    tx = tx.replace(oldScriptPubKey, newScriptPubKey)

    rpc.decoderawtransaction(tx)
    tx = rpc.signrawtransaction(tx)['hex']
    rpc.sendrawtransaction(tx)

   def GetBlockchain(self):
    print "Blockchain Online"
    rpcPort = 4792
    rpcUser = 'multichainrpc'
    rpcPassword = '78v21ut6APgaDPPfwRDnksDctm3aocKZvXiATWK9nyx1'
    serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@10.0.0.6:' + str(rpcPort)
    headers = {'content-type': 'application/json'}
    payload = json.dumps({"method": 'getinfo', "jsonrpc": "2.0"})
    response = requests.get(serverURL, headers=headers, data=payload)
    print(response.json()['result'])

   def GetEvents(self): 
    print "Blockchain Record"

   def get(api_code = None):
    """Get network statistics.
    
    :return: an instance of :class:`Stats` class
    """
    
    resource = 'stats?format=json'
    if api_code is not None:
        resource += '&api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return Stats(json_response)
   
   def get_block(block_id, api_code = None):
    """Get a single block based on a block index or hash.
    
    :param str block_id: block hash or index to look up
    :return: an instance of :class:`Block` class
    """
    
    resource = 'rawblock/' + block_id
    if api_code is not None:
        resource += '?api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return Block(json_response)

   def get_tx(tx_id, api_code = None):
    """Get a single transaction based on a transaction index or hash.
    
    :param str block_id: transaction hash or index to look up
    """
    
    resource = 'rawtx/' + tx_id
    if api_code is not None:
        resource += '?api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return Transaction(json_response)

   def get_block_height(height, api_code = None):
    """Get an array of blocks at the specified height.
    
    :param int height: block height to look up
    :return: an array of :class:`Block` objects
    """
    
    resource = 'block-height/{0}?format=json'.format(height)
    if api_code is not None:
        resource += '&api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return [Block(b) for b in json_response['blocks']]

   def get_address(address, api_code = None):
    """Get data for a single address.
    
    :param str address: address to look up
    :return: an instance of :class:`Address` class
    """
    
    resource = 'rawaddr/' + address
    if api_code is not None:
        resource += '?api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return Address(json_response)
    
   def get_unspent_outputs(address, api_code = None):
    """Get unspent outputs for a single address.
    
    :param str address: address to look up
    :return: an array of :class:`UnspentOutput` objects
    """
    
    resource = 'unspent?active=' + address
    if api_code is not None:
        resource += '&api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return [UnspentOutput(o) for o in json_response['unspent_outputs']]

   def get_latest_block(api_code = None):
    """Get the latest block on the main chain.
    
    :return: an instance of :class:`LatestBlock` class
    """
    
    resource = 'latestblock'
    if api_code is not None:
        resource += '?api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return LatestBlock(json_response)
    
   def get_unconfirmed_tx(api_code = None):
    """Get a list of currently unconfirmed transactions.
    
    :return: an array of :class:`Transaction` objects
    """
    
    resource = 'unconfirmed-transactions?format=json'
    if api_code is not None:
        resource += '&api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return [Transaction(t) for t in json_response['txs']]

   def get_blocks(time = None, pool_name = None, api_code = None):
    """Get a list of blocks for a specific day or mining pool.
    Both parameters are optional but at least one is required.
    
    :param int time: time in milliseconds
    :param str pool_name: name of the mining pool
    :return: an array of :class:`SimpleBlock` objects
    """
    
    resource = 'blocks/{0}?format=json'
    if api_code is not None:
        resource += '&api_code=' + api_code
    if time is not None:
        resource = resource.format(time)
    elif pool_name is not None:
        resource = resource.format(pool_name)
    else:
        resource = resource.format('')
        
    response = util.call_api(resource)
    json_response = json.loads(response)
    return [SimpleBlock(b) for b in json_response['blocks']]

   def get_inventory_data(hash, api_code = None):
    """Get inventory data.
    
    :param str hash: tx or block hash
    :return: an instance of :class:`InventoryData` class
    """
    resource = 'inv/{0}?format=json'.format(hash)
    if api_code is not None:
        resource += '&api_code=' + api_code
    response = util.call_api(resource)
    json_response = json.loads(response)
    return InventoryData(json_response)

def launch():
    '''
    Forensics module Started
    '''
    core.registerNew(Forensics)

