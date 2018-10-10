import Vue from "vue"
import PimpyTask from "./components/pimpy_task.vue"
import UserOverview from "./components/user_overview.vue"
import GroupUserOverview from "./components/group_user_overview.vue"
import CourseOverview from "./components/course_overview.vue"
import EducationOverview from "./components/education_overview.vue"
import * as Sentry from '@sentry/browser';

declare var SentryConfig: Sentry.BrowserOptions;

SentryConfig.integrations = [new Sentry.Integrations.Vue()];

Sentry.init(SentryConfig);


// Pimpy version, cannot use render function yet as we define custom element in
// Jinja e.g. <tr is="pimpy-task" :id="..." ...></tr>.
if (document.querySelector('#pimpy_app')) {
    new Vue({
        el: '#pimpy_app',
        components: {
            'pimpy-task': PimpyTask
        },
        // render: h => h(PimpyApp)
    })
}

// Group users over cannot user render function as we define the component in
// jinja.
if (document.querySelector('#vue-group-user-overview')) {
    new Vue({
        el: '#vue-group-user-overview',
        components: {
            'group-user-overview': GroupUserOverview
        }
    })
}

function loadRenderedVueIfAvailable(el, renderer) {
    if (document.querySelector(el)) {
        new Vue({
            el: el,
            render: h => h(renderer)
        })
    }
}

loadRenderedVueIfAvailable("#vue-user-overview", UserOverview);
loadRenderedVueIfAvailable("#vue-course-overview", CourseOverview);
loadRenderedVueIfAvailable("#vue-education-overview", EducationOverview);
