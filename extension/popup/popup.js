// TabbyPatrol - Popup UI Script

document.addEventListener("DOMContentLoaded", () => {
  const statusBadge = document.getElementById("status-badge");
  const statusText = document.getElementById("status-text");
  const statSwatted = document.getElementById("stat-swatted");
  const statBlockedCount = document.getElementById("stat-blocked-count");
  const siteCountBadge = document.getElementById("site-count-badge");
  const domainsList = document.getElementById("domains-list");
  const newDomainInput = document.getElementById("new-domain-input");
  const addDomainBtn = document.getElementById("add-domain-btn");
  const testSwatBtn = document.getElementById("test-swat-btn");

  let currentDomains = [];

  function cleanDomain(input) {
    let clean = input.trim().toLowerCase();
    if (clean.startsWith("http://") || clean.startsWith("https://")) {
      try {
        clean = new URL(clean).hostname;
      } catch (e) {}
    }
    if (clean.startsWith("www.")) {
      clean = clean.slice(4);
    }
    return clean;
  }

  function renderDomains() {
    domainsList.innerHTML = "";
    statBlockedCount.textContent = currentDomains.length;
    siteCountBadge.textContent = `${currentDomains.length} sites`;

    if (currentDomains.length === 0) {
      domainsList.innerHTML = '<span style="font-size: 11px; color: #a19188; padding: 4px;">No blocked sites added yet.</span>';
      return;
    }

    currentDomains.forEach((domain, idx) => {
      const chip = document.createElement("div");
      chip.className = "domain-chip";
      chip.innerHTML = `
        <span>${domain}</span>
        <button class="remove-btn" title="Remove" data-idx="${idx}">×</button>
      `;
      domainsList.appendChild(chip);
    });

    // Attach remove handlers
    document.querySelectorAll(".remove-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const index = parseInt(e.target.getAttribute("data-idx"), 10);
        if (!isNaN(index)) {
          currentDomains.splice(index, 1);
          chrome.storage.local.set({ blockedDomains: currentDomains }, () => {
            renderDomains();
          });
        }
      });
    });
  }

  function addDomain() {
    const raw = newDomainInput.value;
    const clean = cleanDomain(raw);
    if (!clean) return;

    if (!currentDomains.includes(clean)) {
      currentDomains.push(clean);
      chrome.storage.local.set({ blockedDomains: currentDomains }, () => {
        renderDomains();
        newDomainInput.value = "";
      });
    } else {
      newDomainInput.value = "";
    }
  }

  addDomainBtn.addEventListener("click", addDomain);
  newDomainInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") addDomain();
  });

  // Test Swat
  testSwatBtn.addEventListener("click", () => {
    testSwatBtn.textContent = "🐾 Swatting current tab!";
    testSwatBtn.disabled = true;

    chrome.runtime.sendMessage({ type: "TRIGGER_TEST_SWAT" }, (res) => {
      setTimeout(() => {
        testSwatBtn.textContent = "🐾 Test Swat on Current Tab";
        testSwatBtn.disabled = false;
      }, 2000);
    });
  });

  // Query background service worker for status
  function updateStatus() {
    chrome.runtime.sendMessage({ type: "GET_STATUS" }, (response) => {
      if (chrome.runtime.lastError || !response) {
        statusBadge.className = "status-badge disconnected";
        statusText.textContent = "Connecting to Desktop Cat...";
        return;
      }

      if (response.isConnected) {
        statusBadge.className = "status-badge connected";
        statusText.textContent = "Desktop Cat Connected & Ready!";
      } else {
        statusBadge.className = "status-badge disconnected";
        statusText.textContent = "Desktop Overlay Not Running";
      }

      if (response.blockedDomains) {
        currentDomains = response.blockedDomains;
        renderDomains();
      }

      if (response.stats) {
        statSwatted.textContent = response.stats.closedCount || 0;
      }
    });
  }

  updateStatus();
  setInterval(updateStatus, 1500);
});
