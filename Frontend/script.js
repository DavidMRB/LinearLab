const API_URL = window.APP_CONFIG?.API_URL || "http://127.0.0.1:8000";

const welcomeScreen = document.getElementById("welcomeScreen");
const calculatorScreen = document.getElementById("calculatorScreen");
const workArea = document.getElementById("workArea");
const currentMethod = document.getElementById("currentMethod");
const currentMethodText = document.getElementById("currentMethodText");
const currentMethodIcon = document.getElementById("currentMethodIcon");
const methodMenu = document.getElementById("methodMenu");
const calcTitle = document.getElementById("calcTitle");
const solutionTitle = document.getElementById("solutionTitle");
const solutionPanel = document.getElementById("solutionPanel");
const calculator = document.getElementById("calculator");
const solveBtn = document.getElementById("solveBtn");
const clearEntry = document.getElementById("clearEntry");
const resetBtn = document.getElementById("resetBtn");
const addConstraint = document.getElementById("addConstraint");
const constraintEditor = document.getElementById("constraintEditor");
const objectiveCoefficients = document.getElementById("objectiveCoefficients");
const variableCount = document.getElementById("variableCount");
const constraintCount = document.getElementById("constraintCount");
const constraintsPreview = document.getElementById("constraintsPreview");
const objectivePreview = document.getElementById("objectivePreview");
const stepsOutput = document.getElementById("stepsOutput");
const finalAnswer = document.getElementById("finalAnswer");
const finalDescription = document.getElementById("finalDescription");
const formError = document.getElementById("formError");
const toast = document.getElementById("toast");

let selectedMethod = "simplex";
let mode = "max";

const methodData = {
  simplex: { name: "Método Simplex", icon: "Σ", title: "Resolución mediante el Método Simplex" },
  simplexRevisado: { name: "Simplex Revisado", icon: "B⁻¹", title: "Resolución mediante Simplex Revisado" },
  dualidad: { name: "Método de Dualidad", icon: "⇄", title: "Resolución mediante Dualidad" }
};

function selectMethod(method, firstView = false) {
  selectedMethod = method;
  const data = methodData[method];
  currentMethodText.textContent = "Método";
  currentMethodIcon.textContent = data.icon;
  calcTitle.textContent = data.name;
  solutionTitle.textContent = data.title;
  document.querySelectorAll(".workspace-option").forEach(option => {
    option.classList.toggle("active", option.dataset.method === method);
  });
  if (firstView) {
    welcomeScreen.classList.add("hidden");
    calculatorScreen.classList.remove("hidden");
    renderConstraintEditor();
  }
  methodMenu.classList.remove("show");
}

document.querySelectorAll(".method-card").forEach(card => {
  card.addEventListener("click", () => selectMethod(card.dataset.method, true));
});

document.querySelectorAll(".workspace-option").forEach(option => {
  option.addEventListener("click", () => {
    if (option.dataset.method !== selectedMethod) {
      resetCalculator(false).then(() => selectMethod(option.dataset.method));
    } else {
      methodMenu.classList.remove("show");
    }
  });
});

currentMethod.addEventListener("click", event => {
  event.stopPropagation();
  methodMenu.classList.toggle("show");
});

document.addEventListener("click", event => {
  if (!event.target.closest(".method-selector-wrapper")) methodMenu.classList.remove("show");
});

document.querySelectorAll(".mode").forEach(button => {
  button.addEventListener("click", () => {
    mode = button.dataset.mode;
    document.querySelectorAll(".mode").forEach(item => {
      item.classList.remove("active", "bg-ice", "text-ink");
      item.classList.add("bg-mist", "text-[#597081]");
    });
    button.classList.remove("bg-mist", "text-[#597081]");
    button.classList.add("active", "bg-ice", "text-ink");
  });
});

function renderConstraintEditor() {
  const count = Number.parseInt(variableCount.value, 10);
  const restrictions = Number.parseInt(constraintCount.value, 10);
  if (!Number.isInteger(count) || count < 1 || count > 20 || !Number.isInteger(restrictions) || restrictions < 1 || restrictions > 20) return;

  constraintEditor.innerHTML = Array.from({ length: restrictions }, (_, index) => `
    <div class="constraint-form grid gap-2 rounded-2xl border border-ink/10 bg-mist/50 p-3 short:gap-1 short:p-2" data-index="${index}">
      <div class="text-[11px] font-extrabold text-[#597081]">Restricción ${index + 1}</div>
      <input class="constraint-coefficients w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm outline-none focus:border-steel focus:ring-4 focus:ring-steel/15 short:py-1.5" type="text" placeholder="Coeficientes: 1,2" aria-label="Coeficientes de la restricción ${index + 1}">
      <div class="grid grid-cols-[72px_1fr] gap-2">
        <select class="relation-input rounded-xl border border-ink/10 bg-[#F8FAFB] px-2 text-center font-extrabold outline-none focus:border-steel" aria-label="Relación de la restricción ${index + 1}">
          <option value="<=">≤</option>
          <option value=">=">≥</option>
          <option value="=">=</option>
        </select>
        <input class="rhs-input w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm outline-none focus:border-steel focus:ring-4 focus:ring-steel/15 short:py-1.5" type="text" placeholder="Término independiente" aria-label="Término independiente de la restricción ${index + 1}">
      </div>
    </div>
  `).join("");
}

