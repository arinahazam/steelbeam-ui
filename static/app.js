/* =========================
   Sidebar
========================= */
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.toggle("open");
}

/* =========================
   Camera & Upload Logic
========================= */
let cameraStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let selectedFiles = []; // This holds all our media (Photos, Videos, and Uploads)

/* ---------- Start Camera ---------- */
async function startCamera() {
    const modal = document.getElementById("cameraModal");
    const video = document.getElementById("cameraStream");
    modal.classList.remove("hidden");

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        video.srcObject = cameraStream;
    } catch (err) {
        alert("Camera access denied.");
        console.error(err);
    }
}

/* ---------- Capture Photo ---------- */
function capturePhoto() {
    const video = document.getElementById("cameraStream");
    if (!video.videoWidth) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    canvas.toBlob(blob => {
        const file = new File([blob], `photo_${Date.now()}.jpg`, { type: "image/jpeg" });
        selectedFiles.push(file);
        renderPreviews();
    }, "image/jpeg");
}

/* ---------- Video Recording ---------- */
function toggleVideoRecording() {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        startVideoRecording();
    } else {
        stopVideoRecording();
    }
}

function startVideoRecording() {
    if (!cameraStream) return;
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(cameraStream, { mimeType: "video/webm" });

    mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) recordedChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: "video/webm" });
        const file = new File([blob], `video_${Date.now()}.webm`, { type: "video/webm" });
        selectedFiles.push(file);
        renderPreviews();
    };

    mediaRecorder.start();
    console.log("Recording started");
}

function stopVideoRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        console.log("Recording stopped");
    }
}

/* ---------- Close Camera ---------- */
function closeCamera() {
    document.getElementById("cameraModal").classList.add("hidden");
    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
        cameraStream = null;
    }
}

/* =========================
   File Selection & Preview
========================= */
function handleMultipleFiles(input) {
    const files = Array.from(input.files || []);
    files.forEach(file => selectedFiles.push(file));
    renderPreviews();
}

function renderPreviews() {
    const gallery = document.getElementById("previewGallery");
    gallery.innerHTML = "";

    selectedFiles.forEach((file, idx) => {
        const item = document.createElement("div");
        item.className = "preview-item";

        const remove = document.createElement("div");
        remove.className = "preview-remove";
        remove.innerHTML = "&times;";
        remove.onclick = () => {
            selectedFiles.splice(idx, 1);
            renderPreviews();
        };
        item.appendChild(remove);

        const url = URL.createObjectURL(file);
        if (file.type.startsWith("image")) {
            const img = document.createElement("img");
            img.src = url;
            item.appendChild(img);
        } else {
            const vid = document.createElement("video");
            vid.src = url;
            vid.controls = true;
            item.appendChild(vid);
        }
        gallery.appendChild(item);
    });
}

/* ---------- Final Submit Files ---------- */
function submitSelectedFiles() {
    const uploadBtn = document.querySelector('.upload-btn');
    
    // 1. Check the JAVASCRIPT array, not the input element
    if (selectedFiles.length === 0) {
        alert("Please select or capture media first.");
        return;
    }

    // 2. Build the File List using DataTransfer
    const dt = new DataTransfer();
    selectedFiles.forEach(f => dt.items.add(f));

    // 3. Attach it to the hidden input
    const hiddenInput = document.getElementById("hiddenFileInput");
    hiddenInput.files = dt.files;

    // 4. Visual Loading State
    uploadBtn.classList.add('btn-disabled');
    uploadBtn.innerHTML = '<span class="spinner"></span> AI Analysis in Progress...';

    // 5. Submit
    document.getElementById("uploadForm").submit();
}

function goDashboard() {
    window.location.href = "/dashboard";
}