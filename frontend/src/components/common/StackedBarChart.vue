<template>
  <div class="chart-wrapper" :class="sizeClass" :style="dynamicStyle">
    <Bar :data="chartData" :options="options" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default {
  name: 'StackedGroupsBarChart',
  components: { Bar },
  props: {
    chartData: {
      type: Object,
      required: true
    },
    selectedFrequency: {
      type: String,
      default: 'monthly'
    },
    width: {
      type: Number,
      default: 800
    },
    height: {
      type: Number,
      default: 400
    },
    size: {
      type: String,
      default: 'medium',
      validator: value => ['small', 'medium', 'large', 'custom'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    showLegend: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    sizeClass() {
      return `chart-${this.size}`
    },
    dynamicStyle() {
      if (this.size === 'custom') {
        return { width: this.width + 'px', height: this.height + 'px' }
      }
      return {}
    },
    options() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          title: {
            display: !!this.title,
            text: this.title || `Sales Analysis (${this.selectedFrequency})`,
            font: {
              size: 16,
              weight: 'bold'
            },
            color: '#374151',
            padding: {
              top: 10,
              bottom: 20
            }
          },
          legend: {
            display: this.showLegend,
            position: 'top',
            align: 'center',
            labels: {
              boxWidth: 12,
              padding: 15,
              font: {
                size: 12
              },
              usePointStyle: true,
              pointStyle: 'rect'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {
              title: function(context) {
                return context[0].label
              },
              label: function(context) {
                const label = context.dataset.label || ''
                const stack = context.dataset.stack || ''
                const value = new Intl.NumberFormat('en-PH', {
                  style: 'currency',
                  currency: 'PHP'
                }).format(context.parsed.y)
                
                return `${label} (${stack}): ${value}`
              },
              afterLabel: function(context) {
                // Show stack group total
                const stack = context.dataset.stack
                if (stack) {
                  const stackTotal = context.chart.data.datasets
                    .filter(dataset => dataset.stack === stack)
                    .reduce((total, dataset) => {
                      return total + (dataset.data[context.dataIndex] || 0)
                    }, 0)
                  
                  const formattedTotal = new Intl.NumberFormat('en-PH', {
                    style: 'currency',
                    currency: 'PHP'
                  }).format(stackTotal)
                  
                  return `${stack} Total: ${formattedTotal}`
                }
                return ''
              }
            }
          }
        },
        scales: {
          x: {
            stacked: true,
            grid: {
              display: false
            },
            border: {
              display: false
            },
            ticks: {
              color: '#6b7280',
              font: {
                size: 11
              }
            }
          },
          y: {
            stacked: true,
            beginAtZero: true,
            grid: {
              color: 'rgba(107, 114, 128, 0.1)',
              drawBorder: false
            },
            border: {
              display: false
            },
            ticks: {
              color: '#6b7280',
              font: {
                size: 11
              },
              callback: function(value) {
                return new Intl.NumberFormat('en-PH', {
                  style: 'currency',
                  currency: 'PHP',
                  notation: 'compact',
                  maximumFractionDigits: 1
                }).format(value)
              }
            }
          }
        },
        elements: {
          bar: {
            borderRadius: {
              topLeft: 2,
              topRight: 2,
              bottomLeft: 0,
              bottomRight: 0
            },
            borderSkipped: false
          }
        },
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Predefined sizes */
.chart-small {
  width: 500px;
  height: 250px;
}

.chart-medium {
  width: 700px;
  height: 350px;
}

.chart-large {
  width: 900px;
  height: 450px;
}

/* .chart-custom { } */

/* Responsive behavior */
@media (max-width: 768px) {
  .chart-wrapper {
    width: 100% !important;
    min-width: 300px;
    max-width: 100%;
    padding: 10px;
  }
  
  .chart-small,
  .chart-medium,
  .chart-large {
    width: 100%;
    height: 280px;
  }
}

.chart-wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.3s ease;
}
</style>