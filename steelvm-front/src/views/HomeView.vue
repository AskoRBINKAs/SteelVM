<script setup>
import axios from 'axios';
import CheckAuth from '@/AuthValidator';
import { useRouter, useRoute } from 'vue-router'
import Header from '../components/SidebarComponent.vue'

const router = useRouter()
let a = CheckAuth()
console.log(a)
if (a===false){
  router.push('/login')
}
</script>

<template>
  <Header></Header>
  <h1>Home</h1>  
</template>
