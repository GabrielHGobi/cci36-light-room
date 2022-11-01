import { WebGLRenderer } from '../../../vendor/three/build/three.module.js';

function createRenderer() {
  const renderer = new WebGLRenderer({antialias: false});
  renderer.setSize(window.innerWidth, window.innerHeight);
  return renderer;
}

export { createRenderer };