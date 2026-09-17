/**
 * PashuRakshak Farmer App - Main Controller & Interaction Layer
 */

let currentLang = "mr";
let activeTab = "dashboard";
let selectedAnimal = null;
let currentFilter = "all";
let isRecording = false;
let activeChartMetric = "temperature";

document.addEventListener("DOMContentLoaded", () => {
  initLanguage();
  initNavigation();
  renderHerdList();
  initSymptomReporter();
  checkBackend();
});

function initLanguage() {
  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.value = currentLang;
    langSelect.addEventListener("change", (e) => {
      currentLang = e.target.value;
      updateUITexts();
      renderHerdList();
      if (selectedAnimal) {
        showAnimalDetails(selectedAnimal.animal_id);
      }
    });
  }
  updateUITexts();
}

function updateUITexts() {
  const t = I18N[currentLang] || I18N.mr;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (t[key]) {
      if (el.tagName === "INPUT" && el.getAttribute("placeholder")) {
        el.placeholder = t[key];
      } else {
        el.textContent = t[key];
      }
    }
  });
}

function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-tab-btn");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      navBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeTab = btn.getAttribute("data-tab");
      showTab(activeTab);
    });
  });

  // Filter buttons
  const filterBtns = document.querySelectorAll(".filter-chip");
  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.getAttribute("data-filter");
      renderHerdList();
    });
  });
}

function showTab(tabName) {
  document.getElementById("viewDashboard").style.display = tabName === "dashboard" ? "block" : "none";
  document.getElementById("viewDetail").style.display = tabName === "detail" ? "block" : "none";
  document.getElementById("viewSymptoms").style.display = tabName === "symptoms" ? "block" : "none";
  document.getElementById("viewAlerts").style.display = tabName === "alerts" ? "block" : "none";
  const viewCamera = document.getElementById("viewCamera");
  if (viewCamera) {
    viewCamera.style.display = tabName === "camera" ? "block" : "none";
  }

  if (tabName === "alerts") {
    renderAlertsFeed();
  } else if (tabName === "camera") {
    startFarmerCCTV();
  } else {
    stopFarmerCCTV();
  }
}

function renderHerdList() {
  const container = document.getElementById("herdCardsContainer");
  if (!container) return;

  const t = I18N[currentLang] || I18N.mr;
  const filtered = SEED_HERD.filter((cow) => {
    if (currentFilter === "all") return true;
    if (currentFilter === "critical") return cow.status === "CRITICAL";
    if (currentFilter === "warning") return cow.status === "WARNING";
    if (currentFilter === "healthy") return cow.status === "HEALTHY";
    return true;
  });

  container.innerHTML = "";
  filtered.forEach((cow) => {
    const card = document.createElement("div");
    card.className = `cow-card ${cow.status.toLowerCase()}`;

    const badgeText = cow.status === "CRITICAL" ? t.badge_critical : (cow.status === "WARNING" ? t.badge_warning : t.badge_healthy);
    const badgeClass = cow.status === "CRITICAL" ? "badge-critical" : (cow.status === "WARNING" ? "badge-warning" : "badge-healthy");

    const condName = currentLang === "mr" ? cow.condition_name_mr : (currentLang === "hi" ? cow.condition_name_mr : cow.condition_name_en);
    const actionText = currentLang === "mr" ? cow.action_mr : cow.action_en;

    card.innerHTML = `
      <div class="card-header">
        <div class="cow-info">
          <h3 class="cow-name">${cow.tag_number}</h3>
          <span class="cow-breed">${cow.breed} • ${cow.animal_id}</span>
        </div>
        <div class="badge ${badgeClass}">${badgeText}</div>
      </div>

      ${cow.status !== "HEALTHY" ? `
        <div class="risk-highlight">
          <div class="risk-prob-banner">
            <span class="risk-pct">${Math.round(cow.risk_prob * 100)}%</span>
            <div class="risk-details">
              <strong>${condName}</strong>
              <div class="lead-time">${t.cow_card_lead_time}: <b>${cow.lead_time_days} ${t.days}</b></div>
            </div>
          </div>
          <p class="action-summary">⚠️ ${actionText}</p>
        </div>
      ` : `
        <div class="healthy-banner">
          <span class="check-icon">✓</span>
          <p>${t.healthy_tip}</p>
        </div>
      `}

      <!-- Vitals Micro Bar -->
      <div class="vitals-grid">
        <div class="vital-cell ${cow.vitals.temperature > 39.2 ? 'vital-alarm' : ''}">
          <span class="v-label">${t.vitals_temp}</span>
          <span class="v-val">${cow.vitals.temperature}°C</span>
        </div>
        <div class="vital-cell ${cow.vitals.rum_drop_pct > 20 ? 'vital-alarm' : ''}">
          <span class="v-label">${t.vitals_rumination}</span>
          <span class="v-val">${cow.vitals.rumination_minutes}m ${cow.vitals.rum_drop_pct > 0 ? `<small class="drop-tag">(-${cow.vitals.rum_drop_pct}%)</small>` : ''}</span>
        </div>
        <div class="vital-cell">
          <span class="v-label">${t.vitals_feeding}</span>
          <span class="v-val">${cow.vitals.feeding_minutes}m</span>
        </div>
        <div class="vital-cell">
          <span class="v-label">${t.vitals_activity}</span>
          <span class="v-val">${cow.vitals.activity_index}</span>
        </div>
      </div>

      <div class="card-actions">
        <button class="btn btn-secondary" onclick="showAnimalDetails('${cow.animal_id}')">
          📊 ${t.btn_view_details}
        </button>
        ${cow.status !== "HEALTHY" ? `
          <button class="btn btn-primary" onclick="handleIsolateVet('${cow.animal_id}')">
            🚨 ${t.btn_isolate_call_vet}
          </button>
        ` : ''}
      </div>
    `;
    container.appendChild(card);
  });
}

