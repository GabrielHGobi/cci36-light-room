import * as THREE from "three";

function createScene() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('whitesmoke');
  return scene;
}

export { createScene };