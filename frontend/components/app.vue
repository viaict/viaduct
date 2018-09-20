<template>
    <div class="row">Hello world!</div>
</template>

<script lang="ts">
    import Vue from "vue"
    import {Component} from "vue-property-decorator"

    @Component
    export default class App extends Vue {

        public created() {
            console.log("Message");
        }
    }
</script>

<style scoped>
</style>