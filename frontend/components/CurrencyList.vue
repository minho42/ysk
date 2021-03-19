<template>
  <div id="list" class="flex flex-col items-center justify-between pt-2 pb-2 mx-2">
    <div v-if="currencies.length === 0" class="text-center">
      Loading...
    </div>
    <table v-else class="table-auto">
      <thead>
        <tr class="border-b-2 border-gray-300 dark:border-gray-700">
          <th class="font-medium">No</th>
          <th class="font-medium">Name</th>
          <th class="font-medium">Rate</th>
          <th class="font-medium">Fee</th>
          <th class="font-medium">Real rate</th>
          <th class="font-medium">Note</th>
        </tr>
      </thead>
      <tbody>
        <CurrencyItem
          v-for="(currency, index) in currencies"
          v-bind="currency"
          v-bind:index="index"
          :key="currency.name"
        />
      </tbody>
    </table>

    <div class="my-3">{{ lastUpdate }}</div>

  </div>  
</template>


<script>
import CurrencyItem from './CurrencyItem'
import { formatDistance } from 'date-fns'

export default {
  name: 'CurrencyList',
  data() {
    return {
      currencies: [],
      lastUpdate: ''
    }
  },
  components: {
    CurrencyItem,    
  },
  methods: {
    
  },
  async created() {
    // Ping heroku
    const res = await fetch('https://ysk.herokuapp.com')
    const { data } = await res.json()
    console.log(data)   
  },
  async mounted() {
      const res = await fetch('https://ysk.herokuapp.com/data')
      // const res = await fetch('http://localhost:8000/data')
      const data = await res.json()
      console.log(data)    
      this.currencies = data
      
      if (data && data.length > 0) {
        const lastUpdate = data[0].modified
        if (lastUpdate) {
          this.lastUpdate = formatDistance(new Date(lastUpdate), new Date()) + ' ago'
        }
      }
  },
  computed: {
    
  },
}
</script>

<style>

</style>