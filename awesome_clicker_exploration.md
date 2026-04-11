# Awesome Clicker Tutorial Module

The `awesome_clicker` folder is a companion tutorial module for the Odoo JS Framework (OWL) training. It implements a "clicker" game integrated directly into the Odoo backend.

## 📂 Folder Structure

- `__init__.py` & `__manifest__.py`: Standard Odoo module files. The manifest defines dependencies (`web`, `base`) and loads all assets into `web.assets_backend`.
- `static/src/`: Contains the core logic and UI of the game.
    - `clicker_model.js`: The "brain" of the game. Uses OWL's `Reactive` class to manage game state (clicks, levels, bots, trees, etc.).
    - `clicker_service.js`: An Odoo service that:
        - Initializes the `ClickerModel`.
        - Persists game state to `localStorage`.
        - Listens to global click events (`document.addEventListener("click", ...)`).
        - Handles Odoo-specific effects like "Rainbow Man" upon reaching milestones.
        - Provides the clicker instance to other components via the Odoo service registry.
    - `clicker_systray_item/`: Implements the icon in the Odoo top bar (systray).
        - Shows current click count and fruit status.
        - Allows opening the main game interface.
    - `client_action/`: The main full-screen game interface. Registered as an Odoo client action.
    - `clicker_hook.js`: A custom OWL hook (`useClicker`) to easily access the clicker service in components.
    - `click_rewards.js`: Defines rewards and their application logic.
    - `clicker_migration.js`: Logic for handling state versioning and migrations.
    - `clicker_value/`: A specialized component to display animated "click" values.
    - `utils.js`: Helper functions (e.g., `choose` for random rewards).

## 🚀 Key Concepts Demonstrated

1.  **Reactive State Management**: How to use `Reactive` to create a globally shared state that components can automatically react to.
2.  **Odoo Services**: How to create and register a service (`registry.category("services").add(...)`) to manage long-lived logic and state.
3.  **Systray Integration**: Adding items to the Odoo top bar.
4.  **Client Actions**: Building custom full-page or modal-based UIs in Odoo.
5.  **Event Bus**: Using OWL `EventBus` for communication between the model and the UI.
6.  **Hooks**: Creating reusable patterns to access services or state.
7.  **Persistence**: Interacting with browser `localStorage` within the Odoo framework.
8.  **Odoo UI Services**: Integrating with standard Odoo services like `notification` and `effect`.

## 🎮 How it Works

1.  The `clicker_service` starts when the Odoo backend loads.
2.  Every click anywhere in the Odoo interface increments the click counter in the `ClickerModel`.
3.  As you gain clicks, you reach "Milestones" which trigger visual effects and unlock new "Bots" or "Trees".
4.  Bots and Trees generate clicks or fruits automatically over time via a `tick` interval.
5.  Status is always visible in the Systray, and the full game can be opened for purchasing upgrades.
