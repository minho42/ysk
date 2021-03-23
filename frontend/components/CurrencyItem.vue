<template>
  <tr class="border-b border-gray-700">
    <td>
      <div v-if="name === 'Naver'">
        -
      </div>
      <div v-else>
        {{ index }}
      </div>
    </td>
    <td class="py-1">
      <a class="px-1 text-blue-400 hover:underline"
        :href="url" target="_blank" rel="noopener noreferrer">
        {{ name }}
      </a>
    </td>
    <td class="">
      <div class="inline-flex text-green-400 rounded-md px-2">
        {{ real_rate }}
      </div>
    </td>
    <td>
      <div v-if="rate !== real_rate" class="px-1 text-gray-400">
        {{ rate }}
      </div>
      <div v-else class="text-center">
        -
      </div>
    </td>
    <td>
      <div v-if="rate !== real_rate" class="inline-flex text-pink-400 rounded-md px-1">
        {{ fee }}
      </div>
      <div v-else class="text-center">
        -
      </div>
    </td>
    <td class="hidden sm:block">
      <div v-if="note" class="inline-flex text-yellow-400 px-1 break-all">
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
