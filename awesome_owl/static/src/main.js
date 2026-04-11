import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { Playground } from "./playground";
import { sharedState } from "./shared_state";

const config = {
    name: "Owl Tutorial",
    translateFn: (s) => s,
};

// Mount the Playground component when the document.body is ready
whenReady(() => mountComponent(Playground, document.body, config));
