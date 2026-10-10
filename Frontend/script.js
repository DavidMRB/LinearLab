import { renderLayout } from "./components/layout.js";
import { endpointFor, methodData } from "./modules/methods.js";

renderLayout();

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
const stepsTitle = document.getElementById("stepsTitle");
const graphicSection = document.getElementById("graphicSection");
const graphicOutput = document.getElementById("graphicOutput");
const finalAnswer = document.getElementById("finalAnswer");
const finalDescription = document.getElementById("finalDescription");
const formError = document.getElementById("formError");
const toast = document.getElementById("toast");
const standardEditor = document.getElementById("standardEditor");
const transportEditor = document.getElementById("transportEditor");
const transportMatrix = document.getElementById("transportMatrix");
const assignmentEditor = document.getElementById("assignmentEditor");
const assignmentMatrix = document.getElementById("assignmentMatrix");
const assignmentRowCount = document.getElementById("assignmentRowCount");
const assignmentColumnCount = document.getElementById("assignmentColumnCount");
const flowEditor = document.getElementById("flowEditor");
const flowEdges = document.getElementById("flowEdges");
const flowNodeCount = document.getElementById("flowNodeCount");
const flowEdgeCount = document.getElementById("flowEdgeCount");
const flowSource = document.getElementById("flowSource");
const flowSink = document.getElementById("flowSink");
const flowDemand = document.getElementById("flowDemand");
const flowDemandLabel = document.getElementById("flowDemandLabel");
const originCount = document.getElementById("originCount");
const destinationCount = document.getElementById("destinationCount");
const objectiveMode = document.getElementById("objectiveMode");
const brandHomeButtons = document.querySelectorAll(".brand-home");

let selectedMethod = "simplex";
let mode = "max";

function selectMethod(method, firstView = false) {
  selectedMethod = method;
  const data = methodData[method];
  currentMethodText.textContent = "Método";
  currentMethodIcon.textContent = data.icon;
  calcTitle.textContent = data.name;
  solutionTitle.textContent = data.title;
  const esTransporte = method === "transporte";
  const esAsignacion = method === "asignacion";
  const esFlujo = method === "flujoMaximo" || method === "flujoCostoMinimo";
  calculator.classList.toggle("transport-mode", esTransporte);
  calculator.classList.toggle("assignment-mode", esAsignacion);
  calculator.classList.toggle("flow-mode", esFlujo);
  standardEditor.classList.toggle("hidden", esTransporte || esAsignacion || esFlujo);
  constraintEditor.classList.toggle("hidden", esTransporte || esAsignacion || esFlujo);
  transportEditor.classList.toggle("hidden", !esTransporte);
  assignmentEditor.classList.toggle("hidden", !esAsignacion);
  flowEditor.classList.toggle("hidden", !esFlujo);
  flowDemandLabel.classList.toggle("hidden", method !== "flujoCostoMinimo");
  objectiveMode.classList.toggle("hidden", esTransporte || esAsignacion || esFlujo);
  addConstraint.classList.toggle("hidden", esTransporte || esAsignacion || esFlujo);
  if (esTransporte) renderTransportMatrix();
  if (esAsignacion) renderAssignmentMatrix();
  if (esFlujo) renderFlowEdges();
  document.querySelectorAll(".workspace-option").forEach(option => {
    option.classList.toggle("active", option.dataset.method === method);
    option.classList.toggle("bg-mist", option.dataset.method === method);
    option.querySelector(".option-check").classList.toggle("opacity-0", option.dataset.method !== method);
  });
  if (firstView) {
    welcomeScreen.classList.add("hidden");
    calculatorScreen.classList.remove("hidden");
    renderConstraintEditor();
  }

  methodMenu.classList.remove("show");
}

function collectAssignmentModel() {
  const rows = Number.parseInt(assignmentRowCount.value, 10);
  const columns = Number.parseInt(assignmentColumnCount.value, 10);
  if (!Number.isInteger(rows) || rows < 1 || rows > 20 || !Number.isInteger(columns) || columns < 1 || columns > 20) {
    throw new Error("La cantidad de trabajadores y tareas debe estar entre 1 y 20.");
  }
  const costos = Array.from({ length: rows }, (_, i) => Array.from({ length: columns }, (_, j) => {
    const input = assignmentMatrix.querySelector(`[data-assignment-row="${i}"][data-assignment-column="${j}"]`);
    if (!input) {
      throw new Error("Actualiza la matriz antes de resolver el problema de asignación.");
    }
    return parseTerm(input.value, `El costo del trabajador ${i + 1} y tarea ${j + 1}`);
  }));
  return { costos };
}

