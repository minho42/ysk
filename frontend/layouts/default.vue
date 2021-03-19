<template>
  <div class="text-gray-800 dark:text-gray-300">
    <Navbar />
    <Nuxt />
  </div>
</template>

<script>
import Navbar from '../components/Navbar'
export default {
  components: {
    Navbar,
  }
}
</script>

<style>
body {
  /* from github */
  background-color: #0d1017;
}
</style>