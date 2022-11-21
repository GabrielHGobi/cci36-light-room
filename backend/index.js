const express = require('express');
var cors = require('cors');
const {spawn} = require('child_process');
const bp = require('body-parser');
const app = express()
const port = 8080

const corsOpts = {
    origin: '*',

    methods: [
        'POST',
    ],

    allowedHeaders: [
        'Content-Type',
    ],
};

app.use(cors(corsOpts));
app.use(bp.json())
app.use(bp.urlencoded({ extended: true }))


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