function collectFlowModel() {
  const nodos = Number.parseInt(flowNodeCount.value, 10);
  const origen = Number.parseInt(flowSource.value, 10);
  const destino = Number.parseInt(flowSink.value, 10);
  if (!Number.isInteger(nodos) || nodos < 2 || nodos > 20) throw new Error("La cantidad de nodos debe estar entre 2 y 20.");
  if (!Number.isInteger(origen) || !Number.isInteger(destino) || origen === destino || origen < 1 || destino < 1 || origen > nodos || destino > nodos) {
    throw new Error("El origen y el destino deben ser nodos distintos y válidos.");
  }
  const aristas = [...flowEdges.querySelectorAll(".flow-edge")].map((row, index) => ({
    origen: Number.parseInt(row.querySelector(".flow-from").value, 10),
    destino: Number.parseInt(row.querySelector(".flow-to").value, 10),
    capacidad: parseTerm(row.querySelector(".flow-capacity").value, `La capacidad de la arista ${index + 1}`),
    costo: parseTerm(row.querySelector(".flow-cost").value, `El costo de la arista ${index + 1}`)
  }));
  if (aristas.some(edge => edge.origen === edge.destino || edge.origen < 1 || edge.destino < 1 || edge.origen > nodos || edge.destino > nodos)) {
    throw new Error("Cada arista debe conectar dos nodos distintos y existentes.");
  }
  const model = { nodos, origen, destino, aristas };
  if (selectedMethod === "flujoCostoMinimo") model.flujo_requerido = parseTerm(flowDemand.value, "El flujo requerido");
  return model;
}

document.querySelectorAll(".method-card").forEach(card => {
  card.addEventListener("click", () => selectMethod(card.dataset.method, true));
});

