const setSize = (container, camera, renderer) => {
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.left = width / - 2;
  camera.right = width / 2;
  camera.top = height / 2;
  camera.bottom = height / - 2;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
};

class Resizer {
    constructor(container, camera, renderer) {
        // set initial size on load
        setSize(container, camera, renderer);

        window.addEventListener('resize', () => {
            // set the size again if a resize occurs
            setSize(container, camera, renderer);
        });
    }
  }
  
  export { Resizer };