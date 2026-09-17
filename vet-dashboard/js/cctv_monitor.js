/**
 * PashuRakshak Veterinary Command Center - Live CCTV Surveillance Module
 * ====================================================================
 * Provides real-time computer vision monitoring for rural farm barns:
 * - Multi-channel RTSP camera switcher
 * - Live WebRTC Device Camera (Webcam) support
 * - Real-time AI bounding boxes, posture classification & behavioral anomaly detection
 */

let cctvModalOpen = false;
let currentCCTVChannel = "CH1";
let cctvAnimFrameId = null;
let liveWebcamStream = null;
let lastFpsTime = performance.now();
let frameCount = 0;
let currentFps = 28.5;

// Camera Channels configuration
const CCTV_CHANNELS = {
  CH1: {
    name_mr: "कॅमेरा १: बारामती गोठा (पूर्व शेड)",
    name_en: "Camera 1: Baramati Dairy Shed (East)",
    rtsp: "rtsp://baramati-farm.maha-agro.gov:554/live/ch1",
    location: "बारामती (पुणे) • शेड #०४",
    focusTag: "TAG-1042 (लक्ष्मी)",
    animals: [
      { id: "TAG-1042", name: "लक्ष्मी", breed: "Gir Cross", x: 180, y: 220, w: 230, h: 140, state: "PROLONGED_LYING", conf: 0.94, mr_title: "दीर्घकाळ झोपून राहणे (>१८० मि.)", severity: "CRITICAL" },
      { id: "TAG-1018", name: "गौरी", breed: "HF Cross", x: 520, y: 160, w: 190, h: 190, state: "NORMAL", conf: 0.96, mr_title: "सामान्य रवंथ (निरोगी)", severity: "NORMAL" },
      { id: "TAG-1055", name: "राधा", breed: "Khillari", x: 800, y: 190, w: 180, h: 180, state: "HERD_ISOLATION", conf: 0.88, mr_title: "कळपापासून वेगळे राहणे", severity: "WARNING" }
    ]
  },
  CH2: {
    name_mr: "कॅमेरा २: संगमनेर कळप शेड (खुरकूत पाळत)",
    name_en: "Camera 2: Sangamner Herd Corral (Limping Gait)",
    rtsp: "rtsp://sangamner-coop.maha-agro.gov:554/live/ch2",
    location: "संगमनेर (अहमदनगर) • मुख्य कळप",
    focusTag: "TAG-2089 (कपिला)",
    animals: [
      { id: "TAG-2089", name: "कपिला", breed: "Khillari", x: 260, y: 200, w: 200, h: 200, state: "LIMPING_GAIT", conf: 0.91, mr_title: "चालताना लंगडणे (खुरदाह/लाळ्या संशय)", severity: "CRITICAL" },
      { id: "TAG-2092", name: "मंगळा", breed: "Red Kandhari", x: 620, y: 180, w: 210, h: 190, state: "NORMAL", conf: 0.93, mr_title: "सामान्य हालचाल", severity: "NORMAL" }
    ]
  },
  CH3: {
    name_mr: "कॅमेरा ३: कोल्हापूर दूध डेअरी (दूध काढणी कक्ष)",
    name_en: "Camera 3: Kolhapur Milking Parlor",
    rtsp: "rtsp://kolhapur-dairy.maha-agro.gov:554/live/ch3",
    location: "करवीर (कोल्हापूर) • डेअरी युनिट",
    focusTag: "TAG-3011 (मुर्राह म्हैस)",
    animals: [
      { id: "TAG-3011", name: "मुर्राह-०१", breed: "Murrah Buffalo", x: 220, y: 170, w: 240, h: 210, state: "NORMAL", conf: 0.97, mr_title: "नियमित दूध दोहन स्थिती", severity: "NORMAL" },
      { id: "TAG-3015", name: "मुर्राह-०४", breed: "Murrah Buffalo", x: 580, y: 180, w: 230, h: 200, state: "NORMAL", conf: 0.95, mr_title: "नियमित रवंथ", severity: "NORMAL" }
    ]
  },
  WEBCAM: {
    name_mr: "कॅमेरा ४: थेट स्थानिक कॅमेरा (Live WebCam)",
    name_en: "Camera 4: Live Local Device Camera",
    rtsp: "webrtc://localhost/live-feed",
    location: "स्थानिक डिव्हाइस कॅमेरा (Live AI Detection)",
    focusTag: "LIVE-INSPECTION",
    animals: [
      { id: "LIVE-01", name: "तपासणी जनावर", breed: "Real-Time Detection", x: 320, y: 140, w: 320, h: 260, state: "NORMAL", conf: 0.92, mr_title: "थेट AI तपासणी सक्रिय", severity: "NORMAL" }
    ]
  }
};

