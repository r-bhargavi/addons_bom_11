odoo.define("website_pos.model", function (require) {
    "use strict";

    var pos_model = require('point_of_sale.models');
    var models = pos_model.PosModel.prototype.models;
    var Model = require('web.DataModel');

    pos_model.load_fields("product.product", "unavailable_in_pos");

    for (var i = 0; i < models.length; i++) {
    var model = models[i];
    if (model.model === 'product.product') {
        model.domain =  [['sale_ok','=',true],['available_in_pos','=',true],['unavailable_in_pos','=',false]];
    };
}
});