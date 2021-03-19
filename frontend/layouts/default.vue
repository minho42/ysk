<template>
  <div class="h-screen text-gray-800 dark:text-gray-300 dark:bg-gray-900">
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