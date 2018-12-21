import odoo
from odoo.tests import common

class TestData(common.SavepointCase):

    """Tests for diffrent scenarios of picking creation,merging and change of company"""

    def setUp(self):
        super(TestData, self).setUp()
        self.r_model_template = self.env['stock.picking.template']
        self.r_model_picking = self.env['stock.picking']
        
#        """Add some defaults to let the test run picking"""
        self.supplier_location = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_suppliers')
        print "supplier-------------------",self.supplier_location
        self.stock_location = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_stock')
        self.picking_type_int= self.env["stock.picking.type"].create({
            "name": "Test Picking type",
            "code": "internal",
            "sequence_id": 1,
        })
        self.partner = self.env["res.partner"].create({
            "name": "Test partner",
            "supplier": True,
            "is_company": True,
        })
        self.productA = self.env["product.product"].create({
            "name": "test product1",
            "type": "product",
            "categ_id": 1,
            "uom_id": self.env.ref('product.product_uom_unit').id,
            "uom_po_id": self.env.ref('product.product_uom_unit').id,
            "default_code": "CheckP1"
        })
        self.productB = self.env["product.product"].create({
            "name": "test product2",
            "type": "product",
            "categ_id": 1,
            "uom_id": self.env.ref('product.product_uom_unit').id,
            "uom_po_id": self.env.ref('product.product_uom_unit').id,
            "default_code": "CheckP2"
        })
        self.productC = self.env["product.product"].create({
            "name": "test productC",
            "type": "product",
            "categ_id": 1,
            "uom_id": self.env.ref('product.product_uom_unit').id,
            "uom_po_id": self.env.ref('product.product_uom_unit').id,
            "default_code": "CheckP3"
        })
        self.new_company=self.env['res.company'].create({
        'name':'Other Cmpny2'
        })
        print "new_companynew_companynew_company",self.new_company
