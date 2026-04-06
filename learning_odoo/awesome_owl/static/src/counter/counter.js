import { Component, onWillUpdateProps } from "@odoo/owl";
import { sharedState } from "../shared_state";

export class Counter extends Component {
    static template = "awesome_owl.Counter";
    static props = {
        onChange: { type: Function, optional: true },
        step: { type: Number, optional: true }
    };

    setup() {
        // Understand reactivity: plain object — UI won't re-render on change!
        this.state = { value: 1 };
        this.sharedState = sharedState;

        onWillUpdateProps((nextProps) => {
            if (nextProps.onChange !== this.props.onChange) {
                console.log("onChange prop changed!");
            }
        });
    }

    increment() {
        this.state.value = this.state.value + (this.props.step || 1);
        this.sharedState.value = this.sharedState.value + (this.props.step || 1);
        if (this.props.onChange) {
            this.props.onChange();
        }
    }
}