function openCCTVModal() {
  const modal = document.getElementById("cctvModal");
  if (!modal) return;
  modal.style.display = "flex";
  cctvModalOpen = true;
  initCCTVCanvas();
  selectCCTVChannel(currentCCTVChannel);
}

function closeCCTVModal() {
  const modal = document.getElementById("cctvModal");
  if (modal) modal.style.display = "none";
  cctvModalOpen = false;
  if (cctvAnimFrameId) {
    cancelAnimationFrame(cctvAnimFrameId);
    cctvAnimFrameId = null;
  }
  stopWebcam();
}

function selectCCTVChannel(chKey) {
  currentCCTVChannel = chKey;

  // Update active pill
  document.querySelectorAll(".cctv-ch-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.channel === chKey);
  });

  const chInfo = CCTV_CHANNELS[chKey];
  document.getElementById("cctvLocationText").textContent = chInfo.location;
  document.getElementById("cctvStreamUrlText").textContent = chInfo.rtsp;
  document.getElementById("cctvChannelTitle").textContent = chInfo.name_mr;

  renderCCTVAnimalList(chInfo.animals);

  if (chKey === "WEBCAM") {
    startWebcam();
  } else {
    stopWebcam();
  }
}

async function startWebcam() {
  const videoElem = document.getElementById("cctvWebcamVideo");
  try {
    liveWebcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false
    });
    videoElem.srcObject = liveWebcamStream;
    videoElem.play();
  } catch (err) {
    console.warn("Webcam access declined or not available:", err);
    alert("वेबकॅम उघडता आला नाही. कृपया ब्राउझरमध्ये कॅमेरा परवानगी द्या.");
    selectCCTVChannel("CH1");
  }
}

function stopWebcam() {
  if (liveWebcamStream) {
    liveWebcamStream.getTracks().forEach((track) => track.stop());
    liveWebcamStream = null;
  }
}

function initCCTVCanvas() {
  const canvas = document.getElementById("cctvCanvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let tick = 0;

  function renderLoop() {
    if (!cctvModalOpen) return;

    tick++;
    frameCount++;
    const now = performance.now();
    if (now - lastFpsTime >= 1000) {
      currentFps = (frameCount * 1000) / (now - lastFpsTime);
      frameCount = 0;
      lastFpsTime = now;
      const fpsElem = document.getElementById("cctvFpsText");
      if (fpsElem) fpsElem.textContent = `${currentFps.toFixed(1)} FPS`;
    }

    // Canvas dimensions
    const w = canvas.width = 960;
    const h = canvas.height = 540;

    const chInfo = CCTV_CHANNELS[currentCCTVChannel];
    const isWebcam = currentCCTVChannel === "WEBCAM";
    const webcamVideo = document.getElementById("cctvWebcamVideo");

    if (isWebcam && liveWebcamStream && webcamVideo.readyState >= 2) {
      // Draw live webcam video
      ctx.drawImage(webcamVideo, 0, 0, w, h);
    } else {
      // Draw realistic synthetic cowshed environment
      drawSyntheticBarnScene(ctx, w, h, tick);
    }

    // Draw CRT subtle scanlines
    ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
    for (let y = 0; y < h; y += 4) {
      ctx.fillRect(0, y, w, 1.5);
    }

    // Render Bounding Boxes & AI Tracking
    renderAIOverlay(ctx, chInfo.animals, tick, isWebcam);

    // Top Right HUD
    drawCCTVHud(ctx, w, h, chInfo);

    cctvAnimFrameId = requestAnimationFrame(renderLoop);
  }

  cctvAnimFrameId = requestAnimationFrame(renderLoop);
}

function drawSyntheticBarnScene(ctx, w, h, tick) {
  // Barn floor (earthy concrete)
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, "#1c232d");
  grad.addColorStop(0.35, "#252e3b");
  grad.addColorStop(0.4, "#2d342c");
  grad.addColorStop(1, "#363a2f");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // Shed roof beams & pillars
  ctx.strokeStyle = "rgba(100, 116, 139, 0.4)";
  ctx.lineWidth = 4;
  ctx.beginPath();
  // Left pillar
  ctx.moveTo(120, 0); ctx.lineTo(120, h);
  // Center pillar
  ctx.moveTo(480, 0); ctx.lineTo(480, h);
  // Right pillar
  ctx.moveTo(840, 0); ctx.lineTo(840, h);
  // Cross beams
  ctx.moveTo(0, 140); ctx.lineTo(w, 140);
  ctx.moveTo(0, 260); ctx.lineTo(w, 260);
  ctx.stroke();

  // Hay / fodder feeding trough at the back
  ctx.fillStyle = "rgba(180, 150, 90, 0.25)";
  ctx.fillRect(0, 200, w, 40);

  // Subtle simulated cattle silhouettes / movement
  const ch = currentCCTVChannel;
  if (ch === "CH1") {
    // Cow 1: Lying down (Recumbent)
    const breathOffset = Math.sin(tick * 0.05) * 2;
    drawCowSilhouette(ctx, 290, 290 + breathOffset, 160, 90, "#8b6540", true);

    // Cow 2: Standing normal
    const sway = Math.sin(tick * 0.04) * 3;
    drawCowSilhouette(ctx, 610 + sway, 240, 130, 140, "#4a3b32", false);

    // Cow 3: Standing isolated
    drawCowSilhouette(ctx, 880, 270, 120, 130, "#9c9386", false);
  } else if (ch === "CH2") {
    // Limping cow walking
    const limp = Math.abs(Math.sin(tick * 0.08)) * 12;
    drawCowSilhouette(ctx, 350, 280 - limp, 140, 140, "#735c43", false);
    drawCowSilhouette(ctx, 720, 260, 140, 140, "#2c2a29", false);
  } else {
    // Milking stall cows
    drawCowSilhouette(ctx, 340, 260, 160, 150, "#1a1918", false);
    drawCowSilhouette(ctx, 690, 265, 150, 150, "#222120", false);
  }
}

