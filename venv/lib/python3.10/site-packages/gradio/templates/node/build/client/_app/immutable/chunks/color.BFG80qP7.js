import { w as ordered_colors } from "./2.ChNy08-U.js";
const get_next_color = (index) => {
  return ordered_colors[index % ordered_colors.length];
};
export {
  get_next_color as g
};
