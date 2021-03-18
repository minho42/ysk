<template>
  <tr class="border-b border-gray-300 dark:border-gray-700">
    <td>
      <div v-if="name === 'Naver'">
        -
      </div>
      <div v-else>
        {{ index }}
      </div>
    </td>
    <td class="py-1">
      <a class="px-1 text-blue-600 dark:text-blue-400 dark:hover:text-blue-400 hover:underline"
        :href="url" target="_blank" rel="noopener noreferrer">
        {{ name }}
      </a>
    </td>
    <td>
      <div v-if="rate === real_rate" class="px-1 text-gray-500">
        {{ rate }}
      </div>
      <div v-else>
        -
      </div>
    </td>
    <td>
      <div v-if="rate !== real_rate" class="inline-flex bg-red-100 dark:bg-transparent dark:text-pink-400 rounded-md px-1">
        {{ fee }}
      </div>
      <div v-else>
        -
      </div>
    </td>
    <td class="">
      <div class="inline-flex bg-blue-100 dark:bg-transparent dark:text-green-400 rounded-md px-2">
        {{ real_rate }}
      </div>
    </td>
    <td class="">
      <div v-if="note" class="inline-flex dark:text-yellow-400 px-1">
        {{ note }}
      </div>
    </td>
  </tr>
</template>

<script>
export default {
  name: 'CurrencyItem',
  data() {
    return {
      
    }
  },
  props: {
    name: String,
    rate: String,
    fee: String,
    real_rate: String,
    url: String,
    note: String,
    modified: String,
    index: Number,
  },
  components: {
    
  },
  computed: {
    
  }
}
</script>
