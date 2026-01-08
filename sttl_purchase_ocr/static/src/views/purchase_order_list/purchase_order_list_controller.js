/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { DocumentFileUploaderOCR } from "../../components/purchase_file_uploader/purchase_file_uploader"


export class PurchaseOrderListController extends ListController {
    static components = {
        ...ListController.components,
        DocumentFileUploaderOCR,
    };
}
