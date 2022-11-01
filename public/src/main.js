import { init, animate } from "./World/World.js";

// create the main function
function main() {
  // Get a reference to the container element
  const container = document.querySelector("#scene-container");

  init();
  animate();
}

// call main to start the app
main();
