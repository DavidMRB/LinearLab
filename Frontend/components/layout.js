import { methodData, iconImg } from "../modules/methods.js";

const logo = `
  <button type="button" class="brand-home flex items-center gap-3 text-[17px] font-extrabold tracking-wide" aria-label="Volver al inicio y seleccionar un método">
    <div class="grid size-10 place-items-center overflow-hidden rounded-xl bg-ink shadow-lg">
      <img src="image.svg" alt="LinearLab" class="size-full object-contain p-1.5">
    </div>
    <span>LINEAR<span class="text-steel">LAB</span></span>
  </button>`;

const methods = Object.values(methodData);

function methodCards() {
  return methods.map(({ id, name, description }, index) => `
    <button style="--i:${index}" class="method-card group flex min-h-0 flex-row items-center gap-4 rounded-3xl border border-ink/10 bg-white/75 p-4 text-left shadow-sm transition hover:-translate-y-1.5 hover:border-steel hover:shadow-2xl sm:min-h-[218px] sm:flex-col sm:items-start sm:p-6" data-method="${id}">
      <div class="grid size-14 shrink-0 place-items-center overflow-hidden rounded-2xl sm:size-16">${iconImg(id)}</div>
      <div class="min-w-0 flex-1"><h2 class="mb-1 text-base font-bold leading-tight sm:mb-2 sm:text-lg">${name}</h2><p class="text-[13px] leading-5 text-[#597081]">${description}</p></div>
      <div class="text-2xl text-steel transition group-hover:translate-x-1.5 sm:self-end">→</div>
    </button>`).join("");
}

function methodOptions() {
  return methods.map(({ id, icon, name, description }) => `
    <button class="workspace-option group relative flex min-h-[112px] min-w-0 flex-col items-center justify-start gap-2 rounded-2xl px-2 py-3 text-center transition hover:bg-mist" data-method="${id}" title="${description}">
      <div class="grid size-12 shrink-0 place-items-center overflow-hidden rounded-2xl transition group-hover:scale-105">${iconImg(id)}</div>
      <strong class="line-clamp-2 text-[12px] leading-4">${name}</strong>
      <span class="option-check absolute right-2 top-2 text-xs font-bold text-steel opacity-0">✓</span>
    </button>`).join("");
}

