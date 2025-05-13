const form = document.getElementById("form");
const urlInput = document.getElementById("url");
const getInfoBtn = document.getElementById("getinfo");
const formatSelect = document.getElementById("format_id");
const outFormat = document.getElementById("out_format");
const formatContainer = document.getElementById("format_container");
const bar = document.getElementById("bar");
const statusText = document.getElementById("status-text");
const downloadBtn = document.getElementById("download-btn");

getInfoBtn.addEventListener("click", () => {
  const url = urlInput.value.trim();
  if (!url) return alert("Masukkan URL YouTube terlebih dahulu!");

  formatSelect.innerHTML = '<option>Loading...</option>';

  fetch("/fetch_info", {
    method: "POST",
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: new URLSearchParams({url: url})
  })
  .then(res => res.json())
  .then(data => {
    formatSelect.innerHTML = '';
    if (data.error) {
      alert("Gagal ambil data video: " + data.error);
      return;
    }
    data.formats.forEach(f => {
      const opt = document.createElement("option");
      opt.value = f.format_id;
      opt.innerText = f.label;
      formatSelect.appendChild(opt);
    });
  });
});

outFormat.addEventListener("change", () => {
  formatContainer.style.display = outFormat.value === "mp3" ? "none" : "block";
});

form.addEventListener("submit", function (e) {
  e.preventDefault();
  bar.style.width = "0%";
  bar.innerText = "0%";
  statusText.innerText = "Mengantri...";
  downloadBtn.classList.add("d-none");

  const formData = new FormData(form);

  fetch("/download", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    const taskId = data.task_id;
    const interval = setInterval(() => {
      fetch(`/status/${taskId}`)
        .then(res => res.json())
        .then(status => {
          bar.style.width = `${status.progress}%`;
          bar.innerText = `${status.progress}%`;
          statusText.innerText = status.status;

          if (status.ready) {
            clearInterval(interval);
            downloadBtn.href = `/file/${status.filename}`;
            downloadBtn.classList.remove("d-none");
          }

          if (status.progress >= 100 && !status.ready) {
            clearInterval(interval);
            bar.classList.remove("progress-bar-animated");
            bar.classList.add("bg-danger");
          }
        });
    }, 1000);
  });
});

window.addEventListener("DOMContentLoaded", () => {
  if (outFormat.value === "mp3") {
    formatContainer.style.display = "none";
  }
});
