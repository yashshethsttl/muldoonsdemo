/** @odoo-module **/

import { formView } from "@web/views/form/form_view";
import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";
import { executeButtonCallback } from "@web/views/view_button/view_button_hook";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

export class PreventSaveFormController extends FormController {
    static components = {
        ...FormController.components
    };

    setup() {
        console.log("setup");
        super.setup(...arguments);
        this.dialogService = useService("dialog");
    }

    saveButtonClicked(params = {}) {
        var root = this.model.root;
        this._openSaveConfirmationDialog(() => {
            return executeButtonCallback(this.ui.activeElement, () => this.save(params));
        }, () => {
            root.discard();
        });
    }

    async beforeLeave() {
        var root = this.model.root;
        console.log(root);
        if (root.dirty) {
            return new Promise((resolve) => {
                this._openSaveConfirmationDialog(async () => {
                    await root.urgentSave();
                    await root.model.load();
                    resolve(true);
                }, () => {
                    root.discard();
                    resolve(true);
                });
            });
        }
        return true;
    }

    beforeUnload() {
        var root = this.model.root;
        root.discard();
        return true;
    }

    _openSaveConfirmationDialog(onConfirm, onCancel) {
        this.dialogService.add(ConfirmationDialog, {
            title: _t("Save Confirmation"),
            body: _t("Do you want to save changes?"),
            confirmLabel: _t("Yes"),
            cancelLabel: _t("No"),
            confirm: onConfirm,
            cancel: onCancel,
        });
    }
}

export const PreventSaveForm = { ...formView, Controller: PreventSaveFormController };
registry.category("views").add("stock_form_auto_save", PreventSaveForm);