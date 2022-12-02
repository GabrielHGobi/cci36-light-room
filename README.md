# Exame - CCI36 - Light Room

**Autores:** 

- Thiago Lopes de Araujo
- Gabriel Henrique Gobi

----------
## Introdução

<div style="text-align: justify">

O presente projeto se configura como uma aplicação desenvolvida a partir dos resultados alcançados no  [trabalho prévio sobre radiosidade](Projeto2_Radiosidade.md).

De posse do arcabouço apresentado, o objetivo do presente projeto corresponde no desenvolvimento de uma aplicação a qual forneca uma página web contendo uma cena (oriunda de um arquivo em formato `COLLADA` com importação para `Three.JS`) com possibilidade de interação com o usuário.

Tal interação ocorre de forma que todos os objetos contidos na cena apresentam um estado corrente sendo luminoso ou apagado (possuindo ou não emissão natural), o usuário, por sua vez, pode alterar o estado corrente apenas clicando no objeto, de forma que a iluminação da cena é então alterada e atualizada dinamicamente.

Além disso, fornece-se um _slider_ com possibilidade de se alterar o fator $\gamma$ de iluminação da cena de forma interativa com atualização sendo renderizada na página logo após o cálculo a ser efetuado.

Da descrição acima, observa-se que a construção da aplicação pode ser dividida em dois componenetes: 

- serviço `backend`, cuja função corresponde à computar a radiosidade dado os novos parâmetros definidos pelo usuário e fornecer os novos valores de emissão de luz dos objetos em cena, fornecendo tais resultados para a renderização da página;

- `frontend`, cuja função consiste em fornecer uma interface gráfica com possibilidade de alteração de parâmetros e visualização da cena atualizada.


## Backend

Inicialmente, implementou-se um conteiner docker com imagem de um sistema operacional Alfine Linux com suporte a python 3.8, com a posterior intalação do Node.js e execução de script em javascript a fim de implementar um servidor web (porta 8080) que processe o script python `radiosity.py`  desenvolvido no projeto anterior para cálculo da cena modificada. Tal processamento ocorre com alterações dos parâmetros de estado de iluminação dos objetos e fator $\gamma$ via requisições POST.

Método POST implementado em `index.js`:
```javascript
app.post('/', (req, res) => {
    var largeDataSet = [];
    
    console.log(req.body);

    // getting params from POST request
    var processParams = ['radiosity.py','./scene.dae']
    console.log(req.body.lumObjs);
    for (var i = 0; i < req.body.lumObjs.length; i++) {
        console.log(req.body.lumObjs[i])
        processParams.push(req.body.lumObjs[i]);
    }
    processParams.push("-gama");
    processParams.push(String(req.body.gama));

    console.log(processParams);
    // spawn new child process to call the python script
    const python = spawn('python3', processParams);

    // collect data from script
    python.stdout.on('data', function (data) {
        // console.log('Pipe data from python script ...');
        console.log(data);
        largeDataSet.push(data);
    });

    res.header('Content-Type', 'application/xml');

    // in close event we are sure that stream from child process is closed
    python.on('close', (code) => {
        // console.log(`child process close all stdio with code ${code}`);
        // send data to browser
        res.send(largeDataSet.join(''));
    });
});

app.listen(port, () => {
    // console.log(`Radiosity-server service listening on port ${port}!`)
})
```
`Dockerfile` implementado:
```dockerfile
FROM python:3.8-alpine

RUN apk --no-cache --update-cache add gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install numpy

WORKDIR /usr/src/app

RUN apk add --update nodejs npm

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "index.js" ]
```

Por fim, utilzou-se a plataforma `Google Kubernetes Engine (GKE)` a fim de realizar o deploy do container em cloud, o qual torna-se um servidor acessível na internet de endereço:

https://radiosity-server-iwcwk3spfq-rj.a.run.app


## Frontend

Incialmente, configura-se uma aplicação em `Three.JS` contendo os componentes usuais: `scene`, `camera` e `renderer`.

Em seguida, por meio do script `World.js`:

- instancia-se tais objetos com as respectivas chamadas `create`;
- define-se um controle de navegabilidade orbital, utilizando-se o objeto `OrbitControls`;
- obtém-se a cena COLLADA por meio da criação e manipulação do objeto `ColladaLoader`

Tais ações são efetuadas por meio da função `init`, a qual inclui também o gerenciamento de eventos `resize` e `click` responsáveis pela integração com o usuário.

