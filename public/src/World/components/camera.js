import * as THREE from "three";

function createCamera() {
  const camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.1, 2000 );
  camera.position.set( 8, 10, 8 );
  camera.lookAt( 0, 3, 0 );
  return camera;
}

export { createCamera };