variableCount.addEventListener("change", renderConstraintEditor);
constraintCount.addEventListener("change", renderConstraintEditor);
addConstraint.addEventListener("click", () => {
  renderConstraintEditor();
  showToast("Campos de restricciones actualizados");
});

function parseNumbers(value, expected, label) {
  const parts = value.split(",").map(item => item.trim());
  if (parts.length !== expected || parts.some(item => item === "" || !Number.isFinite(Number(item)))) {
    throw new Error(`${label} debe contener exactamente ${expected} números separados por comas.`);
  }
  return parts.map(Number);
}

function parseTerm(value, label) {
  const number = Number(value.trim());
  if (!value.trim() || !Number.isFinite(number)) throw new Error(`${label} debe ser un número válido.`);
  return number;
}

function collectModel() {
  const count = Number.parseInt(variableCount.value, 10);
  if (!Number.isInteger(count) || count < 1 || count > 20) throw new Error("La cantidad de variables debe estar entre 1 y 20.");
  const objective = parseNumbers(objectiveCoefficients.value, count, "La función objetivo");
  const forms = [...document.querySelectorAll(".constraint-form")];
  if (forms.length === 0) throw new Error("Debes agregar al menos una restricción.");
  const restricciones = forms.map((form, index) => ({
    coeficientes: parseNumbers(form.querySelector(".constraint-coefficients").value, count, `La restricción ${index + 1}`),
    relacion: form.querySelector(".relation-input").value,
    termino_independiente: parseTerm(form.querySelector(".rhs-input").value, `El término independiente de la restricción ${index + 1}`)
  }));
  return { tipo: mode, objetivo: objective, restricciones };
}

function formatNumber(value) {
  return Number(value).toFixed(4).replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1");
}

function formatModel(model) {
  objectivePreview.textContent = `${model.tipo.toUpperCase()} Z = ${model.objetivo.map((value, index) => `${formatNumber(value)}x${index + 1}`).join(" + ")}`;
  constraintsPreview.innerHTML = model.restricciones.map((restriction, index) => {
    const left = restriction.coeficientes.map((value, variable) => `${formatNumber(value)}x${variable + 1}`).join(" + ");
    return `<div class="constraint-result">R${index + 1}: ${left} ${restriction.relacion} ${formatNumber(restriction.termino_independiente)}</div>`;
  }).join("");
}