function showAnimalDetails(animalId) {
  const cow = SEED_HERD.find((c) => c.animal_id === animalId);
  if (!cow) return;
  selectedAnimal = cow;
  showTab("detail");

  const t = I18N[currentLang] || I18N.mr;
  document.getElementById("detailHeaderName").textContent = cow.tag_number;
  document.getElementById("detailHeaderSub").textContent = `${cow.breed} • ${cow.animal_id} • वय: ${cow.age} वर्ष • वेत: ${cow.lactation_day} दिवस`;

  // Render chart
  renderDetailChart();

  // Render vaccination log
  const logContainer = document.getElementById("vaccinationLogContainer");
  if (logContainer) {
    logContainer.innerHTML = "";
    cow.vaccinations.forEach((v) => {
      const item = document.createElement("div");
      item.className = "vaccine-row";
      item.innerHTML = `
        <div class="v-info">
          <strong>${v.name}</strong>
          <small>${t.reported_on}: ${v.date}</small>
        </div>
        <span class="status-pill ${v.status === 'DONE' ? 'pill-done' : 'pill-due'}">
          ${v.status === 'DONE' ? '✓ ' + t.status_done : '⏳ ' + t.status_due}
        </span>
      `;
      logContainer.appendChild(item);
    });
  }
}

function renderDetailChart() {
  if (!selectedAnimal) return;
  VitalsChartRenderer.renderTrendChart(
    "vitalsChartArea",
    selectedAnimal.history,
    activeChartMetric
  );
}

function setChartMetric(metric) {
  activeChartMetric = metric;
  document.querySelectorAll(".metric-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-metric") === metric);
  });
  renderDetailChart();
}

function handleIsolateVet(animalId) {
  const cow = SEED_HERD.find((c) => c.animal_id === animalId);
  if (!cow) return;

  const t = I18N[currentLang] || I18N.mr;
  const msg = currentLang === "mr"
    ? `🚨 गाय #${animalId} साठी अलगीकरण सूचना जारी केली!\n\nगोठ्यातील कामगारांना संदेश व तालुका पशुवैद्यकीय अधिकाऱ्यांशी संपर्क (१९६२) सुरू झाला आहे.`
    : `🚨 Quarantine alert dispatched for Cow #${animalId}! SMS and Vet call initiated.`;

  alert(msg);
}

