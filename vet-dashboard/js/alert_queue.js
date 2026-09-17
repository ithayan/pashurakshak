/**
 * PashuRakshak Veterinary Command Center - Alert Triage Queue
 */

let activeQueueFilter = "all";
let currentSelectedCase = null;

function renderAlertQueue() {
  const container = document.getElementById("alertQueueList");
  if (!container || !geoData) return;

  const filtered = geoData.cases.filter((c) => {
    if (activeQueueFilter === "all") return true;
    return c.risk_level.toLowerCase() === activeQueueFilter.toLowerCase();
  });

  container.innerHTML = "";
  filtered.forEach((c) => {
    const card = document.createElement("div");
    card.className = `case-card ${c.risk_level.toLowerCase()}`;
    card.onclick = () => zoomToCase(c.id);

    const isRed = c.risk_level === "RED";
    const badgeText = isRed ? "CRITICAL (गंभीर)" : (c.risk_level === "ORANGE" ? "HIGH (पूर्वसूचना)" : "MODERATE");

    card.innerHTML = `
      <div class="case-top">
        <div>
          <div class="case-tag">${c.tag_number} • ${c.animal_id}</div>
          <div class="case-loc">📍 ${c.block}, जि. ${c.district}</div>
        </div>
        <span class="priority-badge ${c.risk_level.toLowerCase()}">${badgeText}</span>
      </div>

      <div class="case-condition">🚨 ${c.condition_mr} (${Math.round(c.probability * 100)}%)</div>

      <div class="case-stats">
        <span>ताप: <b>${c.temperature}°C</b></span>
        <span>रवंथ: <b>${c.rumination_drop}</b></span>
        <span>अंदाज: <b>${c.lead_time}</b></span>
      </div>

      <div style="font-size: 11px; color: #CBD5E1; margin-bottom: 8px;">
        👤 शेतकरी: <b>${c.farmer_name}</b> (${c.farmer_phone})
      </div>

      <div class="case-actions" onclick="event.stopPropagation()">
        <button class="action-btn dispatch" onclick="openDispatchModal('${c.id}')">
          🚑 पथक पाठवा
        </button>
        <button class="action-btn" onclick="issueQuarantine('${c.id}')">
          🛡️ अलगीकरण
        </button>
        <button class="action-btn" onclick="broadcastVillageAlert('${c.id}')">
          📢 मेसेज पाठवा
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function setQueueFilter(filter) {
  activeQueueFilter = filter;
  document.querySelectorAll(".q-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-filter") === filter);
  });
  renderAlertQueue();
}

function openDispatchModal(caseId) {
  const c = geoData.cases.find((item) => item.id === caseId);
  if (!c) return;
  currentSelectedCase = c;

  const modal = document.getElementById("dispatchModal");
  document.getElementById("modalCaseTitle").textContent = `पशुवैद्यकीय पथक रवाना: ${c.tag_number}`;
  document.getElementById("modalCaseDesc").innerHTML = `
    तालुका: <b>${c.block} (${c.district})</b><br>
    आजार: <b>${c.condition_mr}</b> (${Math.round(c.probability * 100)}% खात्री)<br>
    शेतकरी: <b>${c.farmer_name}</b> (${c.farmer_phone})<br><br>
    नजीकच्या तालुका पशुवैद्यकीय दवाखान्याला (Dispensary Team) तात्काळ घटनास्थळी भेट देण्याचे आदेश पाठवले जातील.
  `;
  modal.style.display = "flex";
}

function closeDispatchModal() {
  document.getElementById("dispatchModal").style.display = "none";
  currentSelectedCase = null;
}

function confirmDispatch() {
  if (!currentSelectedCase) return;
  alert(`✅ आदेश जारी!\n\n${currentSelectedCase.block} येथील क्षेत्र पशुवैद्यकीय अधिकाऱ्यांना (Live Field Vet) तत्काळ भेटीसाठी एसएमएस आणि जीपीएस लोकेशन पाठवण्यात आले आहे.`);
  closeDispatchModal();
}

function issueQuarantine(caseId) {
  const c = geoData.cases.find((item) => item.id === caseId);
  if (!c) return;
  alert(`🛡️ अलगीकरण आदेश (Quarantine Order):\n\n${c.tag_number} साठी ५० फूट सुरक्षित अंतर राखण्याचे परिपत्रक शेतकरी ${c.farmer_name} यांना व्हॉट्सॲपवर पाठवले गेले.`);
}

function broadcastVillageAlert(caseId) {
  const c = geoData.cases.find((item) => item.id === caseId);
  if (!c) return;
  alert(`📢 ग्राम सतर्कता प्रसारण:\n\n${c.block} परिसरातील नोंदणीकृत ५८ दुग्ध उत्पादक शेतकऱ्यांना लाळ्या खुरकूत / संसर्ग प्रतिबंधक सतर्कता मेसेज पाठवण्यात आला.`);
}
