// service-worker.js - Enhanced with ping/pong management

const SW_VERSION = (() => {
    const url = new URL(self.location);
    return url.searchParams.get("v") || "unknown";
})();

// Ping/pong statistics
let pingPongStats = {
    lastPingReceived: 0,
    lastPongSent: 0,
    pingCount: 0,
    pongCount: 0,
    averageResponseTime: 0
};

self.addEventListener('install', event => {
    console.log(`Service Worker (v${SW_VERSION}): Installed`);
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log(`Service Worker (v${SW_VERSION}): Activated`);
    event.waitUntil(self.clients.claim());
});

self.addEventListener('message', event => {
    // Handle WebSocket initialization
    if (event.data.type === 'INIT_WEBSOCKET') {
        connectWebSocket(event.data.wsUrl, event.data.clientId);
    }

    // Handle requests for ping/pong stats
    if (event.data.type === 'GET_PING_STATS') {
        event.ports[0].postMessage({
            type: 'PING_STATS_RESPONSE',
            stats: pingPongStats
        });
    }
});

// WebSocket connection with ping/pong handling
let websocket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket(wsUrl, clientId) {
    const urlWithId = `${wsUrl}?clientId=${encodeURIComponent(clientId)}`;

    console.log(`Service Worker (v${SW_VERSION}): Connecting WebSocket to`, urlWithId);
    websocket = new WebSocket(urlWithId);

    websocket.onopen = () => {
        console.log(`Service Worker (v${SW_VERSION}): WebSocket connected`);
        reconnectAttempts = 0;

        // Reset ping/pong stats on new connection
        resetPingPongStats();

        // Notify clients
        notifyClients({
            type: 'WEBSOCKET_STATUS',
            status: 'connected',
            version: SW_VERSION
        });
    };

    websocket.onmessage = event => {
        const data = parseWebsocketMessage(event.data);

        if (data && data.type) {
            // Handle ping/pong at service worker level
            if (data.type === 'ping') {
                handlePingInServiceWorker(data);
                return; // Don't forward to main thread
            }

            if (data.type === 'pong') {
                handlePongInServiceWorker(data);
                return; // Don't forward to main thread
            }

            // Forward all other messages to main thread
            notifyClients({
                type: 'WEBSOCKET_MESSAGE',
                data,
                swVersion: SW_VERSION
            });
        } else {
            console.error(`Service Worker (v${SW_VERSION}): Invalid WebSocket message:`, data);
        }
    };

    websocket.onerror = error => {
        console.error(`Service Worker (v${SW_VERSION}): WebSocket error:`, error);

        notifyClients({
            type: 'WEBSOCKET_STATUS',
            status: 'error',
            error: error.toString(),
            version: SW_VERSION
        });
    };

    websocket.onclose = event => {
        console.warn(`Service Worker (v${SW_VERSION}): WebSocket closed.`, {
            code: event.code,
            reason: event.reason
        });

        notifyClients({
            type: 'WEBSOCKET_STATUS',
            status: 'disconnected',
            code: event.code,
            reason: event.reason,
            version: SW_VERSION,
            pingStats: pingPongStats
        });

        // Reconnect with exponential backoff
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000);
            console.log(`Service Worker (v${SW_VERSION}): Reconnecting in ${delay}ms`);
            setTimeout(() => connectWebSocket(wsUrl, clientId), delay);
        }
    };
}

function handlePingInServiceWorker(pingData) {
    const startTime = performance.now();

    console.log(`Service Worker (v${SW_VERSION}): 🏓 Received ping from server`);

    // Update stats
    pingPongStats.lastPingReceived = Date.now();
    pingPongStats.pingCount++;

    // Create pong response
    const pongMessage = {
        type: "pong",
        content: "pong",
        meta: {
            timestamp: Date.now(),
            ping_id: pingData.meta?.ping_id,
            sw_version: SW_VERSION,
            response_time: performance.now() - startTime
        }
    };

    // Send pong directly via WebSocket
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        try {
            websocket.send(JSON.stringify(pongMessage));

            // Update stats
            pingPongStats.lastPongSent = Date.now();
            pingPongStats.pongCount++;

            // Calculate rolling average response time
            const responseTime = performance.now() - startTime;
            pingPongStats.averageResponseTime =
                (pingPongStats.averageResponseTime * (pingPongStats.pongCount - 1) + responseTime) / pingPongStats.pongCount;

            console.log(`Service Worker (v${SW_VERSION}): ✅ Sent pong response (${responseTime.toFixed(2)}ms)`);

        } catch (error) {
            console.error(`Service Worker (v${SW_VERSION}): Failed to send pong:`, error);
        }
    }
}

function handlePongInServiceWorker(pongData) {
    console.log(`Service Worker (v${SW_VERSION}): 🏓 Received pong from server`);

    // Update stats (if we implement client-initiated pings)
    pingPongStats.lastPongReceived = Date.now();

    // Notify main thread about connection health
    notifyClients({
        type: 'WEBSOCKET_HEALTH',
        status: 'healthy',
        lastPong: pingPongStats.lastPongReceived,
        stats: pingPongStats
    });
}

function resetPingPongStats() {
    pingPongStats = {
        lastPingReceived: 0,
        lastPongSent: 0,
        pingCount: 0,
        pongCount: 0,
        averageResponseTime: 0
    };
}

function notifyClients(message) {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage(message);
        });
    });
}

function parseWebsocketMessage(message) {
    try {
        return JSON.parse(message);
    } catch (error) {
        console.error(`Service Worker (v${SW_VERSION}): Failed to parse WebSocket message:`, error);
        return {};
    }
}