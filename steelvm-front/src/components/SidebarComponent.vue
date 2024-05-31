<template>
    <div class="header">
        <img src="../../public/Logo2.png" height="4%" width="4%" style="margin-left: 1vw;">
        <div class="btn">
            <img src="../../public/cloud.svg" width="50%" height="70%" style="margin-top: 3%;">
            <router-link to="/" class="btn-link">Hosts</router-link>
        </div>
        <div class="btn">
            <router-link to="/about" class="btn-link">Hosts</router-link>
        </div>
    </div>
</template>

<script>

export default{
    name:'Header'
}
</script>

<style>
.header{
    background-color: #1565c0;
    height: 100%; /* Full-height: remove this if you want "auto" height */
    width: 10vw; /* Set the width of the sidebar */
    position: fixed; /* Fixed Sidebar (stay in place on scroll) */
    z-index: 1; /* Stay on top */
    top: 0; /* Stay at the top */
    left: 0;
    overflow-x: hidden; /* Disable horizontal scroll */
    padding-top: 20px;
}
.btn{
    display: block;
    margin-left: 1vw;
    margin-top: 1.5vh;
    margin-right: 1vw;
    background: white;
    border-radius: 1px;
    height: 3vh;
    
}
.btn-link{
    text-decoration: none;
    color: black;
    cursor: pointer;
    font-size: 16px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>