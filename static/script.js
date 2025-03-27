const searchBar = document.getElementById("search-bar");

searchBar.addEventListener("input", () => {
  const query = searchBar.value.toLowerCase();
  const options = dropdown.querySelectorAll("option");
  options.forEach(opt => {
    const match = opt.textContent.toLowerCase().includes(query);
    opt.hidden = !match;
  });
});


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


async function loadOverviewStats() {
    const res = await fetch("/api/gpu-list");
    const gpus = await res.json();
  
    // Update total
    document.getElementById("total-gpus").textContent = gpus.length;
  
    // For simplicity, we'll just use the first GPU's trend to mock avg/drop/gain.
    if (gpus.length > 0) {
      const priceRes = await fetch(`/api/gpu-prices?gpu=${encodeURIComponent(gpus[0])}`);
      const data = await priceRes.json();
  
      if (data.length > 0) {
        const prices = data.map(p => p.buy_price);
        const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
        const diff = prices[prices.length - 1] - prices[0];
  
        document.getElementById("avg-price").textContent = `£${avg.toFixed(2)}`;
        document.getElementById("biggest-drop").textContent = diff < 0 ? `£${diff}` : 'None';
        document.getElementById("top-gainer").textContent = diff > 0 ? `£${diff}` : 'None';
      }
    }
  }
  loadOverviewStats();
