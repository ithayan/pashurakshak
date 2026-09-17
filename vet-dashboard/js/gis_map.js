/**
 * PashuRakshak Veterinary Command Center - GIS Leaflet Map Engine
 */

let mapInstance = null;
let districtLayers = [];
let caseMarkers = [];
let showVaccinationLayer = false;
let geoData = null;

async function initGISMap() {
  // Center over Maharashtra State
  mapInstance = L.map("leafletMap", {
    zoomControl: true,
    minZoom: 6,
    maxZoom: 14
  }).setView([18.7, 74.8], 7);

  // CartoDB Dark Matter tile layer for premium dark command center look
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://carto.com/">CartoDB</a> | Govt. of Maharashtra Animal Husbandry Dept.',
    subdomains: "abcd",
    maxZoom: 19
  }).addTo(mapInstance);

  try {
    const res = await fetch("data/maharashtra_geodata.json");
    geoData = await res.json();
    renderDistrictClusters();
    renderCaseMarkers();
  } catch (e) {
    console.error("Error loading geodata:", e);
  }
}

function renderDistrictClusters() {
  if (!mapInstance || !geoData) return;

  // Clear existing district layers
  districtLayers.forEach((l) => mapInstance.removeLayer(l));
  districtLayers = [];

  geoData.districts.forEach((dist) => {
    let circleColor = "#10B981";
    let fillColor = "#10B981";
    let fillOpacity = 0.25;

    if (showVaccinationLayer) {
      // Vaccination Coverage Mode: Green > 80%, Amber 70-80%, Red < 70%
      if (dist.vaccination_coverage_pct >= 80) {
        circleColor = "#10B981";
        fillColor = "#10B981";
      } else if (dist.vaccination_coverage_pct >= 70) {
        circleColor = "#F59E0B";
        fillColor = "#F59E0B";
      } else {
        circleColor = "#EF4444";
        fillColor = "#EF4444";
        fillOpacity = 0.35;
      }
    } else {
      // Outbreak Risk Mode
      if (dist.risk_status === "CRITICAL") {
        circleColor = "#EF4444";
        fillColor = "#EF4444";
        fillOpacity = 0.35;
      } else if (dist.risk_status === "MEDIUM") {
        circleColor = "#F59E0B";
        fillColor = "#F59E0B";
        fillOpacity = 0.25;
      } else {
        circleColor = "#10B981";
        fillColor = "#10B981";
        fillOpacity = 0.15;
      }
    }

    const radius = 24000 + dist.active_flags * 600;

    const circle = L.circle([dist.lat, dist.lng], {
      color: circleColor,
      fillColor: fillColor,
      fillOpacity: fillOpacity,
      weight: 2,
      radius: radius
    }).addTo(mapInstance);

    const popupContent = `
      <div style="font-family: 'Mukta', 'Inter', sans-serif; color: #1E293B; min-width: 200px;">
        <h3 style="margin: 0 0 4px; font-size: 16px; font-weight: 800;">${dist.name_mr} (${dist.name_en})</h3>
        <p style="margin: 2px 0; font-size: 12px;">पशुधन लोकसंख्या: <b>${dist.cattle_population.toLocaleString()}</b></p>
        <p style="margin: 2px 0; font-size: 12px;">लसीकरण प्रमाण: <b>${dist.vaccination_coverage_pct}%</b></p>
        <p style="margin: 2px 0; font-size: 12px; color: ${dist.active_flags > 20 ? '#DC2626' : '#D97706'};">सक्रिय पूर्वसूचना: <b>${dist.active_flags} केसेस</b></p>
        <p style="margin: 4px 0 0; font-size: 11px; color: #64748B;">प्रमुख तालुके: ${dist.blocks.join(", ")}</p>
      </div>
    `;
    circle.bindPopup(popupContent);
    districtLayers.push(circle);
  });
}

function renderCaseMarkers() {
  if (!mapInstance || !geoData) return;

  caseMarkers.forEach((m) => mapInstance.removeLayer(m));
  caseMarkers = [];

  geoData.cases.forEach((c) => {
    const isRed = c.risk_level === "RED";
    const isOrange = c.risk_level === "ORANGE";
    const markerColor = isRed ? "#EF4444" : (isOrange ? "#F59E0B" : "#FBBF24");

    const customIcon = L.divIcon({
      className: "custom-map-pin",
      html: `
        <div style="
          background-color: ${markerColor};
          width: 18px;
          height: 18px;
          border-radius: 50%;
          border: 2px solid #FFFFFF;
          box-shadow: 0 0 12px ${markerColor};
          animation: ${isRed ? 'pulseAlarm 1.8s infinite' : 'none'};
        "></div>
      `,
      iconSize: [18, 18],
      iconAnchor: [9, 9]
    });

    const marker = L.marker([c.lat, c.lng], { icon: customIcon }).addTo(mapInstance);

    const popupHtml = `
      <div style="font-family: 'Mukta', 'Inter', sans-serif; color: #0F172A; min-width: 220px;">
        <h4 style="margin: 0; font-size: 15px; font-weight: 800;">${c.tag_number} • ${c.animal_id}</h4>
        <span style="font-size: 11px; color: #64748B;">स्थान: ${c.block}, जि. ${c.district}</span>
        <hr style="margin: 6px 0; border: none; border-top: 1px solid #E2E8F0;"/>
        <p style="margin: 2px 0; font-size: 13px; font-weight: 700; color: ${isRed ? '#DC2626' : '#D97706'};">
          🚨 ${c.condition_mr} (${Math.round(c.probability * 100)}%)
        </p>
        <p style="margin: 2px 0; font-size: 12px;">लक्षण पूर्वसूचना: <b>${c.lead_time}</b></p>
        <p style="margin: 2px 0; font-size: 12px;">तापमान: <b>${c.temperature}°C</b> • रवंथ घट: <b>${c.rumination_drop}</b></p>
        <p style="margin: 2px 0; font-size: 12px;">शेतकरी: <b>${c.farmer_name}</b> (${c.farmer_phone})</p>
        <div style="margin-top: 8px;">
          <button onclick="openDispatchModal('${c.id}')" style="
            background: #EF4444;
            color: #FFF;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
          ">🚨 तालुका पथक रवाना करा</button>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    caseMarkers.push(marker);
  });
}

function toggleVaccinationOverlay(enabled) {
  showVaccinationLayer = enabled;
  renderDistrictClusters();
}

function zoomToCase(caseId) {
  if (!geoData) return;
  const c = geoData.cases.find((item) => item.id === caseId);
  if (c && mapInstance) {
    mapInstance.flyTo([c.lat, c.lng], 12, { duration: 1.2 });
  }
}