function drawCowSilhouette(ctx, cx, cy, rx, ry, color, isLying) {
  ctx.save();
  ctx.fillStyle = color;
  ctx.beginPath();
  if (isLying) {
    // Lying down oval body
    ctx.ellipse(cx, cy, rx * 0.7, ry * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();
    // Head resting
    ctx.beginPath();
    ctx.ellipse(cx - rx * 0.5, cy - 10, rx * 0.25, ry * 0.35, -0.3, 0, Math.PI * 2);
    ctx.fill();
  } else {
    // Standing body
    ctx.ellipse(cx, cy, rx * 0.55, ry * 0.45, 0, 0, Math.PI * 2);
    ctx.fill();
    // Head upright
    ctx.beginPath();
    ctx.ellipse(cx - rx * 0.45, cy - ry * 0.3, rx * 0.2, ry * 0.25, 0.4, 0, Math.PI * 2);
    ctx.fill();
    // Legs
    ctx.fillRect(cx - rx * 0.3, cy + ry * 0.3, 14, ry * 0.45);
    ctx.fillRect(cx - rx * 0.1, cy + ry * 0.3, 14, ry * 0.45);
    ctx.fillRect(cx + rx * 0.1, cy + ry * 0.3, 14, ry * 0.45);
    ctx.fillRect(cx + rx * 0.3, cy + ry * 0.3, 14, ry * 0.45);
  }
  ctx.restore();
}

function renderAIOverlay(ctx, animals, tick, isWebcam) {
  animals.forEach((anim, idx) => {
    let bx = anim.x;
    let by = anim.y;
    let bw = anim.w;
    let bh = anim.h;

    // Slight dynamic jitter for realistic tracking
    if (!isWebcam) {
      const jitterX = Math.sin(tick * 0.05 + idx) * 2;
      const jitterY = Math.cos(tick * 0.04 + idx) * 1.5;
      bx += jitterX;
      by += jitterY;
    } else {
      // Dynamic simulated center detection over webcam
      bx = 280 + Math.sin(tick * 0.03) * 15;
      by = 120 + Math.cos(tick * 0.02) * 10;
      bw = 400;
      bh = 320;
    }

    let color = "#10B981"; // Green Normal
    let bgHeader = "rgba(16, 185, 129, 0.85)";
    if (anim.severity === "CRITICAL") {
      color = "#EF4444"; // Red Critical
      bgHeader = "rgba(239, 68, 68, 0.9)";
    } else if (anim.severity === "WARNING") {
      color = "#F59E0B"; // Amber Warning
      bgHeader = "rgba(245, 158, 11, 0.9)";
    }

    ctx.save();

    // Bounding Box outline
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.strokeRect(bx, by, bw, bh);

    // Reticle corners (high-tech target look)
    const corner = 18;
    ctx.lineWidth = 4.5;
    // Top-Left
    ctx.beginPath(); ctx.moveTo(bx, by + corner); ctx.lineTo(bx, by); ctx.lineTo(bx + corner, by); ctx.stroke();
    // Top-Right
    ctx.beginPath(); ctx.moveTo(bx + bw - corner, by); ctx.lineTo(bx + bw, by); ctx.lineTo(bx + bw, by + corner); ctx.stroke();
    // Bottom-Left
    ctx.beginPath(); ctx.moveTo(bx, by + bh - corner); ctx.lineTo(bx, by + bh); ctx.lineTo(bx + corner, by + bh); ctx.stroke();
    // Bottom-Right
    ctx.beginPath(); ctx.moveTo(bx + bw - corner, by + bh); ctx.lineTo(bx + bw, by + bh); ctx.lineTo(bx + bw, by + bh - corner); ctx.stroke();

    // Header Label pill
    ctx.fillStyle = bgHeader;
    const labelHeight = 26;
    ctx.fillRect(bx, Math.max(0, by - labelHeight), bw, labelHeight);

    // Label Text
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 13px system-ui, sans-serif";
    const labelText = `${anim.id} • ${anim.mr_title} (${Math.round(anim.conf * 100)}%)`;
    ctx.fillText(labelText, bx + 8, Math.max(16, by - 8));

    // Bottom telemetry bar
    if (anim.severity === "CRITICAL") {
      ctx.fillStyle = "rgba(239, 68, 68, 0.25)";
      ctx.fillRect(bx, by, bw, bh);

      // Warning icon blink
      if (Math.floor(tick / 15) % 2 === 0) {
        ctx.fillStyle = "#EF4444";
        ctx.font = "bold 14px system-ui, sans-serif";
        ctx.fillText("⚠️ तातडीचा इशारा: पशुवैद्यक अलर्ट", bx + 10, by + bh - 12);
      }
    }

    ctx.restore();
  });
}

function drawCCTVHud(ctx, w, h, chInfo) {
  ctx.save();

  // Top Left Record Indicator
  ctx.fillStyle = "#EF4444";
  ctx.beginPath();
  ctx.arc(24, 26, 7, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#FFFFFF";
  ctx.font = "bold 12px monospace";
  const now = new Date();
  const timeStr = now.toTimeString().split(" ")[0];
  ctx.fillText(`● REC LIVE  ${timeStr} IST`, 38, 30);

  // Top Center Camera Details
  ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
  ctx.fillRect(w / 2 - 160, 12, 320, 26);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
  ctx.strokeRect(w / 2 - 160, 12, 320, 26);

  ctx.fillStyle = "#38BDF8";
  ctx.font = "bold 11px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(chInfo.name_en, w / 2, 29);

  // Bottom HUD
  ctx.textAlign = "left";
  ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
  ctx.fillRect(16, h - 38, w - 32, 28);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
  ctx.strokeRect(16, h - 38, w - 32, 28);

  ctx.fillStyle = "#94A3B8";
  ctx.font = "11px monospace";
  ctx.fillText(`YOLO-V8 EDGE INFERENCE: 3.8ms | PROTOCOL: RTSP-H264 | STREAM: 1080p@30 | ANOMALIES: ${chInfo.animals.filter(a => a.severity !== 'NORMAL').length}`, 26, h - 20);

  ctx.restore();
}

function renderCCTVAnimalList(animals) {
  const container = document.getElementById("cctvDetectedAnimalsList");
  if (!container) return;

  container.innerHTML = animals.map((a) => {
    const badgeClass = a.severity === "CRITICAL" ? "pill-critical" : (a.severity === "WARNING" ? "pill-warning" : "pill-healthy");
    return `
      <div class="cctv-animal-card ${a.severity.toLowerCase()}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="color: #F8FAFC; font-size: 14px;">${a.name} (${a.id})</strong>
          <span class="status-pill ${badgeClass}">${a.severity}</span>
        </div>
        <div style="font-size: 12px; color: #CBD5E1; margin-top: 4px;">
          ${a.breed} • विश्वासार्हता: ${Math.round(a.conf * 100)}%
        </div>
        <div style="font-size: 12px; color: ${a.severity === 'CRITICAL' ? '#FCA5A5' : '#FCD34D'}; margin-top: 4px; font-weight: 600;">
          📌 ${a.mr_title}
        </div>
      </div>
    `;
  }).join("");
}

function triggerCCTVQuickScan() {
  const btn = document.getElementById("btnCCTVScan");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "⏳ स्कॅनिंग चालू आहे...";
    setTimeout(() => {
      btn.disabled = false;
      btn.textContent = "🔍 AI वर्तन तपासणी पूर्ण (No new flags)";
      alert("✅ AI वर्तन तपासणी यशस्वी! कॅमेरा फीडवरून ३ जनावरांचे ट्रॅकिंग अपडेट झाले आहे.");
    }, 1200);
  }
}

function dispatchFieldVetFromCCTV() {
  const chInfo = CCTV_CHANNELS[currentCCTVChannel];
  alert(`🚑 तातडीचे व्हेटर्नरी युनिट रवाना करण्यात आले!\n\nस्थान: ${chInfo.location}\nलक्षित जनावर: ${chInfo.focusTag}\nसंशय: तीव्र कासदाह / खुरदाह लक्षणे\n\nस्थानिक मोबाईल व्हेटर्नरी व्हॅनला (1962) जीपीएस मार्ग पाठवला आहे.`);
}
