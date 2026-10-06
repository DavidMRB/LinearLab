import { simplex } from "./simplex.js";
import { simplexRevisado } from "./simplexRevisado.js";
import { dualidad } from "./dualidad.js";
import { grafico } from "./grafico.js";
import { transporte } from "./transporte.js";

export const methodData = { simplex, simplexRevisado, dualidad, grafico, transporte };

export function endpointFor(method) {
  return methodData[method]?.endpoint;
}
