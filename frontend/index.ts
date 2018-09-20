import Vue from "vue"
import App from "./components/app.vue"

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
