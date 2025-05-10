document.addEventListener("DOMContentLoaded", () => {
  const emailField    = document.getElementById("email");
  const summaryEl     = document.getElementById("summary");
  const actionsEl     = document.getElementById("actions");
  const replyArea     = document.getElementById("reply");
  const confidenceEl  = document.getElementById("confidence");

  const analyzeBtn    = document.getElementById("analyzeBtn");
  const copyBtn       = document.getElementById("copyBtn");
  const editBtn       = document.getElementById("editBtn");
  const clearAllBtn   = document.getElementById("clearAllBtn");

  const feedbackInput = document.getElementById("feedback");
  const feedbackBtn   = document.getElementById("feedbackBtn");

  const SUMMARY_PH    = "Здесь появится краткое резюме письма после обработки.";
  const TASKS_PH      = "Здесь появятся задачи после анализа письма.";
  const REPLY_PH      = "Здесь появится предполагаемый ответ после обработки.";

  analyzeBtn.addEventListener("click", async () => {
    const text = emailField.value.trim();
    if (!text) return;

    analyzeBtn.textContent = "Обработка…";
    analyzeBtn.disabled = true;

    try {
      const res  = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();

      summaryEl.textContent = data.summary || "—";
      summaryEl.classList.remove("placeholder");

      actionsEl.innerHTML = data.tasks?.length
        ? `<ul>${data.tasks.map(t => `<li>${t}</li>`).join("")}</ul>`
        : "—";
      actionsEl.classList.remove("placeholder");

      replyArea.value = data.reply || "";
      replyArea.readOnly = true;
      replyArea.classList.remove("placeholder");

      confidenceEl.hidden = false;
      confidenceEl.innerHTML = "Уверенность модели: <strong>высокая</strong>";
    } catch (e) {
      alert("Ошибка сервера");
    } finally {
      analyzeBtn.textContent = "Проанализировать";
      analyzeBtn.disabled = false;
    }
  });

  copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(replyArea.value)
      .then(() => alert("Ответ скопирован в буфер обмена"))
      .catch(() => alert("Не удалось скопировать"));
  });

  editBtn.addEventListener("click", () => {
    replyArea.readOnly = false;
    replyArea.focus();
  });

  clearAllBtn.addEventListener("click", () => {
    emailField.value = "";

    summaryEl.textContent = SUMMARY_PH;
    summaryEl.classList.add("placeholder");

    actionsEl.textContent = TASKS_PH;
    actionsEl.classList.add("placeholder");

    replyArea.value = REPLY_PH;
    replyArea.readOnly = true;
    replyArea.classList.add("placeholder");

    confidenceEl.hidden = true;
    feedbackInput.value  = "";
  });

  feedbackBtn.addEventListener("click", async () => {
    const msg = feedbackInput.value.trim();
    if (!msg) return;
    await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    feedbackInput.value = "";
    alert("Спасибо за отзыв!");
  });
});
