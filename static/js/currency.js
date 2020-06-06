Vue.component("currency-barchart", {
  props: ["labels", "series", "fetchTime"],
  template: '<canvas id="bar-chart"></canvas>',

  data() {
    return {
      myChart: undefined,
      stepSize: 10,
    };
  },
  methods: {
    getMin() {
      var min = Math.min.apply(null, this.series[0]) - 1;
      var roundedMin = Math.floor(min / this.stepSize) * this.stepSize;
      return roundedMin;
    },
    getMax() {
      var max = Math.max.apply(null, this.series[0]) + 1;
      var roundedMax = Math.ceil(max / this.stepSize) * this.stepSize;
      return roundedMax;
    },
    fetchData() {
      // console.log(this.series[0])
      // console.log(this.labels)
      this.myChart.config.options.scales.yAxes[0].ticks.min = this.getMin();
      this.myChart.config.options.scales.yAxes[0].ticks.max = this.getMax();

      this.myChart.config.options.scales.yAxes[0].ticks.stepSize = this.stepSize;
      // this.myChart.config.options.scales.yAxes[0].ticks.stepSize = (this.getMax() - this.getMin()) / 10
      // this.myChart.config.options.title.text = 'AUD/KRW (' + this.fetchTime + ' ago)'

      this.myChart.config.data.labels = this.labels;
      this.myChart.config.data.datasets[0].data = this.series[0];

      this.myChart.update();
    },
    drawData() {},
  },
  watch: {
    labels: "fetchData",
    series: "fetchData",
  },
  mounted: function () {
    var data = {
      datasets: [
        {
          backgroundColor: "#48b884",
          // data: this.series[0],
        },
      ],
    };
    var options = {
      //responsive, maintainAspectRatio for setting width/height in css
      responsive: true,
      maintainAspectRatio: true,
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "AUD/KRW",
        fontSize: 22,
        fontColor: "#000",
        fontStyle: "",
      },
      layout: {
        padding: {
          left: 0,
          right: 50,
          top: 0,
          bottom: 0,
        },
      },
      scales: {
        yAxes: [
          {
            ticks: {
              min: 0,
              max: 0,
              stepSize: 1,
              fontSize: 16,
            },
            gridLines: {
              display: false,
            },
            // categoryPercentage: 0.8,
            // barPercentage: 0.9
          },
        ],
        xAxes: [
          {
            ticks: {
              fontSize: 16,
            },
            gridLines: {
              // display: false
            },
            // categoryPercentage: 0.7,
            // barPercentage: 0.6
          },
        ],
      },
      tooltips: {
        enabled: false,
      },
      // https://chartjs-plugin-datalabels.netlify.com/options
      plugins: {
        datalabels: {
          display: true,
          anchor: "end",
          align: "end",
          // color: 'rgba(0,0,0,.9)',
          color: "$000",
          font: {
            // style: ' bold',
            size: 16,
          },
          offset: 0,
        },
      },
      // http://www.chartjs.org/docs/2.6.0/configuration/animations.html#animation-configuration
      animation: {
        // duration: 500,
        onProgress: function () {},
        onComplete: function () {},
      },
    };
    var ctx = document.getElementById("bar-chart").getContext("2d");
    this.myChart = new Chart(ctx, {
      // type: "bar",
      type: "horizontalBar",
      data: data,
      options: options,
    });
  },
});

var vm = new Vue({
  delimiters: ["[[", "]]"],
  el: "#currency",
  data: {
    labels: [],
    series: [],
    fetchTime: "",
    hostname: window.location.hostname,
    isFetching: false,
  },
  computed: {
    fetchBtnText() {
      if (this.isFetching) {
        return "Fetching...";
      } else {
        return "Fetch";
      }
    },
  },
  mounted: function () {
    this.getOldCurrencies();
    // this.getNewCurrencies()
    // setInterval(this.getOldCurrencies, 1000 * 60 * 60);
    // setInterval(this.getNewCurrencies, 1000 * 60 * 60);
  },
  methods: {
    getOldCurrencies() {
      console.log("getOldCurrencies");
      this.getThis("api/old/", (setFetching = false));
    },
    getNewCurrencies() {
      console.log("getNewCurrencies");
      this.getThis("api/new/", (setFetching = true));
    },
    getThis(url, setFetching) {
      var self = this;
      if (setFetching) {
        self.isFetching = setFetching;
      }

      axios
        .get(url)
        .then(function (response) {
          // check empty response

          self.labels = response.data.labels;
          self.series = [response.data.rates];
          self.fetchTime = response.data.modified;
          if (setFetching) {
            self.isFetching = false;
          }
          // console.log(self.fetchTime)
        })
        .catch(function (error) {
          self.isFetching = false;
          console.log("axios.get error: " + error.message);
        });
    },
  },
});
