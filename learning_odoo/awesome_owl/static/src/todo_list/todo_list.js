import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item";
import { useAutofocus } from "../utils";
import { TodoModel } from "./todo_model";

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup() {
        this.model = useState(new TodoModel());
        this.state = useState({ isFilterActive: false });
        useAutofocus("input")
    }

    get filteredTodos() {
        if (this.state.isFilterActive) {
            return this.model.todos.filter((todo) => !todo.isCompleted);
        }
        return this.model.todos;
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value != "") {
            this.model.add(ev.target.value);
            ev.target.value = "";
        }
    }
}
