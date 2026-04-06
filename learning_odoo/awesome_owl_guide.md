# 🦉 Awesome OWL — Learning Guide

This guide walks you through the **`awesome_owl`** tutorial module, explaining every concept you'll encounter in Odoo's OWL (Odoo Web Library) frontend framework.

---

## 📁 Project Structure

```
awesome_owl/
├── __manifest__.py          ← Module definition & asset bundles
├── controllers/
│   └── controllers.py       ← Python HTTP route → serves the playground page
├── views/
│   └── templates.xml        ← Odoo QWeb template that bootstraps the HTML page
└── static/src/
    ├── main.js              ← Entry point: mounts root component
    ├── playground.js        ← Root component (Playground)
    ├── playground.xml       ← Root component template
    ├── utils.js             ← Shared custom hook (useAutofocus)
    ├── counter/
    │   ├── counter.js       ← Counter component
    │   └── counter.xml      ← Counter template
    ├── card/
    │   ├── card.js          ← Card component (with slots)
    │   └── card.xml         ← Card template
    └── todo_list/
        ├── todo_model.js    ← Plain JS model classes (Todo, TodoModel)
        ├── todo_list.js     ← TodoList component
        ├── todo_list.xml    ← TodoList template
        ├── todo_item.js     ← TodoItem component
        └── todo_item.xml    ← TodoItem template
```

---

## 🔌 How It Boots (The Full Request Flow)

```
Browser hits /awesome_owl
     ↓
controllers.py  →  renders  views/templates.xml
     ↓
templates.xml loads asset bundle  awesome_owl.assets_playground
     ↓
main.js runs  →  mounts  Playground  component onto  document.body
     ↓
OWL renders template  awesome_owl.playground  (playground.xml)
     ↓
Child components: Counter, Card, TodoList rendered recursively
```

---

## 📚 Core OWL Concepts — File by File

---

### 1. `main.js` — Entry Point

```js
import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { Playground } from "./playground";

whenReady(() => mountComponent(Playground, document.body, { dev: true }));
```

**Key concepts:**
| Concept | What it does |
|---|---|
| `whenReady()` | Waits for the DOM to be ready before running |
| `mountComponent()` | OWL entrypoint — mounts a component as the root |
| `dev: true` | Enables OWL dev mode (extra warnings & checks) |

---

### 2. `playground.js` + `playground.xml` — Root Component

```js
export class Playground extends Component {
    static template = "awesome_owl.playground";   // links to XML template
    static components = { Counter, Card, TodoList }; // registers child components

    setup() {
        this.str1 = "<div class='text-primary'>some content</div>";
        this.str2 = markup("<div class='text-primary'>some content</div>");
        this.sum = useState({ value: 2 });  // reactive state
    }

    incrementSum() {
        this.sum.value++;
    }
}
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| `static template` | Points to the QWeb template name in the `.xml` file |
| `static components` | Declares which child components this template can use |
| `setup()` | OWL lifecycle hook — like React's constructor/useEffect combo |
| `useState()` | Makes an object **reactive** — UI re-renders when values change |
| `markup()` | Marks a string as **safe HTML** so `t-out` renders it as real HTML (not escaped) |
| `.bind` in `onChange.bind="incrementSum"` | Automatically binds `this` to the method |

**Template (`playground.xml`):**
```xml
<Counter onChange.bind="incrementSum" />   <!-- passes a prop -->
<t t-esc="sum.value"/>                    <!-- outputs text (HTML-escaped) -->
<Card title="'card 1'">                   <!-- string prop with quotes-in-quotes -->
    content of card 1                     <!-- → goes into t-slot="default" -->
</Card>
```

> [!NOTE]
> `t-esc` escapes HTML (safe), while `t-out` renders raw HTML (use with `markup()` only).

---

### 3. `counter/counter.js` — State & Props & Events

```js
export class Counter extends Component {
    static props = {
        onChange: { type: Function, optional: true }  // optional prop
    };

    setup() {
        this.state = useState({ value: 1 });
    }

