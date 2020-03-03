# Copyright 2020 RGB Consulting
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.addons.website_sale_options.controllers.main import WebsiteSaleOptions


class WebsiteSaleOptionsPopup(WebsiteSaleOptions):

    @http.route(['/shop/cart/update_option'], type='http', auth="public", methods=['POST'], website=True, multilang=False)
    def cart_options_update_json(self, product_id, add_qty=1, set_qty=0, goto_shop=None, lang=None, **kw):
        if lang:
            request.website = request.website.with_context(lang=lang)
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order(force_create=True)
        product = request.env['product.product'].browse(int(product_id))
        option_ids = product.optional_product_ids.mapped('product_variant_ids').ids
        p_option_ids = product.mapped('product_variant_ids').ids
        optional_product_ids = []
        p_product_variant_id = None
        for k, v in kw.items():
            if "optional-product-" in k and int(kw.get(k.replace("product", "add"))) and int(v) in option_ids:
                optional_product_ids.append(int(v))
            if "product-variant-" in k and str(kw.get(k.replace("product", "add"))) and int(v) in p_option_ids:
                p_product_variant_id = int(v)
        attributes = self._filter_attributes(**kw)
        value = {}
        if (add_qty or set_qty) and p_product_variant_id:
            value = order._cart_update(
                product_id=p_product_variant_id,
                add_qty=add_qty,
                set_qty=set_qty,
                attributes=attributes,
                optional_product_ids=optional_product_ids
            )
        # options have all time the same quantity
        for option_id in optional_product_ids:
            order._cart_update(
                product_id=option_id,
                set_qty=value.get('quantity'),
                attributes=attributes,
                linked_line_id=value.get('line_id')
            )
        return str(order.cart_quantity)
