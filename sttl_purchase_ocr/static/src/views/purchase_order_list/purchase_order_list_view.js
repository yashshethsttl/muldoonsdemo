/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { PurchaseOrderListController } from "./purchase_order_list_controller";
import { ListRenderer } from "@web/views/list/list_renderer";

export const purchaseOrderUploadListViewOCR = {
    ...listView,
    Controller: PurchaseOrderListController,
    Renderer: ListRenderer,
    buttonTemplate: "sttl_purchase_ocr.DocumentViewUploadButtonOCR",
};

registry.category("views").add("purchase_tree_ocr", purchaseOrderUploadListViewOCR);
