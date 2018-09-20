<template lang="pug">
.login
    form.form
        h3(style="color: rgb(9, 77, 151)") Inloggen
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