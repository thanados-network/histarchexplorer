document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Fetch the PresentationView data first
    const viewEntity = await fetchPresentationView(file_id);

    // Get the single video file
    const file_data = viewEntity.files[0];
    if (!file_data) throw new Error("No video file found in presentation view");

    // Update the video source dynamically
    const video = document.getElementById("mainVideo");
    video.src = file_data.url;

    // 4Toolbox buttons
    const btnPlay = document.getElementById("btn-play");
    const btnMute = document.getElementById("btn-mute");
    const btnSpeed = document.getElementById("btn-speed");
    const btnFullscreen = document.getElementById("btn-fullscreen");
    const btnDownload = document.getElementById("btn-download");

    // --- Play / Pause ---
    btnPlay.addEventListener("click", () => {
      if (video.paused) {
        video.play();
        btnPlay.innerHTML = '<i class="bi bi-pause-fill"></i>';
      } else {
        video.pause();
        btnPlay.innerHTML = '<i class="bi bi-play-fill"></i>';
      }
    });

    // --- Mute / Unmute ---
    btnMute.addEventListener("click", () => {
      video.muted = !video.muted;
      btnMute.innerHTML = video.muted
        ? '<i class="bi bi-volume-up-fill"></i>'
        : '<i class="bi bi-volume-mute-fill"></i>';
    });

    // --- Playback speed toggle ---
    const speeds = [1, 1.5, 2, 0.5];
    let currentSpeedIndex = 0;
    btnSpeed.addEventListener("click", () => {
      currentSpeedIndex = (currentSpeedIndex + 1) % speeds.length;
      video.playbackRate = speeds[currentSpeedIndex];
      btnSpeed.title = `Speed: ${video.playbackRate}x`;
      btnSpeed.innerHTML = `<i class="bi bi-speedometer"></i><small>${video.playbackRate}x</small>`;
    });

    // --- Fullscreen ---
    btnFullscreen.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        video.requestFullscreen().catch(console.error);
      } else {
        document.exitFullscreen();
      }
    });

    // --- Download video ---
    btnDownload.addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file_data.url + "?download=true";
      a.download = file_data.title || "video.mp4";
      a.click();
    });

    // Info button
    document.getElementById("btn-info").addEventListener("click", () => {
      createInfoOverlay(viewEntity, file_data);
    });


  } catch (err) {
    console.error("Video load error:", err);
    const container = document.querySelector(".video-viewer-wrapper");
    container.innerHTML = `<p class="text-danger">Failed to load video.</p>`;
  }
});
