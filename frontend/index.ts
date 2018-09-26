import Vue from "vue"
import PimpyTask from "./components/pimpy_task.vue"
import * as Sentry from '@sentry/browser';

declare var SentryConfig: Sentry.BrowserOptions;

SentryConfig.integrations = [new Sentry.Integrations.Vue()];

Sentry.init(SentryConfig);

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
