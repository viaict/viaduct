import Vue from "vue"
import App from "./components/app.vue"
// import * as Sentry from '@sentry/browser';
// // import Sentry from "@sentry/node";
//
// Sentry.onLoad(() => {
//     Sentry.init({
//         dsn: 'https://83ee35d289d440cebc546c7bac3fcc0b@sentry.io/122119',
//         release: '1.0.0',
//         environment: 'maico'
//     });
// });

new Vue( {
    el: '#app',
    render: h => h(App)
});