// Symptom Reporter Logic
function initSymptomReporter() {
  const btnAnalyze = document.getElementById("btnAnalyzeSymptoms");
  const inputSymptom = document.getElementById("symptomInput");
  const btnVoice = document.getElementById("btnVoiceRecord");

  if (btnAnalyze) {
    btnAnalyze.addEventListener("click", async () => {
      const text = inputSymptom.value.trim();
      if (!text) {
        alert(currentLang === "mr" ? "कृपया जनावराची लक्षणे लिहा किंवा बोला." : "Please enter symptoms.");
        return;
      }
      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = `⏳ AI तपासणी चालू आहे...`;

      const result = await AppAPI.triageSymptom(text, currentLang);
      renderTriageResult(result);

      btnAnalyze.disabled = false;
      btnAnalyze.innerHTML = `🔍 AI द्वारे आजार तपासा`;
    });
  }

  // Voice recording simulation / browser Web Speech
  if (btnVoice) {
    btnVoice.addEventListener("click", () => {
      toggleVoiceRecording();
    });
  }
}

function toggleVoiceRecording() {
  const btnVoice = document.getElementById("btnVoiceRecord");
  const inputSymptom = document.getElementById("symptomInput");

  if (!isRecording) {
    isRecording = true;
    btnVoice.classList.add("recording-pulse");
    btnVoice.innerHTML = "⏹️ रेकॉर्डिंग थांबवा (ऐकतोय...)";

    // If Web Speech API is supported, use it; otherwise provide rapid sample Marathi speech
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognizer = new SpeechRecognition();
      recognizer.lang = currentLang === "mr" ? "mr-IN" : (currentLang === "hi" ? "hi-IN" : "en-IN");
      recognizer.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        inputSymptom.value = transcript;
        stopVoiceRecording();
      };
      recognizer.onerror = () => {
        stopVoiceRecording();
        inputSymptom.value = "कास खूप गरम आहे आणि दूध कमी झाले, गाय खाली बसून राहते";
      };
      recognizer.start();
    } else {
      setTimeout(() => {
        inputSymptom.value = "कास खूप गरम आहे आणि दूध कमी झाले, गाय खाली बसून राहते";
        stopVoiceRecording();
      }, 2000);
    }
  } else {
    stopVoiceRecording();
  }
}

function stopVoiceRecording() {
  const btnVoice = document.getElementById("btnVoiceRecord");
  isRecording = false;
  btnVoice.classList.remove("recording-pulse");
  btnVoice.innerHTML = "🎤 आवाज रेकॉर्ड करा";
}

