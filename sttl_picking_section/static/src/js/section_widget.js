/** @odoo-module **/

import { registry } from "@web/core/registry";
import { StockMoveX2ManyField, MovesListRenderer } from '@stock/views/picking_form/stock_move_one2many';
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";
import { ProductLabelSectionAndNoteListRender } from '@account/components/product_label_section_and_note_field/product_label_section_and_note_field';
import {
    SectionAndNoteListRenderer,
    sectionAndNoteFieldOne2Many,
} from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import { Component, useEffect } from "@odoo/owl";
import { ListRenderer } from "@web/views/list/list_renderer";


export class StockMoveCustomListRender extends ListRenderer {
    static template = "sttl_picking_section.ListRenderer";

    setup() {
        super.setup();
        this.productColumns = ["product_id", "product_template_id"];
        this.titleField = "name";
        useEffect(
            (editedRecord) => this.focusToName(editedRecord),
            () => [this.editedRecord]
        )
    }
    
    focusToName(editRec) {
        if (editRec && editRec.isNew && this.isSectionOrNote(editRec)) {
            const col = this.columns.find((c) => c.name === this.titleField);
            this.focusCell(col, null);
        }
    }

    isSectionOrNote(record=null) {
        record = record || this.record;
        return ['line_section', 'line_note'].includes(record.data.display_type);
    }

    getRowClass(record) {
        const existingClasses = super.getRowClass(record);
        return `${existingClasses} o_is_${record.data.display_type}`;
    }

    getCellClass(column, record) {
        const classNames = super.getCellClass(column, record);
        if (this.isSectionOrNote(record) && column.widget !== "handle" && column.name !== this.titleField) {
            return `${classNames} o_hidden`;
        }
        return classNames;
    }

    getColumns(record) {
        const columns = super.getColumns(record);
        if (this.isSectionOrNote(record)) {
            return this.getSectionColumns(columns);
        }
        return columns;
    }

    getSectionColumns(columns) {
        const sectionCols = columns.filter((col) => col.widget === "handle" || col.type === "field" && col.name === this.titleField);
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return { ...col, colspan: columns.length - sectionCols.length + 1 };
            } else {
                return { ...col };
            }
        });
    }

    getCellTitle(column, record) {
        // When using this list renderer, we don't want the product_id cell to have a tooltip with its label.
        if (this.productColumns.includes(column.name)) {
            return;
        }
        super.getCellTitle(column, record);
    }

    getActiveColumns(list) {
        let activeColumns = super.getActiveColumns(list);
        const productCol = activeColumns.find((col) => this.productColumns.includes(col.name));
        const labelCol = activeColumns.find((col) => col.name === "name");

        if (productCol) {
            if (labelCol) {
                list.records.forEach((record) => (record.columnIsProductAndLabel = true));
            } else {
                list.records.forEach((record) => (record.columnIsProductAndLabel = false));
            }
            activeColumns = activeColumns.filter((col) => col.name !== "name");
            this.titleField = productCol.name;
        } else {
            this.titleField = "name";
        }

        return activeColumns;
    }
}


export class PickingSectionAndNoteListRenderer extends StockMoveCustomListRender{
    static recordRowTemplate = "sttl_picking_section.PickingSectionAndNoteListRenderer";

    static props = [...ListRenderer.props];
    setup() {
        super.setup();
        useEffect(
            () => {
                this.keepColumnWidths = false;
            },
            () => [this.columns]
        );
    }

    processAllColumn(allColumns, list) {
        let cols = super.processAllColumn(...arguments);
        if (list.resModel === "stock.move") {
            cols.push({
                type: 'opendetailsop',
                id: `column_detailOp_${cols.length}`,
                column_invisible: 'parent.state=="draft"',
            });
        }
        return cols;
    }
}

class CombinedX2ManyField extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: PickingSectionAndNoteListRenderer, 
    };

    setup() {
        super.setup();

        this.canOpenRecord = true;

        this.getCustomFieldValue = () => {
            return this.props.record?.data?.custom_field || "";
        };
    }

    async openRecord(record) {
        if (this.canOpenRecord && !record.isNew) {
            const dirty = await record.isDirty();
            if (await record._parentRecord.isDirty() || (dirty && 'quantity' in record._changes)) {
                await record._parentRecord.save({ reload: true });
                record = record._parentRecord.data[this.props.name].records.find(e => e.resId === record.resId);
                if (!record) {
                    return;
                }
            }
        }
        return super.openRecord(record);
    }
}

export const combinedx2ManyField = {
    ...x2ManyField,
    component: CombinedX2ManyField,
    additionalClasses: [
        ...(x2ManyField.additionalClasses || []),
        ...(sectionAndNoteFieldOne2Many.additionalClasses || [])
    ],
};

registry.category("fields").add("combined_one2many", combinedx2ManyField);
