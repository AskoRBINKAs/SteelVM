<template>
    <div class="base">
        <div class="form">
            <img src="../../public/Logo2.png" width="55%" height="40%" style="margin-left:6.5vw;">
            <div class="form-data">
                <h2 style="font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">Welcome back</h2>
                <div>
                    <input class="inputs" v-model="login" placeholder="Email" type="email">
                </div>
                <div>
                    <input class="inputs" v-model="password" placeholder="Password" type="password">
                </div>
                <button class="send-button" @click="fetch">Sign in</button>
            </div>
        </div>
        <div class="fade">
        </div>
    </div>
</template>

<script setup>
import axios from 'axios'
import {ref} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CheckAuth from '@/AuthValidator';

const router = useRouter()

function pushWithQuery(query) {
  router.push(query)
}

if (CheckAuth()===true){
    pushWithQuery('/')
}
let login = ref("")
let password = ref("")

function fetch(params) {
    axios.post("http://localhost:8000/api/auth/login/",{
        email:login.value,
        password:password.value,
    }).then(function (resp){
        console.log(resp.data.token)
        localStorage.setItem("access_token",resp.data.token)
        pushWithQuery('/')
    }).catch(err => console.log(err))
}
</script>

<style>

.base{
    display: flex;
    flex-direction: row;
    min-width: 100%;
    overflow: hidden;
}
.fade{
    background: #74ebd5;  /* fallback for old browsers */
    background: -webkit-linear-gradient(to right, #ACB6E5, #74ebd5);  /* Chrome 10-25, Safari 5.1-6 */
    background: linear-gradient(to right, #ACB6E5, #74ebd5); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */

    width: 100vw;
    height: 100vh;
    overflow: hidden;
    display: inline-block;
    position: relative;
}
.form{
    margin-top: 8vh;
    margin-left: 5vw;
    margin-right: 5vw;
    max-width: 30vw;
    border-radius: 5px 5px 5px 5px;
}
.form-data{
    flex-direction: column;
    display: flex;
}
.inputs{
    height: 5vh;
    width: 30vw;
    font-size: 2vh;
    margin-bottom: 1vh;
}
.send-button{
    font-size: 16pt;
    font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    width: 10vw;
    margin-left: 9.7vw;
    height: 6vh;
    background-color:aqua;
    border-color: aqua;
    border-radius: 5px;
    box-shadow: none;
}
</style>