Função `init` implementada em `World.js`:
```javascript
function init() {
    
    container = document.getElementById( 'scene-container' );
    rect = container.getBoundingClientRect();
    camera = createCamera();
    scene = createScene();
    renderer = createRenderer();

    const loadingManager = new THREE.LoadingManager(() => {
        scene.add(dae);
    });
    loader = new ColladaLoader( loadingManager );
    loader.load( './models/scene.dae', (collada) => {
        collada.scene.traverse( function(child) {
            if (child instanceof THREE.Mesh) 
                child.material = new THREE.MeshBasicMaterial({vertexColors: true });
        });
        dae = collada.scene;
    });

    orbit_controls = new OrbitControls( camera, renderer.domElement );
    orbit_controls.addEventListener( 'change', render );
    // an animation loop is required when 
    // either damping or auto-rotation are enabled
    orbit_controls.enableDamping = true; 
    orbit_controls.dampingFactor = 0.08;
    orbit_controls.screenSpacePanning = false;
    orbit_controls.minDistance = 10;
    orbit_controls.maxDistance = 50;
    orbit_controls.maxPolarAngle = Math.PI / 2;

    container.append(renderer.domElement);

    window.addEventListener( 'resize', onWindowResize );
    window.addEventListener( 'click', onClick );
}
```

O tratamento de um evento de clique do usuário é, portanto, feito por meio das funções `onClick` e `updateModel`, sendo, para eventos de clique na cena, utilizado raycaster de forma a intersectar o primeiro objeto selecionado (de forma a considerar a profundidade).

Após a seleção do objeto, muda-se o seu estado corrente (com ou sem emissão natural) enviando-se tal alteração via requisição POST para o servidor previamente descrito. 

Ressalta-se que, para eventos de clique no _slider_ referente ao valor $\gamma$ corrente, tal função envia o valor alterado via requisição POST similar.

Funções `onCLick` e `updateModel` implementadas em `World.js`:
```javascript
function onClick(event) {   
    event.preventDefault();
    mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = - ((event.clientY - rect.top) / container.clientHeight) * 2 + 1;
    raycaster.setFromCamera( mouse, camera );
    const interectableObjects = scene.children[0].children.filter(obj => {
        if (obj.name != 'Wall') return obj;
    })
    const intersections = raycaster.intersectObjects(interectableObjects , true );
    if ( intersections.length > 0 ) {
        const object = intersections[ 0 ].object;
        if (postData.lumObjs.find((name) => name == object.name)) {
            const index = postData.lumObjs.indexOf(object.name);
            const removedElement = postData.lumObjs.splice(index, 1);
        } else 
            postData.lumObjs.push(object.name);
        changed = true;
    }
    if (postData.gama != lastGama) {
        lastGama = postData.gama;
        changed = true;
    }
}

function updateModel(postData){
    axios.post('https://radiosity-server-iwcwk3spfq-rj.a.run.app', postData)
    .then(function (response) {
        saveColladaData(response.data)
    })
    .catch(function (error) {
        console.log(error);
    });
}
```

Por fim, ressalta-se que efetuou-se o _deploy_ da página web por meio do `Firebase`, obtendo-se uma página web acessível da internet via endereço:

https://cci36-light-room.web.app/

## Resultados

A corretude da implementação desenvolvida pode ser observada ao se acessar o link acima referente à página web, obtendo-se:

<img src=".//images/previous.png"  style="display: block; margin: 0 auto; width:900px;"/>

Após clicar na lâmpada, obtém-se:

<img src=".//images/lamp.png"  style="display: block; margin: 0 auto; width:300px;"/>

Após clicar no livro vermelho, obtém-se:

<img src=".//images/lamp_plus_redbook.png"  style="display: block; margin: 0 auto; width:300px;"/>

Que corresponde à composição da iluminação resultando dos dois objetos anteriorermente clicados apresentando emissão natural.

Em seguida, alterando-se $\gamma$ por meio do _slider_ para 0.4, obtém-se:

<img src=".//images/lamp_plus_redbook_newgamma.png"  style="display: block; margin: 0 auto; width:300px;"/>

Por fim, clicando-se novamente na lâmpada, obtém-se:

<img src=".//images/redbook_newgamma.png"  style="display: block; margin: 0 auto; width:300px;"/>

Observa-se que a lâmpada "apagou" (deixou de possuir emissão natural).

Além disso, observa-se os efeitos de luminosidade para as configurações condizentes com o esperado no que tange ao arcabouço teórico desenvolvido no trabalho anterior sobre radiosidade (observa-se, por exemplo, que o livro vermelho não ilumina os demais livros conforme esperado pela ortogonalidade do espectro de emissão).