export function renderLayout() {
  document.getElementById("app").innerHTML = `
    <section id="welcomeScreen" class="relative flex min-h-screen flex-col bg-[linear-gradient(90deg,rgba(169,206,244,.18)_1px,transparent_1px),linear-gradient(rgba(169,206,244,.12)_1px,transparent_1px),#F6F8FA] bg-[length:42px_42px] px-4 py-6 sm:px-12 sm:py-8 lg:px-16 xl:px-28">
      ${logo}
      <div class="mx-auto my-auto w-full max-w-[1500px] py-8 sm:py-12 lg:py-16">
        <p class="mb-3 text-[11px] font-extrabold tracking-[2px] text-steel sm:mb-4">CALCULADORA DE PROGRAMACIÓN LINEAL</p>
        <h1 class="max-w-3xl text-[2rem] font-extrabold leading-tight tracking-tight min-[400px]:text-4xl sm:text-6xl lg:text-7xl">Selecciona un<br><span class="text-steel">método de resolución</span></h1>
        <p class="my-5 max-w-2xl text-[15px] leading-7 text-[#597081] sm:my-7 sm:text-lg sm:leading-8">Elige el método que deseas utilizar para resolver tu problema de programación lineal.</p>
        <div class="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-4">${methodCards()}</div>
      </div>
      <div class="absolute bottom-0 left-0 h-2 w-full bg-[linear-gradient(90deg,#A9CEF4_0_20%,#36494E_20%_40%,#000_40%_60%,#7EA0B7_60%_80%,#597081_80%)]"></div>
    </section>

    <section id="calculatorScreen" class="hidden min-h-screen px-4 py-4 sm:px-10 sm:py-5 lg:px-16">
      <header class="mx-auto flex min-h-14 max-w-[1500px] items-center justify-between gap-2 sm:min-h-16 sm:gap-5 short:min-h-12 short:gap-3">
        ${logo}
        <div class="ml-auto flex items-center gap-1 sm:gap-2">
          <div class="sm:relative">
            <button id="currentMethod" class="flex min-h-11 items-center gap-2 rounded-2xl border border-ink/10 bg-white px-3 py-1.5 font-bold shadow-lg shadow-ink/5 sm:px-4 sm:py-2.5 short:py-2" aria-label="Cambiar de método"><span id="currentMethodIcon" class="grid size-8 place-items-center overflow-hidden rounded-lg"></span><span id="currentMethodText" class="hidden sm:inline">Método</span><span class="text-steel">⌄</span></button>
            <div id="methodMenu" class="pointer-events-none fixed inset-x-4 top-[4.5rem] z-20 max-h-[calc(100svh-5.5rem)] -translate-y-2 scale-95 overflow-y-auto rounded-[28px] border border-ink/10 bg-white/95 p-4 opacity-0 shadow-2xl backdrop-blur transition sm:absolute sm:inset-x-auto sm:right-0 sm:top-[calc(100%+12px)] sm:w-[min(30rem,calc(100vw-2rem))] sm:p-5 [&.show]:pointer-events-auto [&.show]:translate-y-0 [&.show]:scale-100 [&.show]:opacity-100">
              <div class="px-2 pb-4 pt-1 text-[11px] font-extrabold tracking-[1.5px] text-steel">MÉTODOS DISPONIBLES</div>
              <div class="grid grid-cols-3 gap-2 sm:grid-cols-4">${methodOptions()}</div>
            </div>
          </div>
          <button id="resetBtn" class="min-h-11 min-w-11 rounded-xl px-3 py-2.5 font-bold text-[#597081] transition hover:bg-[#597081]/10 sm:px-4" title="Nuevo ejercicio" aria-label="Nuevo ejercicio">↺ <span class="hidden sm:inline">Nuevo ejercicio</span></button>
        </div>
      </header>
      <div id="workArea" class="mx-auto mt-4 flex min-h-0 w-full max-w-[1500px] min-w-0 flex-col items-stretch justify-start gap-5 overflow-visible pb-10 transition-[gap,justify-content,align-items] duration-700 ease-[cubic-bezier(.22,.8,.25,1)] sm:mt-5 sm:gap-7 xl:h-[calc(100svh-9rem)] xl:flex-row xl:items-center xl:justify-center xl:[&.show-results]:items-start xl:[&.show-results]:justify-start short:mt-2 short:pb-4">
        ${resultsTemplate()}
        ${calculatorTemplate()}
      </div>
    </section>`;
}

