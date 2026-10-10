import { simplex } from "./simplex.js";
import { simplexRevisado } from "./simplexRevisado.js";
import { dualidad } from "./dualidad.js";
import { grafico } from "./grafico.js";
import { transporte } from "./transporte.js";
import { asignacion } from "./asignacion.js";
import { flujoMaximo } from "./flujoMaximo.js";
import { flujoCostoMinimo } from "./flujoCostoMinimo.js";

export const methodData = { simplex, simplexRevisado, dualidad, grafico, transporte, asignacion, flujoMaximo, flujoCostoMinimo };

export function endpointFor(method) {
  return methodData[method]?.endpoint;
}