brandHomeButtons.forEach(button => {
  button.addEventListener("click", async () => {
    await resetCalculator(true);
    calculatorScreen.classList.add("hidden");
    welcomeScreen.classList.remove("hidden");
    methodMenu.classList.remove("show");
  });
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

function renderAssignmentResult(result) {
  graphicSection.classList.add("hidden");
  stepsTitle.textContent = "3. Desarrollo paso a paso de Kuhn-Munkres";
  const renderAssignmentMatrix = (matrix, assignments = []) => {
    if (!matrix) return "";
    const selected = new Set((assignments || []).map(([worker, column]) => `${worker}-${column}`));
    return `<div class="mt-3 overflow-x-auto"><table class="w-full min-w-[420px] border-collapse font-mono text-[11px]"><thead><tr><th class="border border-ink/10 bg-ink px-2 py-1.5 text-left text-white">Trabajador</th>${matrix[0].map((_, column) => `<th class="border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">T${column + 1}</th>`).join("")}</tr></thead><tbody>${matrix.map((row, worker) => `<tr><th class="border border-ink/10 bg-mist px-2 py-1.5 text-left">Trabajador ${worker + 1}</th>${row.map((value, column) => `<td class="border border-ink/10 px-2 py-1.5 text-right${selected.has(`${worker}-${column}`) ? " bg-ice font-bold" : ""}">${formatNumber(value)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  };
  stepsOutput.innerHTML = result.pasos.map((step, index) => `
    <article class="rounded-xl border-l-4 border-steel bg-[#F6F9FA] p-4 text-sm leading-6">
      <div class="mb-2 flex items-center gap-2"><span class="grid size-6 place-items-center rounded-full bg-ice text-xs font-extrabold">${index + 1}</span><strong>${step.titulo}</strong></div>
      <span class="whitespace-pre-line text-xs leading-5 text-[#597081]">${step.detalle}</span>
      ${renderAssignmentMatrix(step.matriz, step.asignaciones)}
    </article>
  `).join("") + `
    <article class="rounded-xl border border-ink/10 bg-mist p-4">
      <h4 class="mb-2 text-sm font-bold">Asignación óptima</h4>
      <div class="grid gap-2 font-mono text-xs">${result.asignaciones.map(item => `<div>Trabajador ${item.fila + 1} → Tarea ${item.columna + 1} · costo ${formatNumber(item.costo)}</div>`).join("")}</div>
    </article>
  `;
  finalAnswer.textContent = `Costo mínimo: ${formatNumber(result.costo_total)}`;
  finalDescription.textContent = "Cada trabajador se asigna a una sola tarea y cada tarea recibe un solo trabajador. Las celdas azules son los ceros seleccionados.";
}

function renderTransportMatrix() {
  const origins = Number.parseInt(originCount.value, 10);
  const destinations = Number.parseInt(destinationCount.value, 10);
  if (!Number.isInteger(origins) || origins < 1 || origins > 10 || !Number.isInteger(destinations) || destinations < 1 || destinations > 10) return;
  const transportWidth = Math.min(1180, Math.max(620, 210 + destinations * 78));
  calculator.style.setProperty("--transport-width", `${transportWidth}px`);
  transportMatrix.innerHTML = `
    <table class="w-full border-collapse text-xs">
      <thead><tr><th class="p-2 text-left">Costo</th>${Array.from({ length: destinations }, (_, j) => `<th class="p-2">D${j + 1}</th>`).join("")}<th class="p-2">Oferta</th></tr></thead>
      <tbody>${Array.from({ length: origins }, (_, i) => `
        <tr><th class="p-1 text-left">O${i + 1}</th>${Array.from({ length: destinations }, (_, j) => `<td class="p-1"><input class="transport-cost w-16 rounded-lg border border-ink/10 bg-white px-2 py-2 text-center" type="number" min="0" step="any" value="${i === j ? 2 : 5}" data-origin="${i}" data-destination="${j}" aria-label="Costo O${i + 1} D${j + 1}"></td>`).join("")}<td class="p-1"><input class="transport-supply w-20 rounded-lg border border-ink/10 bg-white px-2 py-2 text-center" type="number" min="0" step="any" value="20" data-origin="${i}" aria-label="Oferta O${i + 1}"></td></tr>
      `).join("")}</tbody>
      <tfoot><tr><th class="p-2 text-left">Demanda</th>${Array.from({ length: destinations }, (_, j) => `<td class="p-1"><input class="transport-demand w-20 rounded-lg border border-ink/10 bg-white px-2 py-2 text-center" type="number" min="0" step="any" value="15" data-destination="${j}" aria-label="Demanda D${j + 1}"></td>`).join("")}<td></td></tr></tfoot>
    </table>
  `;
}

function renderAssignmentMatrix() {
  const rows = Number.parseInt(assignmentRowCount.value, 10);
  const columns = Number.parseInt(assignmentColumnCount.value, 10);
  if (!Number.isInteger(rows) || rows < 1 || rows > 20 || !Number.isInteger(columns) || columns < 1 || columns > 20) return;
  const assignmentWidth = Math.min(1180, Math.max(620, 210 + columns * 78));
  calculator.style.setProperty("--assignment-width", `${assignmentWidth}px`);
  assignmentMatrix.style.setProperty("--assignment-width", `${Math.max(420, 150 + columns * 78)}px`);
  assignmentMatrix.innerHTML = `
    <table class="w-full border-collapse text-xs">
      <thead><tr><th class="p-2 text-left">Costo</th>${Array.from({ length: columns }, (_, j) => `<th class="p-2">T${j + 1}</th>`).join("")}</tr></thead>
      <tbody>${Array.from({ length: rows }, (_, i) => `
        <tr><th class="p-1 text-left">Trabajador ${i + 1}</th>${Array.from({ length: columns }, (_, j) => `<td class="p-1"><input class="assignment-cost w-16 rounded-lg border border-ink/10 bg-white px-2 py-2 text-center" type="number" min="0" step="any" value="${i === j ? 2 : 5}" data-assignment-row="${i}" data-assignment-column="${j}" aria-label="Costo trabajador ${i + 1} tarea ${j + 1}"></td>`).join("")}</tr>
      `).join("")}</tbody>
    </table>
  `;
}

function renderFlowEdges() {
  const count = Number.parseInt(flowEdgeCount.value, 10);
  const nodes = Number.parseInt(flowNodeCount.value, 10);
  if (!Number.isInteger(count) || count < 1 || count > 40 || !Number.isInteger(nodes) || nodes < 2 || nodes > 20) return;
  calculator.style.setProperty("--flow-width", `${Math.min(820, Math.max(470, 330 + nodes * 18))}px`);
  flowEdges.innerHTML = Array.from({ length: count }, (_, index) => `
    <div class="flow-edge grid grid-cols-2 gap-2 rounded-xl border border-ink/10 bg-mist/50 p-2 sm:grid-cols-4">
      <label class="flow-field text-[10px] font-extrabold text-[#597081]">Desde
        <input class="flow-from mt-1 w-full rounded-lg border border-ink/10 bg-white px-2 py-2 text-center text-xs" type="number" min="1" max="${nodes}" value="${index % nodes + 1}" aria-label="Origen de arista ${index + 1}">
      </label>
      <label class="flow-field text-[10px] font-extrabold text-[#597081]">Hasta
        <input class="flow-to mt-1 w-full rounded-lg border border-ink/10 bg-white px-2 py-2 text-center text-xs" type="number" min="1" max="${nodes}" value="${(index + 1) % nodes + 1}" aria-label="Destino de arista ${index + 1}">
      </label>
      <label class="flow-field text-[10px] font-extrabold text-[#597081]">Capacidad
        <input class="flow-capacity mt-1 w-full rounded-lg border border-ink/10 bg-white px-2 py-2 text-center text-xs" type="number" min="0" step="any" value="10" aria-label="Capacidad de arista ${index + 1}">
      </label>
      <label class="flow-field text-[10px] font-extrabold text-[#597081]">Costo
        <input class="flow-cost mt-1 w-full rounded-lg border border-ink/10 bg-white px-2 py-2 text-center text-xs" type="number" step="any" value="${index + 1}" aria-label="Costo de arista ${index + 1}">
      </label>
    </div>
  `).join("");
}

function formatFlowModel(model) {
  objectivePreview.textContent = `${selectedMethod === "flujoMaximo" ? "FLUJO MÁXIMO" : "FLUJO A COSTO MÍNIMO"} · ${model.nodos} nodos · ${model.aristas.length} aristas`;
  constraintsPreview.innerHTML = `<div class="constraint-result">Origen: N${model.origen} · Destino: N${model.destino}</div>${model.flujo_requerido === undefined ? "" : `<div class="constraint-result">Flujo requerido: ${formatNumber(model.flujo_requerido)}</div>`}`;
}

function renderFlowResult(result) {
  graphicSection.classList.add("hidden");
  stepsTitle.textContent = "3. Desarrollo paso a paso del algoritmo de flujo";
  const renderFlowState = state => !state?.length ? "" : `
    <div class="mt-3 overflow-x-auto">
      <table class="w-full min-w-[440px] border-collapse font-mono text-[11px]">
        <thead><tr><th class="border border-ink/10 bg-ink px-2 py-1.5 text-left text-white">Arista</th><th class="border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">Flujo</th><th class="border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">Capacidad</th>${selectedMethod === "flujoCostoMinimo" ? '<th class="border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">Costo</th>' : ""}</tr></thead>
        <tbody>${state.map(edge => `<tr><td class="border border-ink/10 px-2 py-1.5">N${edge.origen} → N${edge.destino}</td><td class="border border-ink/10 px-2 py-1.5 text-right">${formatNumber(edge.flujo)}</td><td class="border border-ink/10 px-2 py-1.5 text-right">${formatNumber(edge.capacidad)}</td>${selectedMethod === "flujoCostoMinimo" ? `<td class="border border-ink/10 px-2 py-1.5 text-right">${formatNumber(edge.costo)}</td>` : ""}</tr>`).join("")}</tbody>
      </table>
    </div>`;
  stepsOutput.innerHTML = result.pasos.map((step, index) => `
    <article class="rounded-xl border-l-4 border-steel bg-[#F6F9FA] p-4">
      <div class="mb-1 flex items-center gap-2"><span class="grid size-6 place-items-center rounded-full bg-ice text-xs font-extrabold">${index + 1}</span><strong>${step.titulo}</strong></div>
      <span class="whitespace-pre-line text-xs leading-5 text-[#597081]">${step.detalle}</span>
      ${renderFlowState(step.estado)}
    </article>`).join("") + `
    <article class="rounded-xl border border-ink/10 bg-mist p-4">
      <h4 class="mb-2 text-sm font-bold">Flujo final por arista</h4>
      <div class="grid gap-2 font-mono text-xs">
        ${result.flujos.map(edge => `<div>N${edge.origen} → N${edge.destino}: ${formatNumber(edge.flujo)} / ${formatNumber(edge.capacidad)}${selectedMethod === "flujoCostoMinimo" ? ` · costo ${formatNumber(edge.costo)}` : ""}</div>`).join("")}
      </div>
    </article>`;
  finalAnswer.textContent = selectedMethod === "flujoMaximo"
    ? `Flujo máximo: ${formatNumber(result.flujo)}`
    : `Costo mínimo: ${formatNumber(result.costo_total)}`;
  finalDescription.textContent = result.mensaje;
}

variableCount.addEventListener("change", renderConstraintEditor);
constraintCount.addEventListener("change", renderConstraintEditor);
addConstraint.addEventListener("click", () => {
  renderConstraintEditor();
  showToast("Campos de restricciones actualizados");
});
originCount.addEventListener("change", renderTransportMatrix);
destinationCount.addEventListener("change", renderTransportMatrix);
assignmentRowCount.addEventListener("input", renderAssignmentMatrix);
assignmentColumnCount.addEventListener("input", renderAssignmentMatrix);
flowNodeCount.addEventListener("change", renderFlowEdges);
flowEdgeCount.addEventListener("change", renderFlowEdges);

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

function collectTransportModel() {
  const origins = Number.parseInt(originCount.value, 10);
  const destinations = Number.parseInt(destinationCount.value, 10);
  const costos = Array.from({ length: origins }, (_, i) => Array.from({ length: destinations }, (_, j) => {
    const input = transportMatrix.querySelector(`[data-origin="${i}"][data-destination="${j}"]`);
    return parseTerm(input.value, `El costo O${i + 1}-D${j + 1}`);
  }));
  const oferta = Array.from({ length: origins }, (_, i) => parseTerm(transportMatrix.querySelector(`.transport-supply[data-origin="${i}"]`).value, `La oferta O${i + 1}`));
  const demanda = Array.from({ length: destinations }, (_, j) => parseTerm(transportMatrix.querySelector(`.transport-demand[data-destination="${j}"]`).value, `La demanda D${j + 1}`));
  return { costos, oferta, demanda };
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

function formatTransportModel(model) {
  objectivePreview.textContent = `Problema de transporte · ${model.oferta.length} orígenes · ${model.demanda.length} destinos`;
  constraintsPreview.innerHTML = `<div class="constraint-result">Oferta: [${model.oferta.map(formatNumber).join(", ")}]</div><div class="constraint-result">Demanda: [${model.demanda.map(formatNumber).join(", ")}]</div>`;
}

function formatAssignmentModel(model) {
  objectivePreview.textContent = `KUHN-MUNKRES · minimizar costo · ${model.costos.length} trabajador(es) · ${model.costos[0].length} tarea(s)`;
  constraintsPreview.innerHTML = `
    <div class="constraint-result">1. Normalizar la matriz a formato cuadrado con costos ficticios 0 si hace falta.</div>
    <div class="constraint-result">2. Reducir filas y columnas; cubrir ceros y ajustar hasta hallar ceros independientes.</div>`;
}

function renderAllocationTable(solution, result) {
  const body = solution.asignaciones.map((row, i) => `<tr><th class="border border-ink/10 px-2 py-1.5 text-left">O${i + 1}</th>${row.map(value => `<td class="border border-ink/10 px-2 py-1.5 text-right">${formatNumber(value)}</td>`).join("")}</tr>`).join("");
  return `<div class="mb-3 overflow-x-auto"><table class="w-full border-collapse font-mono text-[11px]"><thead><tr><th class="border border-ink/10 bg-ink px-2 py-1.5 text-left text-white">Asignación</th>${solution.asignaciones[0].map((_, j) => `<th class="border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">D${j + 1}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div><p class="font-bold">Costo total: ${formatNumber(solution.costo_total)}</p>`;
}

function renderTransportResult(result) {
  graphicSection.classList.add("hidden");
  stepsTitle.textContent = "3. Desarrollo de los métodos de transporte";
  objectivePreview.textContent = "Problema de transporte balanceado";
  constraintsPreview.innerHTML = `<div class="constraint-result">${result.mensaje}</div>`;
  stepsOutput.innerHTML = result.soluciones.map(solution => `
    <article class="rounded-xl border border-ink/10 bg-[#F6F9FA] p-4">
      <h4 class="mb-2 text-base font-bold">${solution.nombre} · Costo ${formatNumber(solution.costo_total)}</h4>
      ${solution.pasos.map(step => `<div class="mb-2 rounded-lg bg-white p-3"><strong class="block text-xs">${step.titulo}</strong><span class="whitespace-pre-line text-xs leading-5 text-[#597081]">${step.detalle}</span></div>`).join("")}
      ${renderAllocationTable(solution, result)}
    </article>
  `).join("");
  const mejor = result.soluciones.reduce((actual, solution) => solution.costo_total < actual.costo_total ? solution : actual);
  finalAnswer.textContent = `Mejor costo: ${formatNumber(mejor.costo_total)}`;
  finalDescription.textContent = `La solución con menor costo inicial es la obtenida por ${mejor.nombre}. Posteriormente se podrá verificar y optimizar con MODI.`;
}

function sectionLabel(text) {
  return `<span class="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-[#597081]">${text}</span>`;
}

function renderTablaCompleta(step) {
  return `<div class="overflow-x-auto"><table class="w-full border-collapse font-mono text-[11px]"><thead><tr>${step.encabezados.map(header => `<th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">${header}</th>`).join("")}</tr></thead><tbody>${step.tabla.map(row => `<tr>${row.map(cell => `<td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${formatNumber(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function renderVectorRow(labels, values, opts = {}) {
  const { highlightIndex = -1 } = opts;
  return `<table class="w-full border-collapse font-mono text-[11px]"><thead><tr>${labels.map(label => `<th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">${label}</th>`).join("")}</tr></thead><tbody><tr>${values.map((value, index) => `<td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right${index === highlightIndex ? " bg-ice/60 font-semibold" : ""}">${formatNumber(value)}</td>`).join("")}</tr></tbody></table>`;
}

function renderMatrizB(rowLabels, matriz) {
  const colHeaders = matriz[0].map((_, index) => `F${index + 1}`);
  return `<table class="w-full border-collapse font-mono text-[11px]"><thead><tr><th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white"></th>${colHeaders.map(header => `<th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">${header}</th>`).join("")}</tr></thead><tbody>${matriz.map((row, indice) => `<tr><th class="whitespace-nowrap border border-ink/10 bg-mist px-2 py-1.5 text-right text-ink">${rowLabels[indice]}</th>${row.map(value => `<td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${formatNumber(value)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
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
        <div class="mt-3">${renderTablaCompleta(step)}</div>
      </div>
    `).join("")}
  `;
}

// Vista propia del método simplex revisado: en vez de repetir la tabla completa
// (que es lo que distingue al método clásico), expone las operaciones que
// realmente se hacen a cada iteración: B⁻¹, y = c_B·B⁻¹, x_B = B⁻¹·b, los
// costos reducidos usados para elegir la variable entrante y la columna
// B⁻¹·A(entra) con la prueba de razón mínima para elegir la que sale.
function renderStepsRevisado(result, title) {
  const values = result.valores_variables.map((value, index) => `${result.nombres_variables[index] || `x${index + 1}`} = ${formatNumber(value)}`).join(", ");
  return `
    <div class="mb-3 rounded-xl bg-mist px-4 py-3">
      <strong class="block text-base">${title}</strong>
      <span class="mt-1 block text-xs text-[#597081]">${result.mensaje}</span>
      ${values ? `<span class="mt-1 block font-mono text-xs">${values}</span>` : ""}
    </div>
    ${result.pasos.map(step => {
      if (!Array.isArray(step.base_inversa)) {
        // Respaldo por si el backend desplegado aún no envía los campos del método revisado.
        return `
          <div class="mb-3 rounded-xl border-l-4 border-steel bg-[#F6F9FA] p-4 text-sm leading-6">
            <strong class="block">${step.fase} · Iteración ${step.iteracion}</strong>
            <span class="mt-1 block text-[#597081]">${step.entra ? `Entra ${step.entra}` : "Tabla inicial"}${step.sale ? ` · Sale ${step.sale}` : ""}</span>
            <div class="mt-3">${renderTablaCompleta(step)}</div>
          </div>
        `;
      }
      const variables = step.encabezados.slice(0, -1);
      const entraIndice = step.entra ? variables.indexOf(step.entra) : -1;
      const filaSaleIndice = step.sale ? step.base.indexOf(step.sale) : -1;
      return `
        <div class="mb-3 rounded-xl border-l-4 border-steel bg-[#F6F9FA] p-4 text-sm leading-6">
          <strong class="block">${step.fase} · Iteración ${step.iteracion}</strong>
          <span class="mt-1 block text-[#597081]">${step.entra ? `Entra ${step.entra}` : "Base óptima"}${step.sale ? ` · Sale ${step.sale}` : ""}${step.razon ? ` · ${step.razon}` : ""}</span>

          <div class="mt-3">
            ${sectionLabel("Base actual")}
            <span class="font-mono text-xs">{ ${step.base.join(", ")} }</span>
          </div>

          <div class="mt-3 grid gap-3 md:grid-cols-2">
            <div>
              ${sectionLabel("c_B (costos de las variables básicas)")}
              ${renderVectorRow(step.base, step.cb)}
            </div>
            <div>
              ${sectionLabel("x_B = B⁻¹ · b (valor de las básicas)")}
              ${renderVectorRow(step.base, step.xb)}
            </div>
          </div>

          <div class="mt-3">
            ${sectionLabel("B⁻¹ (inversa de la matriz base)")}
            ${renderMatrizB(step.base, step.base_inversa)}
          </div>

          <div class="mt-3">
            ${sectionLabel("y = c_B · B⁻¹")}
            ${renderVectorRow(step.base.map((_, indice) => `F${indice + 1}`), step.y)}
          </div>

          <div class="mt-3">
            ${sectionLabel("Costos reducidos c_j − y·A_j (se elige el mayor positivo)")}
            ${renderVectorRow(variables, step.costos_reducidos, { highlightIndex: entraIndice })}
          </div>

          ${step.columna_pivote ? `
          <div class="mt-3">
            ${sectionLabel(`Columna entrante B⁻¹·A(${step.entra}) y prueba de razón mínima`)}
            <table class="w-full border-collapse font-mono text-[11px]"><thead><tr>
              <th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">Básica</th>
              <th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">x_B</th>
              <th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">B⁻¹·A(${step.entra})</th>
              <th class="whitespace-nowrap border border-ink/10 bg-ink px-2 py-1.5 text-right text-white">Razón</th>
            </tr></thead><tbody>
              ${step.base.map((nombre, fila) => {
                const direccion = step.columna_pivote[fila];
                const razon = direccion > 1e-9 ? formatNumber(step.xb[fila] / direccion) : "—";
                const esSalida = fila === filaSaleIndice;
                return `<tr class="${esSalida ? "bg-ice/60 font-semibold" : ""}"><td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${nombre}</td><td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${formatNumber(step.xb[fila])}</td><td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${formatNumber(direccion)}</td><td class="whitespace-nowrap border border-ink/10 px-2 py-1.5 text-right">${razon}</td></tr>`;
              }).join("")}
            </tbody></table>
          </div>` : ""}

          <details class="mt-3">
            <summary class="cursor-pointer text-xs font-semibold text-[#597081]">Ver tabla equivalente (comparar con el método clásico)</summary>
            <div class="mt-2">${renderTablaCompleta(step)}</div>
          </details>
        </div>
      `;
    }).join("")}
  `;
}

function renderSimplexResult(result) {
  graphicSection.classList.add("hidden");
  stepsTitle.textContent = "3. Desarrollo del método";
  const values = result.valores_variables.map((value, index) => `${result.nombres_variables[index] || `x${index + 1}`} = ${formatNumber(value)}`).join(", ");
  finalAnswer.textContent = result.valor_objetivo === null ? result.estado : `Z = ${formatNumber(result.valor_objetivo)}`;
  finalDescription.textContent = `${result.mensaje} ${values}`;
  const nombreMetodo = methodData[selectedMethod]?.name ?? "Simplex";
  stepsOutput.innerHTML = selectedMethod === "simplexRevisado"
    ? renderStepsRevisado(result, nombreMetodo)
    : renderSteps(result, nombreMetodo);
}

function renderGraphicResult(result, model) {
  graphicSection.classList.remove("hidden");
  stepsTitle.textContent = "4. Vértices candidatos";
  const points = result.vertices;
  const maxCoordinate = Math.max(
    10,
    ...points.flatMap(point => [point.x, point.y]),
    ...model.restricciones.flatMap(restriction => {
      const [a, b] = restriction.coeficientes;
      return [
        Math.abs(a) > 1e-8 ? Math.abs(restriction.termino_independiente / a) : 0,
        Math.abs(b) > 1e-8 ? Math.abs(restriction.termino_independiente / b) : 0
      ];
    })
  ) * 1.12;
  const width = 620;
  const height = 360;
  const padding = { left: 48, right: 18, top: 18, bottom: 38 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const toSvg = (x, y) => ({
    x: padding.left + (x / maxCoordinate) * plotWidth,
    y: height - padding.bottom - (y / maxCoordinate) * plotHeight
  });
  const cross = (origin, first, second) => (
    (first.x - origin.x) * (second.y - origin.y)
    - (first.y - origin.y) * (second.x - origin.x)
  );
  const hull = [...points].sort((a, b) => a.x - b.x || a.y - b.y).reduce((result, point) => {
    while (result.length >= 2 && cross(result[result.length - 2], result[result.length - 1], point) <= 0) result.pop();
    result.push(point);
    return result;
  }, []);
  const upperHull = [...points].sort((a, b) => a.x - b.x || a.y - b.y).reverse().reduce((result, point) => {
    while (result.length >= 2 && cross(result[result.length - 2], result[result.length - 1], point) <= 0) result.pop();
    result.push(point);
    return result;
  }, []);
  const polygon = [...hull.slice(0, -1), ...upperHull.slice(0, -1)];
  const polygonPoints = polygon.map(point => {
    const svgPoint = toSvg(point.x, point.y);
    return `${svgPoint.x},${svgPoint.y}`;
  }).join(" ");
  const lines = model.restricciones.map((restriction, index) => {
    const [a, b] = restriction.coeficientes;
    const rhs = restriction.termino_independiente;
    if (Math.abs(a) <= 1e-8 && Math.abs(b) <= 1e-8) return "";
    const start = Math.abs(b) > 1e-8 ? toSvg(0, rhs / b) : toSvg(rhs / a, 0);
    const end = Math.abs(b) > 1e-8 ? toSvg(maxCoordinate, (rhs - a * maxCoordinate) / b) : start;
    return `<line x1="${start.x}" y1="${start.y}" x2="${end.x}" y2="${end.y}" stroke="#7EA0B7" stroke-width="2" stroke-dasharray="6 4"/><text x="${Math.max(padding.left, Math.min(width - 35, end.x - 4))}" y="${Math.max(padding.top + 12, Math.min(height - padding.bottom, end.y - 5))}" class="graph-label">R${index + 1}</text>`;
  }).join("");
  const pointMarks = points.map((point, index) => {
    const svgPoint = toSvg(point.x, point.y);
    return `<circle cx="${svgPoint.x}" cy="${svgPoint.y}" r="4.5" fill="${index === points.findIndex(item => item.x === result.valores_variables[0] && item.y === result.valores_variables[1]) ? "#36494E" : "#50856E"}"/><text x="${svgPoint.x + 7}" y="${svgPoint.y - 7}" class="graph-label">(${formatNumber(point.x)}, ${formatNumber(point.y)})</text>`;
  }).join("");
  const ticks = Array.from({ length: 5 }, (_, index) => {
    const value = (maxCoordinate / 4) * index;
    const x = toSvg(value, 0).x;
    const y = toSvg(0, value).y;
    return `<text x="${x}" y="${height - 14}" class="graph-axis-label" text-anchor="middle">${formatNumber(value)}</text><text x="${padding.left - 8}" y="${y + 4}" class="graph-axis-label" text-anchor="end">${formatNumber(value)}</text>`;
  }).join("");
  graphicOutput.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="min-w-[560px] w-full" role="img" aria-label="Gráfica de la región factible">
      <style>.graph-label{font:10px 'DM Mono',monospace;fill:#36494E}.graph-axis-label{font:10px 'DM Mono',monospace;fill:#597081}</style>
      <rect x="${padding.left}" y="${padding.top}" width="${plotWidth}" height="${plotHeight}" fill="#fff" rx="12"/>
      <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" stroke="#36494E" stroke-width="1.5"/>
      <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${padding.left}" y2="${padding.top}" stroke="#36494E" stroke-width="1.5"/>
      ${ticks}${lines}
      ${points.length > 2 ? `<polygon points="${polygonPoints}" fill="#A9CEF4" fill-opacity=".45" stroke="#50856E" stroke-width="2"/>` : ""}
      ${pointMarks}
      <text x="${width - 13}" y="${height - padding.bottom + 2}" class="graph-label">x1</text>
      <text x="${padding.left - 8}" y="${padding.top - 5}" class="graph-label">x2</text>
    </svg>
  `;
  const detailedSteps = (result.pasos || []).map(step => `
    <article class="rounded-xl border border-ink/10 bg-[#F6F9FA] p-4">
      <h4 class="mb-2 text-sm font-bold text-ink">${step.titulo}</h4>
      <div class="whitespace-pre-line font-mono text-xs leading-6 text-[#597081]">${step.detalle}</div>
    </article>
  `).join("");
  const verticesStep = points.length
    ? `<article class="rounded-xl border border-ink/10 bg-mist p-4">
        <h4 class="mb-2 text-sm font-bold text-ink">Vértices factibles encontrados</h4>
        ${points.map((point, index) => `<div class="font-mono text-xs leading-6">${index + 1}. (${formatNumber(point.x)}, ${formatNumber(point.y)}) → Z = ${formatNumber(point.valor_objetivo)}</div>`).join("")}
      </article>`
    : `<article class="rounded-xl bg-[#F8EEEE] px-4 py-3 text-sm text-[#9A4E4E]">${result.mensaje}</article>`;
  stepsOutput.innerHTML = detailedSteps + verticesStep;
  finalAnswer.textContent = result.valor_objetivo === null ? result.estado : `Z = ${formatNumber(result.valor_objetivo)}`;
  finalDescription.textContent = `${result.mensaje} x1 = ${formatNumber(result.valores_variables[0] ?? 0)}, x2 = ${formatNumber(result.valores_variables[1] ?? 0)}`;
}

function renderDualResult(result) {
  graphicSection.classList.add("hidden");
  stepsTitle.textContent = "3. Desarrollo del método";
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
    const model = selectedMethod === "transporte" ? collectTransportModel() : selectedMethod === "asignacion" ? collectAssignmentModel() : selectedMethod === "flujoMaximo" || selectedMethod === "flujoCostoMinimo" ? collectFlowModel() : collectModel();
    if (selectedMethod === "transporte") formatTransportModel(model);
    else if (selectedMethod === "asignacion") formatAssignmentModel(model);
    else if (selectedMethod === "flujoMaximo" || selectedMethod === "flujoCostoMinimo") formatFlowModel(model);
    else formatModel(model);
    if (selectedMethod === "grafico" && model.objetivo.length !== 2) {
      throw new Error("El método gráfico requiere exactamente dos variables.");
    }
    const endpoint = endpointFor(selectedMethod);
    const response = await fetch(`${API_URL}${endpoint}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(model) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 404 && selectedMethod === "simplexRevisado") {
        throw new Error("El backend desplegado aún no tiene disponible el método Simplex Revisado.");
      }
      throw new Error(data.detail?.[0]?.msg || `La API rechazó el modelo (${response.status}).`);
    }
    if (selectedMethod === "dualidad") renderDualResult(data);
    else if (selectedMethod === "grafico") renderGraphicResult(data, model);
    else if (selectedMethod === "transporte") renderTransportResult(data);
    else if (selectedMethod === "asignacion") renderAssignmentResult(data);
    else if (selectedMethod === "flujoMaximo" || selectedMethod === "flujoCostoMinimo") renderFlowResult(data);
    else renderSimplexResult(data);
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
  originCount.value = "3";
  destinationCount.value = "4";
  assignmentRowCount.value = "3";
  assignmentColumnCount.value = "3";
  flowNodeCount.value = "4";
  flowEdgeCount.value = "5";
  flowSource.value = "1";
  flowSink.value = "4";
  flowDemand.value = "10";
  renderTransportMatrix();
  renderAssignmentMatrix();
  renderFlowEdges();
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
renderTransportMatrix();
renderAssignmentMatrix();
renderFlowEdges();

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2200);
}