    increment() {
        this.state.value++;
        if (this.props.onChange) {
            this.props.onChange();  // call parent callback
        }
    }
}
```

```xml
<!-- counter.xml -->
<button t-on-click="increment">Increment</button>
<t t-esc="state.value"/>
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| `static props` | Declares what props the component accepts (type-checked in dev mode) |
| `{ type: Function, optional: true }` | Prop is optional; won't throw if not passed |
| `this.props.onChange` | Access props inside the class |
| `t-on-click="increment"` | Attaches a DOM event listener to a method |
| Callback prop pattern | Parent passes a function → child calls it when something happens |

---

### 4. `card/card.js` + `card.xml` — Slots (Content Projection)

```js
static props = {
    title: String,
    slots: {
        type: Object,
        shape: { default: true }  // declares a default slot
    }
};

setup() {
    this.state = useState({ isOpen: true });
}

toggleContent() {
    this.state.isOpen = !this.state.isOpen;
}
```

```xml
<!-- card.xml -->
<t t-if="state.isOpen">
    <t t-slot="default"/>      ← renders whatever the parent put between <Card>...</Card>
</t>
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| **Slots** | Like React children — parent injects content, child decides where to render it |
| `t-slot="default"` | Renders the default slot content inline |
| `slots` in static props | OWL requires you to declare slots in props for type-checking |
| `t-if` | Conditional rendering — renders element only if expression is truthy |
| Toggle pattern | `useState({ isOpen: true })` + `isOpen = !isOpen` is the standard toggle |

---

### 5. `todo_list/todo_model.js` — Model Classes

```js
export class Todo {
    static nextId = 1;     // class-level auto-increment ID

    constructor(model, description) {
        this._model = model;       // reference back to parent model
        this.id = Todo.nextId++;
        this.description = description;
        this.isCompleted = false;
    }

    toggle() { this.isCompleted = !this.isCompleted; }
    remove() { this._model.remove(this.id); }  // delegates to model
}

export class TodoModel {
    constructor() { this.todos = []; }

    add(description) {
        const todo = new Todo(this, description);
        this.todos.push(todo);
    }

    remove(id) {
        const idx = this.todos.findIndex(t => t.id === id);
        if (idx >= 0) this.todos.splice(idx, 1);
    }
}
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| **Model separation** | Business logic lives in plain JS classes, NOT in components |
| `static nextId` | Class property for shared auto-increment — no database needed |
| Back-reference pattern | `Todo` holds `this._model` to call model methods (`remove`) |
| `useState(new TodoModel())` | OWL makes the entire model **deeply reactive** |

> [!IMPORTANT]
> When you wrap a class instance with `useState()`, OWL tracks **all property mutations** on it recursively — including nested objects and arrays.

---

### 6. `todo_list/todo_list.js` — Using a Model + Custom Hook

```js
import { useAutofocus } from "../utils";

export class TodoList extends Component {
    setup() {
        this.model = useState(new TodoModel());  // reactive model
        useAutofocus("input");                   // custom hook
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value != "") {  // Enter key
            this.model.add(ev.target.value);
            ev.target.value = "";  // clear input
        }
    }
}
```

```xml
<!-- todo_list.xml -->
<input t-on-keyup="addTodo" t-ref="input"/>    ← t-ref names the element
<t t-foreach="model.todos" t-as="todo" t-key="todo.id">
    <TodoItem todo="todo"/>
</t>
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| `t-foreach` | Loops over an array |
| `t-as` | Variable name for each item in the loop |
| `t-key` | Unique key for efficient DOM reconciliation (like React's `key`) |
| `t-ref` | Creates a reference to a DOM element (used by `useAutofocus`) |
| **Enter key detection** | `ev.keyCode === 13` — standard pattern for form-less submission |

---

### 7. `todo_list/todo_item.js` + `todo_item.xml` — Props & Dynamic Attributes

```xml
<!-- todo_item.xml -->
<t t-set="todo" t-value="props.todo"/>        ← local alias for cleaner code

<input
    t-att-id="todo.id"                        ← dynamic attribute binding
    t-att-checked="todo.isCompleted"
    t-on-change="() => todo.toggle()"         ← inline arrow function
/>

<label
    t-att-for="todo.id"
    t-att-class="todo.isCompleted ? 'text-decoration-line-through text-muted' : ''"
>

