<template lang="pug">
    tr
        td
            .btn-group
                a#pimpy_task.btn.dropdown-toggle(data-toggle="dropdown", :class="[statusClass, {loading: isStatusLoading}]")
                    span(v-if="isStatusLoading")
                        i.fa.fa-spinner.fa-spin.fa-lg
                    span(v-if="!isStatusLoading")
                        | {{ b32id }}
                ul.dropdown-menu
                    li(v-for="(statusDetail, statusId) in statusDetails")
                        a.pimpy_status(data-toggle="dropdown", :class="statusDetail.class", @click="setStatus(statusId)")
                            | {{ statusDetail.text }}

        td
            div(@click="collapsed = !collapsed") {{ title }}
            div(v-if="!collapsed")
                hr
                em.pull-right(v-if="!isStatusLoading") Click to edit
                em.pull-right(v-if="isStatusLoading") Updating...
                dl
                    dt(@click="focusField('title')") Task
                    dd(v-show="!isEditable('title')", @click="focusField('title')") {{ title }}
                    input(v-show="isEditable('title')", @blur="unfocusField()", @keyup.enter="unfocusField()", v-model="editValues.title", autofocus)

                    dt(@click="focusField('users')")  Users
                    dd(v-show="!isEditable('users')", @click="focusField('users')") {{ users }}
                    input(v-show="isEditable('users')", @blur="unfocusField()", @keyup.enter="unfocusField()", v-model="editValues.users", autofocus)

                    dt(@click="focusField('content')")  Content
                    dd(v-show="!isEditable('content')", @click="focusField('content')") {{ content }}
                    input(v-show="isEditable('content')", @blur="unfocusField()", @keyup.enter="unfocusField()", v-model="editValues.content", autofocus)

                    dt Created
                    dd {{ timestamp }}

                    a(:href="minuteUrl", v-if="minute_id") View Minute

        td {{ users }}

</template>

<style lang="sass" scoped>
    input
        width: 100%
</style>

<script lang="ts">
    import Vue from "vue"
    import {Component, Prop} from "vue-property-decorator"
    import instance from "../utils/axios";

    interface PimpyTaskEditableValues {
        users: string;
        title: string;
        content: string;
    }

    interface PimpyTaskStatusDetails {
        text: string;
        value: string;
        class: string;
    }

    @Component({name: 'pimpy-task'})
    export default class PimpyTask extends Vue {

        @Prop(Number) id: number;
        @Prop(String) b32id: string;
        @Prop(String) timestamp: string;
        @Prop(String) title: string;
        @Prop(String) content: string;
        @Prop(Number) minute_id: number;
        @Prop(String) users: string;
        @Prop(Number) line: number;
        @Prop(String) status: string;

        private collapsed: boolean = true;
        private isStatusLoading: boolean = false;
        private isFieldLoading: boolean = false;
        private editField: string = "";

        private editValues: PimpyTaskEditableValues;
        private baseMinuteUrl: string = "/pimpy/minutes/single/{minute_id}/{line}";

        private baseTaskUrl: string = "/api/tasks/" + this.b32id;
        private statusDetails: object = {
            "new": <PimpyTaskStatusDetails> {
                text: "Not started",
                class: "btn-info"
            },
            "started": <PimpyTaskStatusDetails> {
                text: "Started",
                class: "btn-warning"
            },
            "done": <PimpyTaskStatusDetails> {
                text: "Done",
                class: "btn-success"
            },
            "remove": <PimpyTaskStatusDetails> {
                text: "Not Done",
                class: "btn-danger"
            }
        };

        public created() {
            this.editValues = {
                'title': this.title,
                'users': this.users,
                'content': this.content
            }
        }

        get statusClass() {
            return this.statusDetails[this.status].class;
        }

        get statusText() {
            return this.statusDetails[this.status].text;
        }

        get minuteUrl() {
            return this.baseMinuteUrl
                .replace("{minute_id}", this.minute_id.toString())
                .replace("{line}", this.line.toString())
        }


        public isEditable(fieldName) {
            return this.editField === fieldName;
        }

        public focusField(fieldName) {
            this.editField = fieldName;
        }

        public async unfocusField() {
            let requestJson = {};
            if (this.editField === 'users') {
                requestJson[this.editField] = this.editValues[this.editField].split(",");
            } else {
                requestJson[this.editField] = this.editValues[this.editField];
            }

            try {
                this.isFieldLoading = true;
                const resp = await instance.patch(this.baseTaskUrl, requestJson);
                if (resp.status === 200) {
                    this.users = this.editValues['users'] = resp.data.users.join(", ");
                    this.content = this.editValues['content'] = resp.data.content;
                    this.title = this.editValues['title'] = this.title;
                }
            }
            catch (error) {
                console.log(error)
            }
            finally {
                this.isStatusLoading = false;
            }

            this.editField = "";
        }

        public async setStatus(status: string) {
            try {
                this.isStatusLoading = true;
                const resp = await instance.patch(this.baseTaskUrl, {status: status});
                if (resp.status === 200) {
                    this.status = status;
                }
            } catch (error) {
                console.log(error);
            } finally {
                this.isStatusLoading = false;
            }
        }
    }
</script>
