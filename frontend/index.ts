import Vue from "vue"
import App from "./components/app.vue"

import {init as SentryInit} from "@sentry/browser/dist";


SentryInit({
    dsn: 'https://d20fbd1634454649bd8877942ebb5657@sentry.io/1285048',
    release: '1.0.0',
    environment: 'maico',
    debug: true,

});

new Vue( {
    el: '#app',
    render: h => h(App)
});