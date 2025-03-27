// script.js
let allGpus = [];
let chart = null;

const searchInput = document.getElementById("search-bar");
const gpuContainer = document.getElementById("gpu-cards");
const detailsSection = document.getElementById("gpu-details");
const nameSpan = document.getElementById("gpu-name");
const buySpan = document.getElementById("gpu-buy-price");
const cashSpan = document.getElementById("gpu-sell-cash");
const storeSpan = document.getElementById("gpu-sell-store");
const profitSpan = document.getElementById("gpu-profit");
const totalGpuSpan = document.getElementById("total-gpus");

async function fetchGpuList() {
  try {
    const res = await fetch("/api/gpu-list");
    const gpus = await res.json();
    allGpus = gpus;
    totalGpuSpan.textContent = gpus.length;
    displayGpuCards(gpus);
  } catch (err) {
    console.error("Failed to load GPUs", err);
  }
}

function displayGpuCards(gpus) {
  gpuContainer.innerHTML = "";
  gpus.forEach((gpu) => {
    const card = document.createElement("div");
    card.className =
      "bg-white p-4 rounded shadow cursor-pointer hover:bg-gray-50 transition";
    card.textContent = gpu;
    card.onclick = () => loadGpuDetails(gpu);
    gpuContainer.appendChild(card);
  });
}

searchInput.addEventListener("input", (e) => {
  const searchTerm = e.target.value.toLowerCase();
  const filtered = allGpus.filter((g) => g.toLowerCase().includes(searchTerm));
  displayGpuCards(filtered);
});

async function loadGpuDetails(gpu) {
  try {
    const res = await fetch(`/api/gpu-prices?gpu=${encodeURIComponent(gpu)}`);
    const data = await res.json();
    if (!data.length) return;

    const latest = data[data.length - 1];
    nameSpan.textContent = gpu;
    buySpan.textContent = latest.buy_price;
    cashSpan.textContent = latest.sell_cash ?? "-";
    storeSpan.textContent = latest.sell_store ?? "-";

    const diff = (latest.buy_price - Math.max(latest.sell_cash || 0, latest.sell_store || 0)).toFixed(2);
    profitSpan.textContent = diff;

    renderChart(data);
    detailsSection.classList.remove("hidden");
  } catch (err) {
    console.error("Failed to load details", err);
  }
}

function renderChart(data) {
  const ctx = document.getElementById("priceChart").getContext("2d");
  const labels = data.map((d) => d.date);
  const buy = data.map((d) => d.buy_price);
  const cash = data.map((d) => d.sell_cash);
  const store = data.map((d) => d.sell_store);

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Buy Price",
          data: buy,
          borderColor: "#3b82f6",
          borderWidth: 2,
        },
        {
          label: "Cash Price",
          data: cash,
          borderColor: "#f59e0b",
          borderWidth: 2,
        },
        {
          label: "Store Credit",
          data: store,
          borderColor: "#10b981",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
      },
    },
  });
}

window.onload = fetchGpuList;