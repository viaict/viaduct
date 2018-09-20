<template lang="pug">
.div Hello world
</template>

<script lang="ts">
    import Vue from "vue"
    import {Component} from "vue-property-decorator"
    import {captureException} from "@sentry/browser/dist"

    @Component
    export default class App extends Vue {

        public created() {
            console.log("Message");
        }
    }
</script>

<style scoped>
</style>