// TabbyPatrol - Background Service Worker
// Connects to the Desktop Overlay App via WebSocket, watches for blocked tabs,
// and removes tabs when the cute cat swats them!

const DEFAULT_BLOCKED_DOMAINS = [
  "reddit.com",
  "twitter.com",
  "x.com",
  "youtube.com",
  "instagram.com",
  "tiktok.com",
  "twitch.tv",
  "facebook.com",
  "netflix.com",
  "pinterest.com",
  "buzzfeed.com"
];

let blockedDomains = [...DEFAULT_BLOCKED_DOMAINS];
let socket = null;
let isConnected = false;
let pendingCloseTabs = new Set();
let recentlyTriggeredTabs = new Map(); // tabId -> timestamp

// Load saved settings
chrome.storage.local.get(["blockedDomains", "stats"], (result) => {
  if (result.blockedDomains && Array.isArray(result.blockedDomains)) {
    blockedDomains = result.blockedDomains;
  } else {
    chrome.storage.local.set({ blockedDomains: DEFAULT_BLOCKED_DOMAINS });
  }

  if (!result.stats) {
    chrome.storage.local.set({ stats: { closedCount: 0, lastEvent: null } });
  }
});

// Listen for storage changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.blockedDomains) {
    blockedDomains = changes.blockedDomains.newValue || [];
  }
});

// WebSocket Connection Management
function connectWebSocket() {
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return;
  }

  try {
    socket = new WebSocket("ws://127.0.0.1:48888");

    socket.onopen = () => {
      isConnected = true;
      console.log("[TabbyPatrol] Connected to Desktop Overlay Cat!");
      sendSyncStatus();
      reportTabState();
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleOverlayMessage(data);
      } catch (err) {
        console.error("[TabbyPatrol] Failed to parse message:", err);
      }
    };

    socket.onclose = () => {
      isConnected = false;
      console.log("[TabbyPatrol] Disconnected from Desktop Overlay. Retrying in 2s...");
      setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = (err) => {
      isConnected = false;
      // Socket error - will trigger onclose and retry
    };
  } catch (e) {
    setTimeout(connectWebSocket, 2000);
  }
}

// Send payload to overlay if connected
function sendToOverlay(msg) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(msg));
  }
}

// Handle messages from the Desktop Overlay
function handleOverlayMessage(msg) {
  switch (msg.type) {
    case "CLOSE_TAB":
      if (msg.tabId) {
        closeTabSafely(msg.tabId, msg.reason);
      }
      break;

    case "PING":
      sendToOverlay({ type: "PONG", timestamp: Date.now() });
      break;

    case "REQUEST_TAB_STATE":
      reportTabState();
      break;

    default:
      console.log("[TabbyPatrol] Unknown message from overlay:", msg);
  }
}

// Safely close the blocked tab
function closeTabSafely(tabId, reason = "swatted") {
  chrome.tabs.get(tabId, (tab) => {
    if (chrome.runtime.lastError || !tab) {
      pendingCloseTabs.delete(tabId);
      return;
    }

    chrome.tabs.remove(tabId, () => {
      if (chrome.runtime.lastError) {
        console.warn("[TabbyPatrol] Could not close tab:", chrome.runtime.lastError.message);
      } else {
        console.log(`[TabbyPatrol] Tab ${tabId} closed! (${reason})`);
        pendingCloseTabs.delete(tabId);

        // Update stats
        chrome.storage.local.get(["stats"], (res) => {
          const stats = res.stats || { closedCount: 0 };
          stats.closedCount = (stats.closedCount || 0) + 1;
          stats.lastEvent = {
            title: tab.title,
            url: tab.url,
            time: new Date().toLocaleTimeString()
          };
          chrome.storage.local.set({ stats });
        });
      }
    });
  });
}

// Check if a URL matches any blocked domain
function isUrlBlocked(rawUrl) {
  if (!rawUrl || typeof rawUrl !== "string") return false;
  try {
    const urlObj = new URL(rawUrl);
    const hostname = urlObj.hostname.toLowerCase();

    return blockedDomains.some((domain) => {
      const clean = domain.trim().toLowerCase();
      if (!clean) return false;
      return hostname === clean || hostname.endsWith("." + clean);
    });
  } catch (e) {
    return false;
  }
}

