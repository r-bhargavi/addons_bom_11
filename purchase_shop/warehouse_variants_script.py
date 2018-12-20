#!/usr/bin/env python
# coding: utf-8

import xmlrpclib
import datetime


start_time = datetime.datetime.now()
print ("the Starting time is ====>>>>%s"%start_time)

#credentials of server
username = 'admin'
pwd = 'GrdPvrGrdsRspsblts!'
dbname = 'fonteyne-1-0'

#connecting to server
sock_common = xmlrpclib.ServerProxy ('http://mirror.fthek.be/xmlrpc/common', allow_none=True)
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://mirror.fthek.be/xmlrpc/object', allow_none=True)

#searching variants
variant_ids=sock.execute(dbname, uid, pwd,'product.product', 'search',[['product_tmpl_id.purchase_warehouse_ids','!=',False]])
print "variant_ids--------------------------------",variant_ids
#searching related templates
tmpl_ids=sock.execute_kw(dbname, uid, pwd,'product.product', 'read',[variant_ids], {'fields': ['product_tmpl_id']})
print "template ids----------------------",tmpl_ids

#to link variants with WH and unlink the WH from template
for each_tmpl in tmpl_ids:
    warehouse_ids=sock.execute_kw(dbname, uid, pwd,'product.template', 'read',[each_tmpl.get('product_tmpl_id')[0]], {'fields': 	          ['purchase_warehouse_ids']})
    if warehouse_ids.get('purchase_warehouse_ids')!=[]:
        #updating the warehouses in variants with warehouses linked in templates
        sock.execute_kw(dbname, uid, pwd, 'product.product', 'write', [[each_tmpl.get('id')],{'purchase_warehouse_variants': [(4,i) for i in 		warehouse_ids.get('purchase_warehouse_ids')]}])
        #deleting the templates linked warehouse after updating its variants
        sock.execute_kw(dbname, uid, pwd, 'product.template', 'write', [[each_tmpl.get('product_tmpl_id')[0]],{'purchase_warehouse_ids': [(5,i) 	for i in warehouse_ids.get('purchase_warehouse_ids')]}])
        print("Done")
    
    