function resultsTemplate() {
  return `<section id="solutionPanel" class="hidden order-2 w-full min-w-0 scroll-mt-4 opacity-0 transition xl:order-1 xl:w-0 xl:max-w-4xl xl:translate-x-16 xl:overflow-hidden xl:[.show-results_&]:block xl:[.show-results_&]:w-[calc(100%-440px)] xl:[.show-results_&]:translate-x-0 xl:[.show-results_&]:opacity-100">
    <div class="flex flex-wrap items-center justify-between gap-3 rounded-t-3xl border border-ink/10 bg-white/80 p-4 sm:p-7"><div class="min-w-0"><p class="mb-2 text-[11px] font-extrabold tracking-[2px] text-steel sm:mb-4">PROCESO DE RESOLUCIÓN</p><h2 id="solutionTitle" class="text-xl font-bold sm:text-2xl">Resolviendo el problema</h2></div><div class="whitespace-nowrap rounded-full bg-[#EEF6F2] px-3 py-2 text-[11px] font-bold text-[#50856E]">● Completado</div></div>
    <div class="rounded-b-3xl xl:max-h-[calc(100vh-230px)] xl:overflow-y-auto border border-t-0 border-ink/10 bg-white/80 p-4 sm:p-7">
      <div class="mb-6 border-b border-ink/10 pb-6"><h3 class="mb-4 text-[13px] font-bold">1. Función objetivo</h3><div id="objectivePreview" class="rounded-xl bg-ink p-4 font-mono text-white">MAX Z = 3x₁ + 5x₂</div></div>
      <div class="mb-6 border-b border-ink/10 pb-6"><h3 class="mb-4 text-[13px] font-bold">2. Restricciones ingresadas</h3><div id="constraintsPreview" class="grid gap-2 font-mono text-xs"></div></div>
      <div id="graphicSection" class="mb-6 hidden border-b border-ink/10 pb-6"><h3 class="mb-4 text-[13px] font-bold">3. Región factible</h3><div id="graphicOutput" class="overflow-x-auto rounded-2xl bg-[#F6F9FA] p-2"></div><p class="mt-2 text-[11px] text-[#597081] sm:hidden">Desliza horizontalmente para ver toda la gráfica.</p></div>
      <div class="mb-6 border-b border-ink/10 pb-6"><h3 id="stepsTitle" class="mb-4 text-[13px] font-bold">3. Desarrollo del método</h3><div id="stepsOutput" class="grid grid-cols-[minmax(0,1fr)] gap-3"></div></div>
      <div class="rounded-2xl bg-ice p-6"><span class="block text-[11px] font-extrabold tracking-widest">RESULTADO</span><strong id="finalAnswer" class="my-2 block text-3xl">Z = 0</strong><p id="finalDescription" class="break-words text-xs text-[#597081]">Resultado del modelo enviado al backend.</p></div>
      <button id="editDataBtn" type="button" class="mt-4 min-h-11 w-full rounded-xl bg-mist px-4 py-3 text-xs font-extrabold text-ink transition hover:bg-ice xl:hidden">↑ Editar los datos del problema</button>
    </div>
  </section>`;
}

