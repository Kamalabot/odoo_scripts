import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo_list/todo_list";
import { ProgressBar } from "./progress_bar/progress_bar";
import { sharedState } from "./shared_state";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList, ProgressBar };

    setup() {
        this.str1 = "<div class='text-primary'>some content</div>";
        this.str2 = markup("<div class='text-primary'>some content</div>");
        this.sum = useState({ value: 2 });
        this.sharedState = sharedState;
    }

    get sharedStateValue() {
        return this.sharedState.value;
    }

    incrementSum() {
        this.sum.value++;
    }
}
