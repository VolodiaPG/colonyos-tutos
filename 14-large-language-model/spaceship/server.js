var express = require('express');
var cors = require('cors'); // Import cors
var app = express();

// Enable CORS for all requests
app.use(cors());
app.use(express.static('public'));

console.log("starting");
var server = app.listen(1111);

