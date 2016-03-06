var express = require('express');
var bodyParser = require('body-parser');
var exphbs  = require('express-handlebars');
var log = console.log;
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var hbs = exphbs.create({
  defaultLayout: 'main',
  extname: '.hbs',
  helpers: require('./helpers.js')(app, hbs)
});

app.use(bodyParser.urlencoded({extended: false}));
app.engine('.hbs', hbs.engine);
app.set('view engine', 'hbs');
app.use(express.static('views/static'));

require('./sockets.js')(app, io);

require('./routes.js')(app, hbs, io);

http.listen(8912, function(err){
  log("now listening on port 8912");
});
