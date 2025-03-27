const dropdown = document.getElementById("gpu-dropdown");

let chart;

async function loadGpuOptions() {
  const res = await fetch("/api/gpu-list");
  const gpus = await res.json();

  dropdown.innerHTML = '';
  gpus.forEach(gpu => {
    const option = document.createElement("option");
    option.value = gpu;
    option.textContent = gpu;
    dropdown.appendChild(option);
  });

  if (gpus.length > 0) {
    dropdown.value = gpus[0];
    loadChart(); // Load first GPU by default
  }
}

async function loadChart() {
  const gpu = dropdown.value;
  if (!gpu) return;

  const res = await fetch(`/api/gpu-prices?gpu=${encodeURIComponent(gpu)}`);
  const data = await res.json();

  const labels = data.map(d => d.date);
  const buy = data.map(d => d.buy_price);
  const cash = data.map(d => d.sell_cash);
  const store = data.map(d => d.sell_store);

  const ctx = document.getElementById("priceChart").getContext("2d");

  if (chart) chart.destroy(); // Clear old chart

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: "Buy Price", data: buy, borderWidth: 2, borderColor: '#3e95cd', fill: false },
        { label: "Sell for Cash", data: cash, borderWidth: 2, borderColor: '#8e5ea2', fill: false },
        { label: "Sell for Store Credit", data: store, borderWidth: 2, borderColor: '#3cba9f', fill: false }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

dropdown.addEventListener("change", loadChart);
loadGpuOptions();
