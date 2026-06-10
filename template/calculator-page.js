/* =========================================================================
   Trueline — Calculator Page interactions
   - FAQ accordion
   - Number-of-hires stepper
   - "Get My Custom Estimate" => clickbait, opens a popup (Popup Maker) later
   - "Ready to Hire?" native form => HubSpot Forms API submit
   IIFE + scoped to .tl-calc so it can be dropped into any page safely.
   ========================================================================= */
(function () {
  "use strict";

  /* -----------------------------------------------------------------
     CONFIG — fill these in (see SETUP.md).
     Find your IDs in HubSpot: Settings > Account Setup > Account Defaults
     (Hub/Portal ID) and the embed code of the form (Form GUID).
  ----------------------------------------------------------------- */
  var HUBSPOT = {
    portalId: "__HUBSPOT_PORTAL_ID__",
    formGuid: "__HUBSPOT_FORM_GUID__",
    region: "na1" // "na1" (US) or "eu1"
  };

  // Popup Maker popup ID that the clickbait calculator should open.
  // Set this to the numeric ID of the popup you create in Popup Maker.
  var QUOTE_POPUP_ID = "__POPUP_ID__";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var roots = document.querySelectorAll(".tl-calc");
    roots.forEach(function (root) {
      initAccordion(root);
      initStepper(root);
      initQuotePopups(root);
      initHubspotForm(root);
    });
  });

  /* ---- FAQ accordion -------------------------------------------------- */
  function initAccordion(root) {
    root.querySelectorAll(".tl-acc").forEach(function (acc) {
      var btn = acc.querySelector(".tl-acc__q");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var open = acc.classList.contains("is-open");
        // close siblings for a clean single-open accordion
        root.querySelectorAll(".tl-acc.is-open").forEach(function (o) {
          if (o !== acc) o.classList.remove("is-open");
        });
        acc.classList.toggle("is-open", !open);
        btn.setAttribute("aria-expanded", String(!open));
      });
    });
  }

  /* ---- Number-of-hires stepper --------------------------------------- */
  function initStepper(root) {
    root.querySelectorAll(".tl-stepper").forEach(function (s) {
      var input = s.querySelector("input");
      var dec = s.querySelector("[data-step='-']");
      var inc = s.querySelector("[data-step='+']");
      var min = parseInt(input.getAttribute("min") || "1", 10);
      function set(v) { input.value = Math.max(min, v); }
      if (dec) dec.addEventListener("click", function () { set(parseInt(input.value || min, 10) - 1); });
      if (inc) inc.addEventListener("click", function () { set(parseInt(input.value || min, 10) + 1); });
    });
  }

  /* ---- Clickbait calculator => open popup ---------------------------- */
  // The calculator inputs are intentionally not used for a live estimate.
  // Any element with [data-open-quote] opens the quote popup instead.
  function initQuotePopups(root) {
    root.querySelectorAll("[data-open-quote]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        openQuotePopup();
      });
    });
  }

  function openQuotePopup() {
    // Popup Maker: PUM.open(id). Falls back gracefully until QUOTE_POPUP_ID is set.
    if (window.PUM && QUOTE_POPUP_ID && QUOTE_POPUP_ID.indexOf("__") === -1) {
      window.PUM.open(QUOTE_POPUP_ID);
      return;
    }
    // Fallback before the popup is wired: scroll to the Ready-to-Hire form.
    var hire = document.querySelector(".tl-hire");
    if (hire) hire.scrollIntoView({ behavior: "smooth" });
  }

  /* ---- Ready to Hire => HubSpot Forms API ---------------------------- */
  function initHubspotForm(root) {
    var form = root.querySelector(".tl-hire__form");
    if (!form) return;
    var msg = root.querySelector(".tl-hire__msg");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (HUBSPOT.portalId.indexOf("__") !== -1 || HUBSPOT.formGuid.indexOf("__") !== -1) {
        showMsg(msg, "Form not configured yet — add your HubSpot portal & form IDs.", false);
        return;
      }

      var btn = form.querySelector("button[type='submit']");
      var orig = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }

      var fields = [];
      form.querySelectorAll("[name]").forEach(function (el) {
        if (el.value) fields.push({ name: el.getAttribute("name"), value: el.value });
      });

      var payload = {
        fields: fields,
        context: {
          pageUri: window.location.href,
          pageName: document.title
        }
      };

      var url = "https://api.hsforms.com/submissions/v3/integration/submit/" +
        HUBSPOT.portalId + "/" + HUBSPOT.formGuid;

      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (r) { return r.json().then(function (b) { return { ok: r.ok, body: b }; }); })
        .then(function (res) {
          if (res.ok) {
            form.reset();
            showMsg(msg, "Thanks! A Trueline recruiter will reply within 1 business day.", true);
          } else {
            var detail = res.body && res.body.message ? res.body.message : "Please try again.";
            showMsg(msg, "Something went wrong: " + detail, false);
          }
        })
        .catch(function () { showMsg(msg, "Network error — please try again.", false); })
        .finally(function () { if (btn) { btn.disabled = false; btn.textContent = orig; } });
    });
  }

  function showMsg(msg, text, ok) {
    if (!msg) return;
    msg.textContent = text;
    msg.classList.remove("is-ok", "is-err");
    msg.classList.add(ok ? "is-ok" : "is-err");
  }
})();