<span t-on-click="() => todo.remove()"/>      ← calls model method directly
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| `t-att-*` | Dynamically sets any HTML attribute from an expression |
| `t-set` / `t-value` | Creates a local template variable (alias) |
| `() => todo.toggle()` | Inline arrow function in template event handler |
| `t-att-class` | Dynamic class names (ternary expression) |

---

### 8. `utils.js` — Custom Hooks

```js
import { useRef, onMounted } from "@odoo/owl";

export function useAutofocus(refName) {
    const ref = useRef(refName);       // get the t-ref reference
    onMounted(() => {
        ref.el.focus();                // focus element when component mounts
    });
}
```

**Key concepts:**

| Concept | Explanation |
|---|---|
| `useRef(refName)` | Gets a reference to a DOM element marked with `t-ref="refName"` |
| `onMounted()` | Lifecycle hook — runs **after** the component is inserted into the DOM |
| **Custom hooks** | Any function using OWL hooks = a "custom hook". Must be called in `setup()` |
| `ref.el` | The actual DOM element (could be `null` before mount) |

---

## 🗺️ OWL Template Directive Quick Reference

| Directive | Purpose | Example |
|---|---|---|
| `t-name` | Declares a template | `<t t-name="awesome_owl.Counter">` |
| `t-esc` | Output escaped text | `<t t-esc="state.value"/>` |
| `t-out` | Output raw HTML (use with `markup()`) | `<t t-out="str2"/>` |
| `t-if` / `t-elif` / `t-else` | Conditional rendering | `<div t-if="isVisible">` |
| `t-foreach` + `t-as` + `t-key` | List rendering | `<t t-foreach="items" t-as="item" t-key="item.id">` |
| `t-on-*` | DOM event handler | `t-on-click="handleClick"` |
| `t-att-*` | Dynamic attribute | `t-att-class="myClass"` |
| `t-ref` | DOM element reference | `<input t-ref="myInput"/>` |
| `t-slot` | Render slot content | `<t t-slot="default"/>` |
| `t-set` + `t-value` | Local template variable | `<t t-set="x" t-value="props.foo"/>` |
| `t-call-assets` | Load an asset bundle | `<t t-call-assets="bundle.name"/>` |

---

## 🔑 OWL Hooks Quick Reference

| Hook | When it runs | Use case |
|---|---|---|
| `useState(obj)` | Setup | Make reactive state |
| `useRef(name)` | Setup | Access a DOM element |
| `onMounted(fn)` | After first render | DOM access, focus, fetch data |
| `onWillUnmount(fn)` | Before unmount | Cleanup timers/subscriptions |
| `onWillUpdateProps(fn)` | Before props change | React to incoming prop changes |
| `useEnv()` | Setup | Access OWL environment |

---

## 🚀 Learning Path — What to Try Next

1. **Understand reactivity** — Change `useState` to a plain object and see what breaks
2. **Add a prop** — Add a `step` prop to `Counter` so it increments by `step` instead of 1
3. **Add a named slot** — Add a `footer` slot to `Card`
4. **Add a filter** — Add "Show active only" toggle to `TodoList`
5. **Use `onWillUpdateProps`** — Log when `Counter`'s `onChange` prop changes
6. **Create a new component** — Build a `ProgressBar` that takes `value` (0–100) as a prop
7. **Add `useEnv`** — Share state between `Counter` components via OWL environment

> [!TIP]
> Access your running playground at **`http://localhost:8069/awesome_owl`** after starting Odoo.
> The URL is defined in `controllers/controllers.py` and the asset bundle in `__manifest__.py`.

---

## ⚙️ How Asset Bundles Work

In `__manifest__.py`:
```python
'assets': {
    'awesome_owl.assets_playground': [
        ('include', 'web._assets_helpers'),   # SCSS helpers
        ('include', 'web._assets_bootstrap'), # Bootstrap
        ('include', 'web._assets_core'),      # OWL + Odoo core JS
        'awesome_owl/static/src/**/*',         # ALL files in src/ (glob)
    ],
}
```

In `views/templates.xml`:
```xml
<t t-call-assets="awesome_owl.assets_playground"/>  ← injects all JS/CSS
```

This is how Odoo serves frontend bundles — no Webpack config needed; Odoo handles the bundling.
