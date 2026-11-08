import { simplex } from "./simplex.js";
import { simplexRevisado } from "./simplexRevisado.js";
import { dualidad } from "./dualidad.js";
import { grafico } from "./grafico.js";
import { transporte } from "./transporte.js";
import { asignacion } from "./asignacion.js";
import { flujoMaximo } from "./flujoMaximo.js";
import { flujoCostoMinimo } from "./flujoCostoMinimo.js";

export const methodData = { simplex, simplexRevisado, dualidad, grafico, transporte, asignacion, flujoMaximo, flujoCostoMinimo };

export const methodIcons = {
  simplex: "components/icons/metodo_simplex.svg",
  simplexRevisado: "components/icons/metodo_simplex_revisado.svg",
  dualidad: "components/icons/metodo_dualidad.svg",
  grafico: "components/icons/metodo_grafico.svg",
  transporte: "components/icons/metodo_transporte.svg",
  asignacion: "components/icons/metodo_khun_munkres.svg",
  flujoMaximo: "components/icons/metodo_flujo_maximo.svg",
  flujoCostoMinimo: "components/icons/metodo_flujo_minimo.svg"
};

export function iconImg(id, cls = "size-full object-contain") {
  return `<img src="${methodIcons[id]}" alt="" class="${cls}" draggable="false">`;
}

export function endpointFor(method) {
  return methodData[method]?.endpoint;
}