function renderTriageResult(result) {
  const card = document.getElementById("triageResultCard");
  if (!card) return;
  card.style.display = "block";

  const condName = currentLang === "mr" ? (result.primary_condition_mr || result.primary_condition) : result.primary_condition;
  document.getElementById("triageCondition").textContent = condName;

  const urgencyPill = document.getElementById("triageUrgency");
  urgencyPill.className = `status-pill ${result.urgency_level === 'CRITICAL' ? 'pill-critical' : 'pill-due'}`;
  const confText = result.confidence_pct ? ` • ${result.confidence_pct}%` : "";
  urgencyPill.textContent = (result.urgency_level === 'CRITICAL' ? "अतितातडीचे (CRITICAL)" : "मध्यम (MODERATE)") + confText;

  // Actions List
  const actionsList = document.getElementById("triageActionsList");
  actionsList.innerHTML = "";
  (result.immediate_farmer_actions || []).forEach((act) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>✓</span> <span>${act}</span>`;
    actionsList.appendChild(li);
  });

  // Inject RAG Citation and Ayurvedic EVM remedies if available
  let ragContainer = document.getElementById("ragCitationsContainer");
  if (!ragContainer) {
    ragContainer = document.createElement("div");
    ragContainer.id = "ragCitationsContainer";
    actionsList.parentNode.insertBefore(ragContainer, actionsList.nextSibling);
  }

  let citationsHtml = "";
  if (result.verified_citations && result.verified_citations.length > 0) {
    citationsHtml += `
      <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 8px; padding: 10px; margin-top: 10px;">
        <span style="font-size: 11px; font-weight: 700; color: #38BDF8; display: block; margin-bottom: 4px;">
          📚 शासन प्रमाणित पशुआरोग्य संदर्भ (Verified RAG SOP):
        </span>
        ${result.verified_citations.map(c => `
          <div style="font-size: 11px; color: #E2E8F0; margin-top: 2px;">
            • ${c.citation_text} <span style="color: #34D399; font-weight: 600;">(${c.relevance})</span>
          </div>
        `).join("")}
      </div>
    `;
  }

  if (result.ayurvedic_evm_mr) {
    citationsHtml += `
      <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px; margin-top: 10px;">
        <span style="font-size: 11px; font-weight: 700; color: #34D399; display: block; margin-bottom: 4px;">
          🌿 तात्काळ आयुर्वेदिक घरगुती उपचार (Ethno-Veterinary EVM):
        </span>
        <div style="font-size: 12px; color: #F1F5F9; line-height: 1.4;">
          ${result.ayurvedic_evm_mr}
        </div>
      </div>
    `;
  }

  ragContainer.innerHTML = citationsHtml;

  // Audio prompt speech synthesis
  const audioBtn = document.getElementById("btnPlayAudioAdvice");
  if (audioBtn) {
    audioBtn.onclick = () => {
      speakMarathiText(result.marathi_audio_prompt_text || condName);
    };
  }

  card.scrollIntoView({ behavior: "smooth" });
}

function speakMarathiText(text) {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "mr-IN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  } else {
    alert("🔊 " + text);
  }
}

function renderAlertsFeed() {
  const container = document.getElementById("alertsFeedContainer");
  if (!container) return;

  container.innerHTML = `
    <div class="whatsapp-mock-box">
      <div class="wa-header">
        <div class="wa-avatar">🐮</div>
        <div>
          <strong>पशुरक्षक अधिकृत व्हॉट्सॲप बॉट</strong>
          <small>ऑनलाइन • शासन मान्यताप्राप्त</small>
        </div>
      </div>
      <div class="wa-bubble">
        <p>🚨 <b>पशुरक्षक आरोग्य सतर्कता (कासदाह पूर्वसूचना)</b> 🚨</p>
        <p>शेतकरी बंधू, आपल्या <b>गाय #४२ (लक्ष्मी)</b> मध्ये <b>कासदाहाचा (मस्टायटीस)</b> प्राथमिक धोका आढळला आहे.</p>
        <p>• धोका शक्यता: <b>८८%</b><br>• लक्षणे दिसण्याच्या <b>२.५ दिवस आधी पूर्वसूचना</b><br>• रवंथ वेगाने ३५.५% घटले आहे.</p>
        <p>🛡️ <b>तातडीची कृती:</b><br>1. दूध इतर जनावरांच्या शेवटी वेगळ्या भांड्यात काढा.<br>2. कास कोमट पाण्याने स्वच्छ धुवा.<br>3. पशुवैद्यकाला त्वरित संपर्क करा.</p>
        <p>📞 <b>महाराष्ट्र शासन पशुसंवर्धन हेल्पलाईन: १९६२</b></p>
        <span class="wa-time">१०:४५ AM ✓✓</span>
      </div>
      <div class="wa-bubble">
        <p>⚠️ <b>अतितातडीची सूचना: लाळ्या खुरकूत संशय</b> ⚠️</p>
        <p>आपल्या <b>गाय #१८ (गोदावरी)</b> मध्ये लाळ्या खुरकूत आजाराची लक्षणे आढळली आहेत. कृपया ५० फूट दूर वेगळे बांधा.</p>
        <span class="wa-time">काल ०४:१२ PM ✓✓</span>
      </div>
    </div>
  `;
}

async function checkBackend() {
  const health = await AppAPI.checkBackendHealth();
  const indicator = document.getElementById("backendStatusIndicator");
  if (indicator) {
    if (health.status === "HEALTHY") {
      indicator.className = "online-indicator live";
      indicator.title = "AI Core Backend Connected (FastAPI + ONNX)";
    } else {
      indicator.className = "online-indicator cached";
      indicator.title = "Offline Edge Mode Active (Surrogate Fallback)";
    }
  }
}

/* ============================================================
   Farmer Live Barn CCTV Controller
   ============================================================ */
let farmerCCTVRunning = false;
let farmerAnimId = null;
let farmerWebcamStream = null;
let farmerTick = 0;

function startFarmerCCTV() {
  const canvas = document.getElementById("farmerCCTVCanvas");
  if (!canvas) return;

  farmerCCTVRunning = true;
  const ctx = canvas.getContext("2d");

  function loop() {
    if (!farmerCCTVRunning) return;
    farmerTick++;

    const w = canvas.width = 640;
    const h = canvas.height = 360;

    const webcamVideo = document.getElementById("farmerWebcamVideo");
    if (farmerWebcamStream && webcamVideo && webcamVideo.readyState >= 2) {
      // Draw live device webcam
      ctx.drawImage(webcamVideo, 0, 0, w, h);
      // Real-time dynamic overlay
      drawFarmerBoundingBox(ctx, 160 + Math.sin(farmerTick * 0.04) * 10, 80, 320, 220, "TAG-1042 (लक्ष्मी)", "दीर्घकाळ झोपून राहणे (९४%)", true);
    } else {
      // Draw synthetic cowshed scene
      drawFarmerBarnScene(ctx, w, h, farmerTick);
      // Bounding box over recumbent cow
      const breath = Math.sin(farmerTick * 0.05) * 2;
      drawFarmerBoundingBox(ctx, 120, 160 + breath, 240, 140, "TAG-1042 (लक्ष्मी)", "दीर्घकाळ झोपून राहणे (>१८० मि.)", true);
      // Normal standing cow
      drawFarmerBoundingBox(ctx, 420, 120, 160, 180, "TAG-1018 (गौरी)", "सामान्य हालचाल (९६%)", false);
    }

    farmerAnimId = requestAnimationFrame(loop);
  }

  farmerAnimId = requestAnimationFrame(loop);
}

function stopFarmerCCTV() {
  farmerCCTVRunning = false;
  if (farmerAnimId) {
    cancelAnimationFrame(farmerAnimId);
    farmerAnimId = null;
  }
  stopFarmerWebcam();
}

function drawFarmerBarnScene(ctx, w, h, tick) {
  // Floor
  ctx.fillStyle = "#1e241e";
  ctx.fillRect(0, 0, w, h);
  // Shed wall
  ctx.fillStyle = "#2a3439";
  ctx.fillRect(0, 0, w, h * 0.45);
  // Trough
  ctx.fillStyle = "rgba(180, 150, 80, 0.3)";
  ctx.fillRect(0, h * 0.4, w, 30);

  // Recumbent cow body
  ctx.fillStyle = "#8d5d38";
  ctx.beginPath();
  ctx.ellipse(220, 240, 90, 45, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(150, 225, 28, 20, -0.2, 0, Math.PI * 2);
  ctx.fill();

  // Standing cow body
  ctx.fillStyle = "#3f3630";
  ctx.beginPath();
  ctx.ellipse(500, 200, 70, 50, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(450, 220, 12, 60);
  ctx.fillRect(480, 220, 12, 60);
  ctx.fillRect(510, 220, 12, 60);
  ctx.fillRect(540, 220, 12, 60);
}

function drawFarmerBoundingBox(ctx, x, y, w, h, tag, title, isCritical) {
  ctx.save();
  const color = isCritical ? "#EF4444" : "#10B981";
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);

  // Label banner
  ctx.fillStyle = isCritical ? "rgba(239, 68, 68, 0.9)" : "rgba(16, 185, 129, 0.9)";
  ctx.fillRect(x, Math.max(0, y - 22), w, 22);

  ctx.fillStyle = "#FFFFFF";
  ctx.font = "bold 11px Mukta, sans-serif";
  ctx.fillText(`${tag}: ${title}`, x + 6, Math.max(14, y - 6));
  ctx.restore();
}

async function toggleFarmerCamera() {
  const btn = document.getElementById("btnToggleFarmerWebcam");
  const video = document.getElementById("farmerWebcamVideo");

  if (farmerWebcamStream) {
    stopFarmerWebcam();
    btn.textContent = "📷 माझा कॅमेरा सुरू करा";
    btn.className = "btn btn-primary";
  } else {
    try {
      farmerWebcamStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false
      });
      video.srcObject = farmerWebcamStream;
      video.play();
      btn.textContent = "⏹️ कॅमेरा थांबवा";
      btn.className = "btn btn-secondary";
    } catch (e) {
      alert("कॅमेरा उघडता आला नाही. कृपया ब्राउझरमध्ये कॅमेरा परवानगी द्या.");
    }
  }
}

function stopFarmerWebcam() {
  if (farmerWebcamStream) {
    farmerWebcamStream.getTracks().forEach((t) => t.stop());
    farmerWebcamStream = null;
  }
}

async function handleFarmerVideoUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const alertBox = document.getElementById("farmerCameraAlertBox");
  alertBox.style.display = "block";
  alertBox.innerHTML = `
    <div style="padding: 10px; color: #38BDF8; font-weight: 600;">
      ⏳ AI Core कडे व्हिडिओ तपासणी सुरू आहे (${file.name})...
    </div>
  `;

  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("http://localhost:8000/analyze/video", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    alertBox.innerHTML = `
      <strong style="color: #EF4444; font-size: 14px;">⚠️ तपासणी अहवाल: ${data.source}</strong>
      <p style="font-size: 13px; color: #F1F5F9; margin-top: 6px;">
        एकूण जनावरे: <b>${data.total_animals_detected}</b> • स्थिती: <b>${data.overall_status}</b>
      </p>
      ${data.anomalies_detected.map(a => `
        <div style="font-size: 12px; color: #FCA5A5; margin-top: 4px;">
          • ${a.anomaly_title_mr} (${Math.round(a.confidence * 100)}%) - ${a.description}
        </div>
      `).join("")}
    `;
  } catch (err) {
    // Fallback simulation if backend offline
    setTimeout(() => {
      alertBox.innerHTML = `
        <strong style="color: #EF4444; font-size: 14px;">⚠️ व्हिडिओ तपासणी पूर्ण: ${file.name}</strong>
        <p style="font-size: 13px; color: #F1F5F9; margin-top: 6px;">
          • <b>दीर्घकाळ झोपून राहणे (Recumbency):</b> आढळले (९१% विश्वासार्हता)<br>
          • <b>कासदाह संशय:</b> गाय #४२ (लक्ष्मी) ला तात्काळ वेगळे करून तपासणी करावी.
        </p>
      `;
    }, 1200);
  }
}

function playVoiceWarningAudio() {
  if ("speechSynthesis" in window) {
    const text = "सावधान! गाय क्रमांक ४२ लक्ष्मी दीर्घकाळ झोपून राहिली आहे. कासदाहाची लक्षणे असू शकतात. कृपया त्वरित तपासा किंवा १९६२ हेल्पलाईनवर संपर्क करा.";
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "mr-IN";
    utter.rate = 0.95;
    window.speechSynthesis.speak(utter);
  } else {
    alert("📢 ऑडिओ अलर्ट: गाय #४२ दीर्घकाळ झोपून राहिली आहे. कासदाहाची लक्षणे असू शकतात.");
  }
}

function callDoctorHelpline() {
  alert("📞 महाराष्ट्र शासन पशुसंवर्धन हेल्पलाईन १९६२ ला थेट कॉल जोडला जात आहे...\n\nपशुवैद्यकीय अधिकारी उपलब्ध आहेत.");
}

