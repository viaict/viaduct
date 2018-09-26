import Vue from "vue"
import App from "./components/app.vue"
import PimpyTask from "./components/pimpy_task.vue"


import {init as SentryInit, Integrations} from "@sentry/browser/dist";


SentryInit({
    dsn: 'https://d20fbd1634454649bd8877942ebb5657@sentry.io/1285048',
    release: '1.0.0',
    environment: 'maico',
    // debug: true,
    integrations: [new Integrations.Vue()]

});

// This makes sure that only the vue component is loaded on pages that support it.
if (document.querySelector('#app')) {
    console.log("Vue app has been detected.");
    new Vue({
        el: '#app',
        render: h => h(App)
    });
}

// Pimpy version, cannot use render function yet as we define custom element in
// Jinja e.g. <tr is="pimpy-task" :id="..." ...></tr>.
if (document.querySelector('#pimpy_app')) {
    console.log("Pimpy app has been detected.");

    new Vue({
        el: '#pimpy_app',
        components: {
            'pimpy-task': PimpyTask
        },
        // render: h => h(PimpyApp)

    })
}
