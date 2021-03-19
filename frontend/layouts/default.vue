<template>
  <div class="h-screen text-gray-800 dark:text-gray-300 dark:bg-gray-900">
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