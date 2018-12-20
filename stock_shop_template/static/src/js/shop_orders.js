odoo.define('stock_shop_template.shop_orders', function (require) {
'use strict';

var website = require('website.website');
var ajax = require('web.ajax');

var the_form = $('.shop_order_page');

if(!the_form.length) {
    return $.Deferred().reject("DOM doesn't contain '.shop_order_page'");
}
console.log($("div.picking-item a"));
console.log($("a.picking-item"));

$("a.picking-item").on('click', function(e) {
        console.log(e.currentTarget);
        console.log($(e.currentTarget).parent());
        console.log($(e.currentTarget).parent().find(".picking-content"));
        $(e.currentTarget).parent().find(".picking-content").toggleClass('hidden').find('input').first().focus();
    });

$('.shop-order-form input[type=number]').on('keydown', function(e) {
    if (e.which == 13 || e.keyCode == 13 ) {
        e.preventDefault();
        console.log($(e.currentTarget));
        console.log($(e.currentTarget).next());
        console.log($(e.currentTarget).nextAll('input[type=number]'));
        $(e.currentTarget).closest('tr').next().find('input[type=number]').first().focus();
    }
});

$('.shop-order-form').on('focus', 'input[type=number]', function(e) {
        $(this).on('wheel', function(e) {
            e.preventDefault();
        });
    });
 
    // Restore scroll on number inputs.
    $('.shop-order-form').on('blur', 'input[type=number]', function(e) {
        $(this).off('wheel');
    });
 
    // Disable up and down keys.
    $('.shop-order-form').on('keydown', 'input[type=number]', function(e) {
        if ( e.which == 38 || e.which == 40 )
            e.preventDefault();
    });  

$('.shop-order-form button[type=submit]').click(function(e){
        e.preventDefault();
        console.log($(e.currentTarget));
        $(e.currentTarget).prop("disabled","disabled")
        console.log(e.currentTarget);
        console.log($(e.currentTarget).parent().parent().parent());
        var picking_complete = $(e.currentTarget).parent().parent().parent();
        var picking_id = picking_complete.data('picking_id');
        var move_lines = [];
        console.log(picking_id);
         $(e.currentTarget).parent().find('tbody tr').each(function(index, tr){
            console.log(tr);
            console.log($(tr).data('move_id'));
            console.log($(tr).find('input').val());
            
            move_lines.push([1, $(tr).data('move_id'),{product_uom_qty : $(tr).find('input').val() ? parseFloat($(tr).find('input').val()) : 0.0}]);
            
         });
         console.log(move_lines);
         ajax.jsonRpc('/web/dataset/call', 'call', {
                model: 'stock.picking',
                method: 'read',
                args: [parseInt(picking_id),
                   ['state']],
            }).then(function(res){
                console.log(res);
                if(res.state === 'draft'){
                    ajax.jsonRpc('/web/dataset/call', 'call', {
                    model: 'stock.picking',
                    method: 'write',
                    args: [parseInt(picking_id),
                       {'move_lines':move_lines}],
                    }).then(function(res){
                        console.log(res);
                        console.log('success');

                            ajax.jsonRpc('/web/dataset/call', 'call', {
                    model: 'stock.picking',
                    method: 'read',
                    args: [parseInt(picking_id),
                       ['state']],
                    }).then(function(res){

                        console.log(res);
                        if(res.state === 'draft'){ 
                            ajax.jsonRpc('/web/dataset/call', 'call', {
                            model: 'stock.picking',
                            method: 'action_confirm',
                            args: [parseInt(picking_id),
                              ]
                            }).then(function(){
                                console.log('picking_validated !');
                                picking_complete.find('a span').replaceWith('<span class="badge badge-success">Done</span>');
                                picking_complete.find('.picking-content').remove();
                            })
                        }
                    })}).fail(function(source,error){
                        console.log('error');
                        console.log(source);
                        console.log(error);
                });
                }
                else{
                    console.log("picking was not in draft state");
                    picking_complete.find('a span').replaceWith('<span class="badge badge-error">Error, please refresh</span>');
                    picking_complete.find('.picking-content').remove();
                }
            });
            });

         

});