// Check a specific tab and notify overlay if blocked
function inspectTab(tabId) {
  chrome.tabs.get(tabId, (tab) => {
    if (chrome.runtime.lastError || !tab || !tab.url) return;

    if (isUrlBlocked(tab.url)) {
      // Throttle trigger per tab within 4 seconds
      const now = Date.now();
      const last = recentlyTriggeredTabs.get(tabId) || 0;
      if (now - last < 4000) return;
      recentlyTriggeredTabs.set(tabId, now);

      // Query all tabs in this window to determine the exact index and total count
      chrome.tabs.query({ windowId: tab.windowId }, (allTabs) => {
        if (!allTabs || allTabs.length === 0) return;

        chrome.windows.get(tab.windowId, (win) => {
          const winBounds = win ? {
            left: win.left || 0,
            top: win.top || 0,
            width: win.width || 1920,
            height: win.height || 1080,
            state: win.state || "normal"
          } : null;

          const tabIndex = allTabs.findIndex((t) => t.id === tab.id);

          console.log(`[TabbyPatrol] Blocked site detected! Tab ${tab.id} at index ${tabIndex}/${allTabs.length}`);

          sendToOverlay({
            type: "BLOCKED_TAB_OPENED",
            tabId: tab.id,
            tabIndex: tabIndex >= 0 ? tabIndex : tab.index,
            totalTabs: allTabs.length,
            title: tab.title || "Blocked Tab",
            url: tab.url,
            window: winBounds
          });
        });
      });
    }
  });
}

// Report overall tab state (count, window geometry)
function reportTabState() {
  chrome.windows.getCurrent({ populate: true }, (win) => {
    if (chrome.runtime.lastError || !win || !win.tabs) return;

    const activeTab = win.tabs.find((t) => t.active);
    sendToOverlay({
      type: "TABS_UPDATED",
      totalTabs: win.tabs.length,
      activeTabIndex: activeTab ? activeTab.index : 0,
      window: {
        left: win.left || 0,
        top: win.top || 0,
        width: win.width || 1920,
        height: win.height || 1080,
        state: win.state
      }
    });
  });
}

function sendSyncStatus() {
  sendToOverlay({
    type: "SYNC_STATUS",
    blockedCount: blockedDomains.length,
    timestamp: Date.now()
  });
}

// Listen for tab navigation / URL changes
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.status === "loading" || changeInfo.status === "complete") {
    inspectTab(tabId);
  }
});

// Listen for tab switches
chrome.tabs.onActivated.addListener((activeInfo) => {
  inspectTab(activeInfo.tabId);
  reportTabState();
});

// Listen for tab creation / deletion / movement to update positions
chrome.tabs.onCreated.addListener(() => reportTabState());
chrome.tabs.onRemoved.addListener((tabId) => {
  recentlyTriggeredTabs.delete(tabId);
  reportTabState();
});
chrome.tabs.onMoved.addListener(() => reportTabState());

// Popup communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "GET_STATUS") {
    chrome.storage.local.get(["blockedDomains", "stats"], (res) => {
      sendResponse({
        isConnected,
        blockedDomains: res.blockedDomains || blockedDomains,
        stats: res.stats || { closedCount: 0 }
      });
    });
    return true;
  }

  if (request.type === "TRIGGER_TEST_SWAT") {
    // Send a test swat trigger so user can test the cat right away!
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs && tabs[0];
      chrome.tabs.query({ currentWindow: true }, (allTabs) => {
        chrome.windows.getCurrent((win) => {
          sendToOverlay({
            type: "BLOCKED_TAB_OPENED",
            tabId: activeTab ? activeTab.id : 999,
            tabIndex: activeTab ? activeTab.index : 0,
            totalTabs: (allTabs && allTabs.length) || 1,
            title: (activeTab && activeTab.title) || "Test Swat Action",
            url: (activeTab && activeTab.url) || "https://distraction-example.com",
            isTest: true,
            window: win ? {
              left: win.left || 0,
              top: win.top || 0,
              width: win.width || 1920,
              height: win.height || 1080
            } : null
          });
          sendResponse({ success: true });
        });
      });
    });
    return true;
  }
});

// Connect immediately on startup
connectWebSocket();

// Periodic heartbeat & keepalive check
chrome.alarms.create("tabbyKeepalive", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "tabbyKeepalive") {
    if (!isConnected) {
      connectWebSocket();
    } else {
      sendToOverlay({ type: "HEARTBEAT", timestamp: Date.now() });
    }
  }
});
