import * as THREE from "three";
import { ColladaLoader } from "https://cdn.jsdelivr.net/npm/three@0.146/examples/jsm/loaders/ColladaLoader.js";
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.146/examples/jsm/controls/OrbitControls.js';
import { createRenderer } from "./systems/renderer.js";
import { createScene } from "./components/scene.js";
import { createCamera } from "./components/camera.js";


let container, rect, camera, scene, orbit_controls, dae, renderer;
const mouse = new THREE.Vector2(), raycaster = new THREE.Raycaster();

function init() {
    
    container = document.getElementById( 'scene-container' );
    rect = container.getBoundingClientRect();
    camera = createCamera();
    scene = createScene();
    renderer = createRenderer();

    const loadingManager = new THREE.LoadingManager(() => {
        scene.add(dae);
    });
    const loader = new ColladaLoader( loadingManager );
    loader.load( './models/scene.dae', (collada) => {
        collada.scene.traverse( function(child) {
            if (child instanceof THREE.Mesh) 
                child.material = new THREE.MeshBasicMaterial({vertexColors: true });
        });
        dae = collada.scene;
    });

    orbit_controls = new OrbitControls( camera, renderer.domElement );
    orbit_controls.addEventListener( 'change', render );
    orbit_controls.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
    orbit_controls.dampingFactor = 0.08;
    orbit_controls.screenSpacePanning = false;
    orbit_controls.minDistance = 10;
    orbit_controls.maxDistance = 50;
    orbit_controls.maxPolarAngle = Math.PI / 2;

    container.append(renderer.domElement);

    window.addEventListener( 'resize', onWindowResize );
    window.addEventListener( 'click', onClick );
    
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function onClick(event) {

    event.preventDefault();
    mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = - ((event.clientY - rect.top) / container.clientHeight) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    const intersections = raycaster.intersectObjects( scene.children, true );
    if ( intersections.length > 0 ) {
        const object = intersections[ 0 ].object;
        console.log(object.name)
    }
}

function render() {
    renderer.render( scene, camera );
}

 
export { init, render };