function renderSteps(result, title) {
  const values = result.valores_variables.map((value, index) => `${result.nombres_variables[index] || `x${index + 1}`} = ${formatNumber(value)}`).join(", ");
  return `
    <div class="mb-3 rounded-xl bg-mist px-4 py-3">
      <strong class="block text-base">${title}</strong>
      <span class="mt-1 block text-xs text-[#597081]">${result.mensaje}</span>
      ${values ? `<span class="mt-1 block font-mono text-xs">${values}</span>` : ""}
    </div>
    ${result.pasos.map(step => `
      <div class="mb-3 rounded-xl border-l-4 border-steel bg-[#F6F9FA] p-4 text-sm leading-6">
        <strong class="block">${step.fase} · Iteración ${step.iteracion}</strong>
        <span class="mt-1 block text-[#597081]">${step.entra ? `Entra ${step.entra}` : "Tabla inicial"}${step.sale ? ` · Sale ${step.sale}` : ""}</span>
        <div class="mt-3 overflow-x-auto"><table class="w-full border-collapse font-mono text-[11px]"><thead><tr>${step.encabezados.map(header => `<th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">${header}</th>`).join("")}</tr></thead><tbody>${step.tabla.map(row => `<tr>${row.map(cell => `<td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${formatNumber(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
      </div>
    `).join("")}
  `;
}

function renderSimplexResult(result) {
  const values = result.valores_variables.map((value, index) => `${result.nombres_variables[index] || `x${index + 1}`} = ${formatNumber(value)}`).join(", ");
  finalAnswer.textContent = result.valor_objetivo === null ? result.estado : `Z = ${formatNumber(result.valor_objetivo)}`;
  finalDescription.textContent = `${result.mensaje} ${values}`;
  stepsOutput.innerHTML = renderSteps(result, "Simplex");
}

function renderDualResult(result) {
  const primal = result.primal;
  const dual = result.dual;
  const primalValue = primal.valor_objetivo === null ? primal.estado : formatNumber(primal.valor_objetivo);
  const dualValue = dual.valor_objetivo === null ? dual.estado : formatNumber(dual.valor_objetivo);
  finalAnswer.textContent = `Primal: ${primalValue} · Dual: ${dualValue}`;
  finalDescription.textContent = result.valores_coinciden ? "Los valores óptimos coinciden." : "Revisa la factibilidad o la formulación de ambos problemas.";
  stepsOutput.innerHTML = renderSteps(primal, "Primal") + renderSteps(dual, "Dual construido");
}

async function solve() {
  formError.textContent = "";
  solveBtn.disabled = true;
  solveBtn.textContent = "Resolviendo...";
  try {
    const model = collectModel();
    formatModel(model);
    const endpoint = selectedMethod === "simplex" ? "/api/simplex/resolver" : selectedMethod === "simplexRevisado" ? "/api/simplex-revisado/resolver" : "/api/dualidad/resolver";
    const response = await fetch(`${API_URL}${endpoint}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(model) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 404 && selectedMethod === "simplexRevisado") {
        throw new Error("El backend desplegado aún no tiene disponible el método Simplex Revisado.");
      }
      throw new Error(data.detail?.[0]?.msg || `La API rechazó el modelo (${response.status}).`);
    }
    selectedMethod === "dualidad" ? renderDualResult(data) : renderSimplexResult(data);
    await setResultsVisible(true);
  } catch (error) {
    formError.textContent = error.message || "No se pudo resolver el modelo.";
  } finally {
    solveBtn.disabled = false;
    solveBtn.innerHTML = "Resolver <span>→</span>";
  }
}

solveBtn.addEventListener("click", solve);
async function setResultsVisible(visible) {
  const before = calculator.getBoundingClientRect();

  if (visible) {
    solutionPanel.classList.remove("hidden");
    solutionPanel.classList.remove("opacity-100");
    solutionPanel.classList.add("opacity-0");
    workArea.classList.add("lg:flex-row", "lg:items-start", "lg:justify-start", "show-results");
    calculator.classList.add("lg:max-w-[420px]");
  } else {
    solutionPanel.classList.add("hidden");
    solutionPanel.classList.remove("opacity-100");
    workArea.classList.remove("lg:flex-row", "lg:items-start", "lg:justify-start", "show-results");
    calculator.classList.remove("lg:max-w-[420px]");
  }

  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const after = calculator.getBoundingClientRect();
  const deltaX = before.left - after.left;
  const deltaY = before.top - after.top;
  if (Math.abs(deltaX) < 1 && Math.abs(deltaY) < 1) {
    solutionPanel.classList.remove("opacity-0");
    solutionPanel.classList.add("opacity-100");
    return;
  }

  calculator.animate(
    [
      { transform: `translate(${deltaX}px, ${deltaY}px)` },
      { transform: "translate(0, 0)" }
    ],
    { duration: 700, easing: "cubic-bezier(.22,.8,.25,1)" }
  );

  await new Promise(resolve => setTimeout(resolve, 680));
  solutionPanel.classList.remove("opacity-0");
  solutionPanel.classList.add("opacity-100");
}

clearEntry.addEventListener("click", () => {
  mode = "max";
  document.querySelectorAll(".mode").forEach(item => {
    item.classList.remove("active", "bg-ice", "text-ink");
    item.classList.add("bg-mist", "text-[#597081]");
  });
  document.querySelector('.mode[data-mode="max"]').classList.remove("bg-mist", "text-[#597081]");
  document.querySelector('.mode[data-mode="max"]').classList.add("active", "bg-ice", "text-ink");
  objectiveCoefficients.value = "";
  variableCount.value = "2";
  constraintCount.value = "2";
  renderConstraintEditor();
  setResultsVisible(false);
  formError.textContent = "";
});

async function resetCalculator(clearEverything = true) {
  await setResultsVisible(false);
  if (clearEverything) clearEntry.click();
}

resetBtn.addEventListener("click", () => resetCalculator(true));
renderConstraintEditor();

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2200);
}
