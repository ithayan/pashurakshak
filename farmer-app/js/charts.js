/**
 * PashuRakshak Lightweight SVG Vitals Chart Engine
 * Zero external dependencies, pure SVG, optimized for 2G rural mobile connections.
 */

class VitalsChartRenderer {
  static renderTrendChart(containerId, historyData, activeMetric = "temperature") {
    const container = document.getElementById(containerId);
    if (!container) return;

    const metricConfigs = {
      temperature: {
        label: "शरीराचे तापमान (°C)",
        unit: "°C",
        color: "#EF4444",
        min: 37.5,
        max: 41.5,
        threshold: 39.2,
        thresholdLabel: "तापमान मर्यादा (३९.२°)"
      },
      rumination: {
        label: "रवंथ वेळ (मिनिटे/दिवस)",
        unit: " min",
        color: "#3B82F6",
        min: 200,
        max: 550,
        threshold: 380,
        thresholdLabel: "सामान्य रवंथ मर्यादा"
      },
      feeding: {
        label: "चारा खाणे (मिनिटे/दिवस)",
        unit: " min",
        color: "#10B981",
        min: 120,
        max: 320,
        threshold: 200,
        thresholdLabel: "किमान चारा मर्यादा"
      },
      activity: {
        label: "हालचाल / सक्रियता निर्देशांक",
        unit: " pts",
        color: "#F59E0B",
        min: 50,
        max: 120,
        threshold: 80,
        thresholdLabel: "किमान सक्रियता"
      }
    };

    const cfg = metricConfigs[activeMetric] || metricConfigs.temperature;
    const width = container.clientWidth || 360;
    const height = 180;
    const padding = { top: 25, right: 20, bottom: 30, left: 40 };

    const plotW = width - padding.left - padding.right;
    const plotH = height - padding.top - padding.bottom;

    const n = historyData.length;
    if (n < 2) return;

    // Coordinate mapping
    const getX = (idx) => padding.left + (idx / (n - 1)) * plotW;
    const getY = (val) => {
      const clamped = Math.max(cfg.min, Math.min(cfg.max, val));
      const pct = (clamped - cfg.min) / (cfg.max - cfg.min);
      return padding.top + (1 - pct) * plotH;
    };

    const points = historyData.map((d, i) => ({
      x: getX(i),
      y: getY(d[activeMetric]),
      val: d[activeMetric],
      day: d.day
    }));

    // Generate path data
    let dPath = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      const p0 = points[i - 1];
      const p1 = points[i];
      const cpx1 = p0.x + (p1.x - p0.x) / 2;
      const cpy1 = p0.y;
      const cpx2 = p0.x + (p1.x - p0.x) / 2;
      const cpy2 = p1.y;
      dPath += ` C ${cpx1} ${cpy1}, ${cpx2} ${cpy2}, ${p1.x} ${p1.y}`;
    }

    // Gradient area path
    const areaPath = `${dPath} L ${points[points.length - 1].x} ${padding.top + plotH} L ${points[0].x} ${padding.top + plotH} Z`;

    const thresholdY = getY(cfg.threshold);

    // SVG construction
    let svg = `
      <svg viewBox="0 0 ${width} ${height}" class="vitals-svg-chart">
        <defs>
          <linearGradient id="chartGrad_${activeMetric}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="${cfg.color}" stop-opacity="0.35"/>
            <stop offset="100%" stop-color="${cfg.color}" stop-opacity="0.0"/>
          </linearGradient>
        </defs>

        <!-- Grid Lines & Y Labels -->
        <line x1="${padding.left}" y1="${padding.top}" x2="${width - padding.right}" y2="${padding.top}" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3"/>
        <line x1="${padding.left}" y1="${padding.top + plotH / 2}" x2="${width - padding.right}" y2="${padding.top + plotH / 2}" stroke="rgba(255,255,255,0.08)" stroke-dasharray="3,3"/>
        <line x1="${padding.left}" y1="${padding.top + plotH}" x2="${width - padding.right}" y2="${padding.top + plotH}" stroke="rgba(255,255,255,0.15)"/>

        <!-- Threshold line -->
        <line x1="${padding.left}" y1="${thresholdY}" x2="${width - padding.right}" y2="${thresholdY}" stroke="rgba(239, 68, 68, 0.5)" stroke-dasharray="4,4"/>
        <text x="${width - padding.right}" y="${thresholdY - 4}" text-anchor="end" fill="rgba(239, 68, 68, 0.7)" font-size="9">${cfg.thresholdLabel}</text>

        <!-- Shaded Area -->
        <path d="${areaPath}" fill="url(#chartGrad_${activeMetric})" />

        <!-- Line Curve -->
        <path d="${dPath}" fill="none" stroke="${cfg.color}" stroke-width="2.5" stroke-linecap="round"/>

        <!-- Points and Day labels -->
    `;

    points.forEach((p) => {
      svg += `
        <circle cx="${p.x}" cy="${p.y}" r="4" fill="#0B1512" stroke="${cfg.color}" stroke-width="2.2" />
        <text x="${p.x}" y="${p.y - 8}" text-anchor="middle" fill="#E2E8F0" font-size="10" font-weight="600">${p.val}${cfg.unit}</text>
        <text x="${p.x}" y="${height - 10}" text-anchor="middle" fill="#94A3B8" font-size="11">${p.day}</text>
      `;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }
}
