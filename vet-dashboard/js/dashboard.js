/**
 * PashuRakshak Veterinary Command Center - Master Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
  await initGISMap();
  initDashboardControls();
  renderAlertQueue();
  updateTopMetrics();
});

function initDashboardControls() {
  const toggleVaccine = document.getElementById("toggleVaccineOverlay");
  if (toggleVaccine) {
    toggleVaccine.addEventListener("change", (e) => {
      toggleVaccinationOverlay(e.target.checked);
    });
  }
}

function updateTopMetrics() {
  if (!geoData) return;

  const totalFlags = geoData.districts.reduce((sum, d) => sum + d.active_flags, 0);
  const redCases = geoData.cases.filter((c) => c.risk_level === "RED").length;
  const avgVaccine = Math.round(
    geoData.districts.reduce((sum, d) => sum + d.vaccination_coverage_pct, 0) / geoData.districts.length
  );

  const elTotal = document.getElementById("metricTotalFlags");
  const elCritical = document.getElementById("metricCriticalCases");
  const elVaccine = document.getElementById("metricAvgVaccine");

  if (elTotal) elTotal.textContent = totalFlags;
  if (elCritical) elCritical.textContent = redCases;
  if (elVaccine) elVaccine.textContent = `${avgVaccine}%`;
}
