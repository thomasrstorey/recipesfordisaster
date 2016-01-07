var express = require('express');
var bodyParser = require('body-parser');
var exphbs  = require('express-handlebars');
var log = console.log;
var app = express();
app.use(bodyParser.urlencoded({extended: false}));
app.engine('.hbs', exphbs({defaultLayout: 'main', extname: '.hbs'}));
app.set('view engine', 'hbs');
app.use(express.static('views/static'));

require('./routes.js')(app);

app.listen(8912, function(err){
  log("now listening on port 8912");
});
