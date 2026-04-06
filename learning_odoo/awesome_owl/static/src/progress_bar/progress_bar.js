import { Component } from "@odoo/owl";

export class ProgressBar extends Component {
    static template = "awesome_owl.ProgressBar";
    static props = {
        value: { type: Number },
        color: { type: String, optional: true }
    };
}
