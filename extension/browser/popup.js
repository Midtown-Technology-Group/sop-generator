const statusEl = document.getElementById("status");
const messageEl = document.getElementById("message");
const titleEl = document.getElementById("title");
const buttons = {
  start: document.getElementById("start"),
  pause: document.getElementById("pause"),
  resume: document.getElementById("resume"),
  stop: document.getElementById("stop"),
};

function setMessage(message, isError) {
  messageEl.textContent = message || "";
  messageEl.className = isError ? "error" : "";
}

function renderState(state) {
  if (!state || !state.recording) {
    statusEl.textContent = "Idle";
    buttons.start.disabled = false;
    buttons.pause.disabled = true;
    buttons.resume.disabled = true;
    buttons.stop.disabled = true;
    return;
  }

  statusEl.textContent = state.paused ? "Paused" : "Recording";
  buttons.start.disabled = true;
  buttons.pause.disabled = state.paused;
  buttons.resume.disabled = !state.paused;
  buttons.stop.disabled = false;
}

async function send(type, extra) {
  setMessage("");
  const response = await chrome.runtime.sendMessage({ type, ...extra });
  if (!response || response.ok === false) {
    throw new Error((response && response.error) || "No response from background worker");
  }
  renderState(response.state);
}

buttons.start.addEventListener("click", async () => {
  try {
    await send("start", { title: titleEl.value.trim() || "Browser capture" });
  } catch (error) {
    setMessage(error.message, true);
  }
});

buttons.pause.addEventListener("click", async () => {
  try {
    await send("pause");
  } catch (error) {
    setMessage(error.message, true);
  }
});

buttons.resume.addEventListener("click", async () => {
  try {
    await send("resume");
  } catch (error) {
    setMessage(error.message, true);
  }
});

buttons.stop.addEventListener("click", async () => {
  try {
    await send("stop");
  } catch (error) {
    setMessage(error.message, true);
  }
});

send("get-state").catch((error) => {
  renderState(null);
  setMessage(error.message, true);
});
