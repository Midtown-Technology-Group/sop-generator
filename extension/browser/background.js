const API_BASE = "http://127.0.0.1:8765";
const DEFAULT_STATE = {
  sessionId: null,
  recording: false,
  paused: false,
};

function storageGet(keys) {
  return chrome.storage.local.get(keys);
}

function storageSet(values) {
  return chrome.storage.local.set(values);
}

async function getState() {
  const stored = await storageGet(DEFAULT_STATE);
  return {
    sessionId: stored.sessionId || null,
    recording: Boolean(stored.recording),
    paused: Boolean(stored.paused),
  };
}

async function saveState(state) {
  await storageSet(state);
  return getState();
}

function eventPayload(event) {
  return {
    type: event.type,
    timestamp: new Date().toISOString(),
    url: event.url || null,
    title: event.title || null,
    label: event.label || null,
    selector: event.selector || null,
    value_hint: event.value_hint || null,
    screenshot_path: event.screenshot_path || null,
    note: event.note || null,
  };
}

async function appendEvent(event) {
  const state = await getState();
  if (!state.recording || state.paused || !state.sessionId) {
    return { ok: false, skipped: true };
  }

  const response = await fetch(`${API_BASE}/api/sessions/${state.sessionId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(eventPayload(event)),
  });

  if (!response.ok) {
    throw new Error(`Event append failed: ${response.status}`);
  }
  return { ok: true };
}

async function startSession(title) {
  const response = await fetch(`${API_BASE}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title || "Browser capture" }),
  });

  if (!response.ok) {
    throw new Error(`Session create failed: ${response.status}`);
  }

  const session = await response.json();
  return saveState({
    sessionId: session.id,
    recording: true,
    paused: false,
  });
}

async function pauseSession() {
  await appendEvent({ type: "pause", note: "Recording paused" }).catch(() => null);
  return saveState({ paused: true });
}

async function resumeSession() {
  const state = await saveState({ paused: false });
  await appendEvent({ type: "resume", note: "Recording resumed" }).catch(() => null);
  return state;
}

async function stopSession() {
  await appendEvent({ type: "stop", note: "Recording stopped" }).catch(() => null);
  return saveState({
    sessionId: null,
    recording: false,
    paused: false,
  });
}

async function handleMessage(message) {
  if (!message || !message.type) {
    return { ok: false, error: "Missing message type" };
  }

  if (message.type === "get-state") {
    return { ok: true, state: await getState() };
  }
  if (message.type === "start") {
    return { ok: true, state: await startSession(message.title) };
  }
  if (message.type === "pause") {
    return { ok: true, state: await pauseSession() };
  }
  if (message.type === "resume") {
    return { ok: true, state: await resumeSession() };
  }
  if (message.type === "stop") {
    return { ok: true, state: await stopSession() };
  }
  if (message.type === "capture-event") {
    return await appendEvent(message.event || {});
  }

  return { ok: false, error: `Unknown message type: ${message.type}` };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  handleMessage(message)
    .then(sendResponse)
    .catch((error) => sendResponse({ ok: false, error: error.message }));
  return true;
});

chrome.tabs.onUpdated.addListener((_tabId, changeInfo, tab) => {
  if (changeInfo.status !== "complete" || !tab.url) {
    return;
  }

  appendEvent({
    type: "navigation",
    url: tab.url,
    title: tab.title || null,
    label: tab.title || tab.url,
  }).catch(() => null);
});
