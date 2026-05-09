const MAX_LABEL_LENGTH = 120;

function compactText(value) {
  return (value || "").replace(/\s+/g, " ").trim().slice(0, MAX_LABEL_LENGTH);
}

function fieldLabel(element) {
  if (!element) {
    return "";
  }

  if (element.id) {
    const explicit = document.querySelector(`label[for="${CSS.escape(element.id)}"]`);
    if (explicit) {
      return compactText(explicit.innerText);
    }
  }

  const wrapped = element.closest("label");
  if (wrapped) {
    return compactText(wrapped.innerText);
  }

  return compactText(
    element.getAttribute("aria-label") ||
      element.getAttribute("placeholder") ||
      element.name ||
      element.id ||
      element.type ||
      element.tagName
  );
}

function visibleLabel(element) {
  if (!element) {
    return "";
  }

  return compactText(
    element.innerText ||
      element.getAttribute("aria-label") ||
      element.getAttribute("title") ||
      element.getAttribute("alt") ||
      fieldLabel(element) ||
      element.tagName
  );
}

function formLabel(form) {
  if (!form) {
    return "";
  }

  const heading = form.querySelector("h1, h2, h3, legend");
  return compactText(
    form.getAttribute("aria-label") ||
      (heading && heading.innerText) ||
      form.name ||
      form.id ||
      "form"
  );
}

function selectorFor(element) {
  if (!element || !element.tagName) {
    return null;
  }

  const parts = [element.tagName.toLowerCase()];
  if (element.id) {
    parts.push(`#${element.id}`);
  }
  if (element.name) {
    parts.push(`[name="${element.name}"]`);
  }
  return parts.join("");
}

function sendCaptureEvent(event) {
  chrome.runtime.sendMessage({
    type: "capture-event",
    event: {
      ...event,
      url: window.location.href,
      title: document.title,
    },
  });
}

document.addEventListener(
  "click",
  (event) => {
    const target = event.target.closest("button, a, input, select, textarea, [role='button']");
    if (!target) {
      return;
    }

    sendCaptureEvent({
      type: "click",
      label: visibleLabel(target),
      selector: selectorFor(target),
    });
  },
  true
);

document.addEventListener(
  "submit",
  (event) => {
    sendCaptureEvent({
      type: "submit",
      label: formLabel(event.target),
      selector: selectorFor(event.target),
    });
  },
  true
);

document.addEventListener(
  "change",
  (event) => {
    const target = event.target.closest("input, select, textarea");
    if (!target) {
      return;
    }

    sendCaptureEvent({
      type: "form_change",
      label: fieldLabel(target),
      selector: selectorFor(target),
      value_hint: "changed",
    });
  },
  true
);