function calculatorTemplate() {
  return `<section id="calculator" class="order-1 w-full min-w-0 max-w-[470px] self-center rounded-[31px] border border-ink/10 bg-white/90 p-4 shadow-2xl transition-[max-width,transform] duration-700 ease-[cubic-bezier(.22,.8,.25,1)] sm:p-6 md:max-w-[640px] xl:order-2 xl:max-w-[470px] xl:self-auto xl:[.show-results_&]:max-w-[420px] short:p-3">
    <div class="flex items-center justify-between px-1 pb-5 short:pb-3"><div><p class="mb-1 text-[11px] font-extrabold tracking-widest text-steel">ENTRADA DEL PROBLEMA</p><h2 id="calcTitle" class="text-lg font-bold">Método Simplex</h2></div><div class="size-3 rounded-full bg-[#7EB7A4] shadow-[0_0_0_5px_rgba(126,183,164,.13)]"></div></div>
    <div id="objectiveMode" class="grid grid-cols-[1fr_1fr_.7fr] gap-2 py-3 short:gap-1 short:py-2"><button class="mode rounded-xl bg-ice py-3 text-xs font-extrabold text-ink" data-mode="max">MAX</button><button class="mode rounded-xl bg-mist py-3 text-xs font-extrabold text-[#597081]" data-mode="min">MIN</button><button class="clear-entry rounded-xl bg-[#F8EEEE] py-3 text-xs font-extrabold text-[#9A4E4E]" id="clearEntry">AC</button></div>
    <div id="standardEditor" class="grid gap-2 short:gap-1"><label class="text-[11px] font-extrabold text-[#597081]" for="variableCount">Cantidad de variables</label><input id="variableCount" class="w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="20" value="2"><label class="mt-2 text-[11px] font-extrabold text-[#597081]" for="objectiveCoefficients">Coeficientes de Z</label><input id="objectiveCoefficients" class="w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="text" value="3,5" placeholder="Ejemplo: 3,5"><p class="-mt-1 mb-1 text-[11px] text-[#597081]">Escríbelos en orden: x1, x2, x3...</p><label class="text-[11px] font-extrabold text-[#597081]" for="constraintCount">Cantidad de restricciones</label><input id="constraintCount" class="w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="20" value="2"></div>
    <div id="constraintEditor" class="mt-5 grid gap-2 pr-1 xl:max-h-80 xl:overflow-y-auto"></div>
    <div id="transportEditor" class="mt-5 hidden grid gap-3"><div class="grid grid-cols-2 gap-2"><label class="text-[11px] font-extrabold text-[#597081]">Orígenes<input id="originCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="10" value="3"></label><label class="text-[11px] font-extrabold text-[#597081]">Destinos<input id="destinationCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="10" value="4"></label></div><div id="transportMatrix" class="rounded-2xl border border-ink/10 bg-mist/50 p-2"></div><p class="text-[11px] text-[#597081]">Ingresa costos, oferta y demanda.</p></div>
    <div id="assignmentEditor" class="mt-5 hidden grid gap-3">
      <div class="rounded-2xl border border-[#D9C8EC] bg-[#F8F4FC] p-3 text-xs leading-5 text-[#76539A]">
        <strong class="block">Objetivo: minimizar el costo total</strong>
        <span>Kuhn-Munkres requiere una matriz de costos. Puede ser cuadrada o rectangular; las celdas ficticias se agregan automáticamente.</span>
      </div>
      <div class="grid grid-cols-2 gap-2"><label class="text-[11px] font-extrabold text-[#597081]">Trabajadores<input id="assignmentRowCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="20" value="3"></label><label class="text-[11px] font-extrabold text-[#597081]">Tareas<input id="assignmentColumnCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="20" value="3"></label></div>
      <div id="assignmentMatrix" class="rounded-2xl border border-ink/10 bg-mist/50 p-2"></div>
      <p class="text-[11px] text-[#597081]">Cada celda representa un costo no negativo. Escribe <strong>X</strong> para prohibir una asignación; se mostrará como ∞ en el procedimiento y los resultados.</p>
    </div>
    <div id="flowEditor" class="mt-5 hidden grid gap-3">
      <div class="grid grid-cols-2 gap-2"><label class="text-[11px] font-extrabold text-[#597081]">Nodos<input id="flowNodeCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="2" max="20" value="4"></label><label class="text-[11px] font-extrabold text-[#597081]">Aristas<input id="flowEdgeCount" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" max="40" value="5"></label></div>
      <div class="grid grid-cols-2 gap-2"><label class="text-[11px] font-extrabold text-[#597081]">Origen<input id="flowSource" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" value="1"></label><label class="text-[11px] font-extrabold text-[#597081]">Destino<input id="flowSink" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="1" value="4"></label></div>
      <label id="flowDemandLabel" class="text-[11px] font-extrabold text-[#597081]">Flujo requerido<input id="flowDemand" class="mt-1 w-full rounded-xl border border-ink/10 bg-[#F8FAFB] px-3 py-2.5 text-sm" type="number" min="0" step="any" value="10"></label>
      <div id="flowEdges" class="grid gap-2 pr-1 xl:max-h-64 xl:overflow-y-auto"></div>
      <p class="text-[11px] text-[#597081]">Cada arista se define como origen, destino, capacidad y costo.</p>
    </div>
    <div class="mt-3 grid grid-cols-2 gap-2"><button id="addConstraint" class="rounded-xl bg-ice py-3 text-xs font-extrabold text-ink" type="button">Actualizar campos</button><button id="solveBtn" class="rounded-xl bg-ink py-3 text-xs font-extrabold text-white" type="button">Resolver <span>→</span></button></div><p id="formError" class="min-h-5 mt-3 text-xs leading-5 text-[#9A4E4E]" role="alert"></p>
  </section>`;
}
