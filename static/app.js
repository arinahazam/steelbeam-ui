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
let selectedFiles = [];

/* ---------- Start Camera ---------- */
async function startCamera() {
    console.log("startCamera called");

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
        const file = new File([blob], `photo_${Date.now()}.jpg`, {
            type: "image/jpeg"
        });
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
        const file = new File([blob], `video_${Date.now()}.webm`, {
            type: "video/webm"
        });
        selectedFiles.push(file);
        renderPreviews();
    };

    mediaRecorder.start();
    alert("Recording started");
}

function stopVideoRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        alert("Recording stopped");
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
        remove.innerText = "✕";
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

/* ---------- Submit Files ---------- */
function submitSelectedFiles() {
    if (selectedFiles.length === 0) {
        alert("Please select at least one file.");
        return;
    }

    const dt = new DataTransfer();
    selectedFiles.forEach(f => dt.items.add(f));

    document.getElementById("hiddenFileInput").files = dt.files;
    document.getElementById("uploadForm").submit();
}
function goDashboard() {
    window.location.href = "/dashboard";
}
