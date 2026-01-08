/** @odoo-module **/

import MainComponent from '@stock_barcode/components/main';
import { patch } from "@web/core/utils/patch";

patch(MainComponent.prototype, {
    async createPackaging(ev) {
        ev.stopPropagation();
        await this.env.model.save();
        try {
            const result = await this.orm.call(
                this.resModel,
                'action_packaging_create',
                [[this.resId]]
            );
            if (typeof result === 'object') {
                await this.action.doAction(result);
            } else {
                await this.action.loadState();
            }
        } catch (error) {
            const message = error.data?.message || error.message || 'An error occurred';
            this.env.services.notification.add(message, { type: 'danger' });
        }
    }
});
