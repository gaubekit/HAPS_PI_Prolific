// heartbeat.js > default threshold = 120 sec
function startHeartbeat(intervalMs = 1000, dropoutThresholdSec = 120) {
    let lastPing = Date.now();

    // send regular ping
    setInterval(() => {
        if (typeof liveSend === "function") {
            liveSend({ type: "heartbeat", t: Date.now() });
            lastPing = Date.now();
        }
    }, intervalMs);

    // Optional: lokale Anzeige im Browser, falls Spieler "droht rauszufallen"
        /*
        setInterval(() => {
            const elapsed = (Date.now() - lastPing) / 1000;
            if (elapsed > dropoutThresholdSec) {
                console.warn("⚠️ Heartbeat stopped! Player would be flagged as dropout.");
            }
        }, 2000);
    */
}
