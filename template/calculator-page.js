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
      initQuoteModal(root);
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

  /* ---- Quote popup (self-contained modal) ---------------------------- */
  // The calculator inputs are intentionally not used for a live estimate.
  // Any element with [data-open-quote] opens the centered modal form.
  function initQuotePopups(root) {
    root.querySelectorAll("[data-open-quote]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        openQuoteModal(root);
      });
    });
  }

  function getModal(root) {
    return root.querySelector("#tl-quote-modal") || document.getElementById("tl-quote-modal");
  }

  function openQuoteModal(root) {
    var modal = getModal(root);
    if (!modal) {
      // Fallback if the modal markup is missing: scroll to the hire form.
      var hire = root.querySelector(".tl-hire");
      if (hire) hire.scrollIntoView({ behavior: "smooth" });
      return;
    }
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("tl-modal-open");
    var first = modal.querySelector("input, textarea");
    if (first) setTimeout(function () { try { first.focus(); } catch (e) {} }, 60);
  }

  function closeQuoteModal(modal) {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("tl-modal-open");
  }

  // Close via ✕, backdrop click, or Esc. Effects fully reverse on close.
  function initQuoteModal(root) {
    var modal = getModal(root);
    if (!modal) return;
    modal.querySelectorAll("[data-close-quote]").forEach(function (el) {
      el.addEventListener("click", function () { closeQuoteModal(modal); });
    });
    document.addEventListener("keydown", function (e) {
      if ((e.key === "Escape" || e.keyCode === 27) && modal.classList.contains("is-open")) {
        closeQuoteModal(modal);
      }
    });
  }

  /* ---- Ready to Hire + modal => HubSpot Forms API -------------------- */
  // Binds every .tl-hire__form on the page (the section form AND the modal form).
  function initHubspotForm(root) {
    root.querySelectorAll(".tl-hire__form").forEach(function (form) {
      bindHubspotForm(form);
    });
  }

  function bindHubspotForm(form) {
    var msg = form.querySelector(".tl-hire__msg");

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
            var modal = form.closest ? form.closest(".tl-modal") : null;
            if (modal) setTimeout(function () { closeQuoteModal(modal); }, 1800);
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
