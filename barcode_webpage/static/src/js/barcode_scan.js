
odoo.define('barcode_webpage.barcode', function(require){
	"use strict";
	var core = require('web.core');
	var Dialog = require('web.Dialog');
	var Widget = require('web.Widget');
	var Model = require('web.DataModel');

	var QWeb = core.qweb;
	var _t = core._t;
	var _lt = core._lt;
	
	var ScanBarcode = Dialog.extend( {
		template: 'ScanBarcode',
		events: {
			'click #scanCode': 'scanBarCode',
			'keypress #product_barcode': 'doActionBarcode',
			'change #select_restaurant': 'getLastProduct',
		},
		init: function (parent, data) {
			this.context = data.context;
        	this._super.apply(this, arguments);
    	},
    	start: function(){
        	var self = this;
        	this.User = new Model('res.users');
        	var restaurantConfig = new Model('restaurant.picking.config');
        	this.User.call('read',[[this.context.uid],['restaurant_config_ids'],this.context]).done(function(res){
        		restaurantConfig.call('read',[res[0]['restaurant_config_ids'],['name']]).done(function(restaurants){
        			var options = QWeb.render('RestaurantList',{'restaurants':restaurants});
        			self.$el.find('#select_restaurant').append(options);
        			self.getLastProduct();

        		});
        	});
            self.$el.on('shown.bs.modal', function () { 
                self.$el.find('#product_barcode').focus();
            });
        	self.$el.modal('show');
            self.$el.find('#product_barcode').focus();
        	return self._super.apply(self, arguments);
        },
        doActionBarcode: function(ev){
        	var self = this;
        	if (ev.which === 13) {
        		self.scanBarCode();
    		}
        },
        scanBarCode: function(){
        	var self = this;
        	var rest_id = self.$el.find('#select_restaurant').val()
        	var barcode = self.$el.find('#product_barcode').val()
        	self.$el.find('#infoBox').html('');
        	if(rest_id && barcode){
        		this.User.call('scanProductBarcode',[rest_id,barcode]).done(function(resp){
        			var InfoBox = QWeb.render('InfoBox',resp);
        			self.$el.find('#infoBox').append(InfoBox);
        			self.$el.find('#product_barcode').val('');
                    self.$el.find('#product_barcode').focus();
        		});
        	}
        	else{
        		var InfoBox = QWeb.render('InfoBox',{'error': 'No field can be empty'});
        		self.$el.find('#infoBox').append(InfoBox);
        		self.$el.find('#product_barcode').val('');
                self.$el.find('#product_barcode').focus();
        	}
        },
        getLastProduct: function(){
        	var self = this;
        	var rest_id = self.$el.find('#select_restaurant').val()
        	console.log('change',rest_id);
        	self.$el.find('#infoBox').html('');
        	var InfoBox = QWeb.render('InfoBox',{'message': ''});
        	self.$el.find('#infoBox').append(InfoBox);
            self.$el.find('#product_barcode').focus();
            console.log('focused');
        }

	});

	core.action_registry.add('scanbarcode.ui', ScanBarcode);
});
