import { OrthographicCamera } from "../../../vendor/three/build/three.module.js";

function createCamera() {
  const container = document.querySelector("#scene-container");
  const width = container.clientWidth;
  const height = container.clientHeight;
  const camera = new OrthographicCamera( width / - 2, width / 2, height / 2, height / - 2, 0);

  // move the camera back so we can view the scene
  camera.position.set(450, 100, 0);

  return camera;
}

export { createCamera };
