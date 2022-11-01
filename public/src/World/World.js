import * as THREE from "three";
import { ColladaLoader } from "https://cdn.jsdelivr.net/npm/three@0.146/examples/jsm/loaders/ColladaLoader.js";
import { createRenderer } from "./systems/renderer";
import { createScene } from "./components/scene";
import { createCamera } from "./components/camera";

let container;
let camera, scene;
let elf, renderer, clock;

function init() {
    

    container = document.getElementById( 'scene-container' );

    camera = createCamera();
    scene = createScene();
    renderer = createRenderer();
    clock = new THREE.Clock();


    // loading manager
    const loadingManager = new THREE.LoadingManager( function () {
        scene.add( elf );
    } );

    // collada
    const loader = new ColladaLoader( loadingManager );
    loader.load( './models/scene_mod.dae', function ( collada ) {
        elf = collada.scene;
    } );

    // light
    const ambientLight = new THREE.AmbientLight( 0xcccccc, 0.4 );
    scene.add( ambientLight );
    const directionalLight = new THREE.DirectionalLight( 0xffffff, 0.8 );
    directionalLight.position.set( 1, 1, 0 ).normalize();
    scene.add( directionalLight );

    container.append(renderer.domElement);

    window.addEventListener( 'resize', onWindowResize );
    
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

    requestAnimationFrame( animate );

    render();

}

function render() {

    const delta = clock.getDelta();

    if ( elf !== undefined ) {

        elf.rotation.z += delta * 0.5;

    }

    renderer.render( scene, camera );

}

 
export { init, animate };
