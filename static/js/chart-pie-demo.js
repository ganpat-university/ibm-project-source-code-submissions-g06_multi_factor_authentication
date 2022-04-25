// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ["CryptoCurrency", "Mutual Funds", "Stocks", "Fixed Deposit"],
    datasets: [{
      data: [45, 30, 15,10],
      backgroundColor: ['#4e73df', '#36b9cc', '#1cc88a', '#737CA1'],
      hoverBackgroundColor: ['#2e59d9', '#2c9faf', '#17a673', '#566D7E'],
      hoverBorderColor: "rgba(234, 236, 244, 258)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 60,
  },
});
