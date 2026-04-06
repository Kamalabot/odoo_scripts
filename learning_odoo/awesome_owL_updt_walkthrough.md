# OWL Tutorial Exercises Walkthrough

I have implemented all the tutorial exercises in the `awesome_owl` addon. Here's a summary of the changes:

## 1. Reactivity Experiment
In `Counter.js`, I replaced `useState` with a plain object:
```javascript
this.state = { value: 1 };
```
> [!NOTE]
> Since `this.state` is no longer reactive, clicking "Increment" in the UI will update the value in memory but **will not** trigger a re-render. You'll notice the "Local" count stays at 1.

## 2. Counter Component Enhancements
- **Step Prop**: Added a `step` prop to `Counter`. It now increments by the specified step (defaulting to 1). One instance in the Playground uses `step="2"`.
- **onWillUpdateProps**: Added a lifecycle hook to log when the `onChange` prop changes.
- **useEnv / Shared State**: Created a reactive `sharedState` in `main.js` and shared it via the environment. All `Counter` components now display and update this shared value.

## 3. Card Component: Named Slots
Added a `footer` slot to the `Card` component. In `Playground.xml`, I demonstrated this by adding a button to the card footer.
```xml
<Card title="'Card with footer'">
    This card has a footer!
    <t t-set-slot="footer">
        <button class="btn btn-sm btn-outline-secondary">Footer Action</button>
    </t>
</Card>
```

## 4. TodoList: Filtering
Added a "Show active only" checkbox to the `TodoList`. It uses a reactive state `isFilterActive` and a getter `filteredTodos` to dynamically filter the list of todos.

## 5. New Component: ProgressBar
Created a reusable `ProgressBar` component located in `static/src/progress_bar/`.
- **Props**: `value` (Number) and `color` (String, optional).
- **Styling**: Uses Bootstrap 5 progress bar classes.
- **Integration**: One instance in the Playground is bound to the shared state value, so it moves as you click the counters!

## Changes Summary

- [MODIFY] [main.js](file:///opt/odoo/tutorials/awesome_owl/static/src/main.js)
- [MODIFY] [counter.js](file:///opt/odoo/tutorials/awesome_owl/static/src/counter/counter.js)
- [MODIFY] [counter.xml](file:///opt/odoo/tutorials/awesome_owl/static/src/counter/counter.xml)
- [MODIFY] [card.js](file:///opt/odoo/tutorials/awesome_owl/static/src/card/card.js)
- [MODIFY] [card.xml](file:///opt/odoo/tutorials/awesome_owl/static/src/card/card.xml)
- [MODIFY] [todo_list.js](file:///opt/odoo/tutorials/awesome_owl/static/src/todo_list/todo_list.js)
- [MODIFY] [todo_list.xml](file:///opt/odoo/tutorials/awesome_owl/static/src/todo_list/todo_list.xml)
- [NEW] [progress_bar.js](file:///opt/odoo/tutorials/awesome_owl/static/src/progress_bar/progress_bar.js)
- [NEW] [progress_bar.xml](file:///opt/odoo/tutorials/awesome_owl/static/src/progress_bar/progress_bar.xml)
- [MODIFY] [playground.js](file:///opt/odoo/tutorials/awesome_owl/static/src/playground.js)
- [MODIFY] [playground.xml](file:///opt/odoo/tutorials/awesome_owl/static/src/playground.xml)
