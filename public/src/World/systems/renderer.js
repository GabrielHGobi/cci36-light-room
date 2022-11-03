import * as THREE from "three";

function createRenderer() {
  const renderer = new THREE.WebGLRenderer({antialias: false});
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.setSize( window.innerWidth, window.innerHeight );
  return renderer;
}

export { createRenderer };