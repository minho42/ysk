<template>
  <div class="text-gray-300">
    <Navbar />
    <Nuxt />
    <Footer />
    
  </div>
</template>

<script>
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
export default {
  components: {
    Navbar,
  }
}
</script>

<style>
body {
  /* github dark navbar */
  background-color: #161b21;
}
</style>