# Copyright 2023 Quartile Limited
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpSubcontractingSkipNoNegative(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_stock_no_negative=True,
            )
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        picking_form.partner_id = cls.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.finished
            move.product_uom_qty = 1
        cls.subcontracting_receipt = picking_form.save()

    def _create_stock_quant(self, product, qty):
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "location_id": self.subcontractor_partner1.property_stock_subcontractor.id,
                "quantity": qty,
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_mrp_subcontracting_skip_no_negative_01(self):
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(immediate_wizard.get("res_model"), "stock.immediate.transfer")
        immediate_wizard_form = Form(
            self.env[immediate_wizard["res_model"]].with_context(
                **immediate_wizard["context"]
            )
        ).save()
        # Component1 error
        with self.assertRaises(ValidationError) as e1:
            immediate_wizard_form.process()
        self.assertIn("Component1", str(e1.exception))
        # Create comp1 stock, and try subcontracting receipt process.
        self._create_stock_quant(self.comp1, 10)
        # Component2 error
        with self.assertRaises(ValidationError) as e2:
            immediate_wizard_form.process()
        self.assertIn("Component2", str(e2.exception))
        # Create comp2 stock, and subcontracting receipt should now be successful.
        self._create_stock_quant(self.comp2, 10)
        immediate_wizard_form.process()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_skip_no_negative_03(self):
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(immediate_wizard.get("res_model"), "stock.immediate.transfer")
        immediate_wizard_form = Form(
            self.env[immediate_wizard["res_model"]].with_context(
                **immediate_wizard["context"]
            )
        ).save()
        immediate_wizard_form.process()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_skip_no_negative_04(self):
        self.subcontractor_partner1.property_stock_subcontractor.allow_negative_stock = (
            True
        )
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(immediate_wizard.get("res_model"), "stock.immediate.transfer")
        immediate_wizard_form = Form(
            self.env[immediate_wizard["res_model"]].with_context(
                **immediate_wizard["context"]
            )
        ).save()
        immediate_wizard_form.process()
        self.assertEqual(self.subcontracting_receipt.state, "done")

    def test_mrp_subcontracting_with_normal_product(self):
        another_product = self.env["product.product"].create(
            {
                "name": "Another Product",
                "type": "product",
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": self.subcontracting_receipt.id,
                "product_id": another_product.id,
                "name": another_product.name,
                "product_uom": another_product.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.subcontracting_receipt.location_id.id,
                "location_dest_id": self.subcontracting_receipt.location_dest_id.id,
            }
        )
        self._create_stock_quant(self.comp1, 10)
        self._create_stock_quant(self.comp2, 10)
        self.subcontracting_receipt.action_confirm()
        self.assertEqual(self.subcontracting_receipt.state, "assigned")
        immediate_wizard = self.subcontracting_receipt.sudo().button_validate()
        self.assertEqual(immediate_wizard.get("res_model"), "stock.immediate.transfer")
        immediate_wizard_form = Form(
            self.env[immediate_wizard["res_model"]].with_context(
                **immediate_wizard["context"]
            )
        ).save()
        immediate_wizard_form.process()
        self.assertEqual(self.subcontracting_receipt.state, "done")
        products = self.subcontracting_receipt.move_ids.mapped("product_id")
        self.assertIn(self.finished, products)
        self.assertIn(another_product, products)
        for move in self.subcontracting_receipt.move_ids:
            self.assertEqual(move.quantity_done, 1)
