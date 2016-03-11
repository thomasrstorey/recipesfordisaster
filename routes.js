module.exports = function(app, hbs, io){

  var https = require('https');
  var recipeater = require("./recipeaterbot/lib/recipeaterbot.js");
  var kitchen = require("./kitchen.js")(io);
  var fs = require('fs');
  var ig = require('instagram-node').instagram();
  var secrets = require('./secrets.js');

  // Instagram Shit ===========================================================

  var interval;
  ig.use(secrets);
  var redirect_uri = 'http://quick-and-easy.recipes/handleauth';
  var access_token = '';

  // This is where you would initially send users to authorize
  app.get('/authorize_user', function(req, res) {
    if(access_token.length <= 0){
      ig.use(secrets);
      res.redirect( ig.get_authorization_url(redirect_uri) );
    }
  });

  // This is your redirect URI
  app.get('/handleauth', function(req, res) {
    ig.authorize_user(req.query.code, redirect_uri, function(err, result) {
      if (err) {
        console.error(err);
        res.send("Didn't work");
      } else {
        access_token = result.access_token;
        interval = setInterval(getFeed, 30000, access_token);
        console.log(access_token);
        res.send('You made it!!');
      }
    });
  });

  var getFeed = function (at) {
    if(at.length > 0){
      var body = '';
      https.get(
        'https://api.instagram.com/v1/users/self/media/recent/?access_token='
        +at, function (res) {
          console.log("FEED STATUS: " + res.statusCode);
          res.resume();
          res.on('data', function (chunk){
            if(chunk.length) body+=chunk;
          });
          res.on('error', function (err) {
            console.error(err);
            cb(err, null);
          })
          res.on('end', function () {
            body = body.slice(0); // XXX: REMOVE 'UNDEFINED' AT BEGINNING
            io.emit('instagram', body);
          });
        });
    }
  };

  // EntreAR App API ==========================================================

  app.get('/api/order', function (req, res) {
      // get decide text
      var d = req.query.d;
      //generate recipe
      var recipe = recipeater.generateRecipe();
      recipe.title += " " + d;
      //feed recipe to python/blender
      kitchen.execute(recipe, function(err, urls, serve){
        if(err){
          console.error(err);
          res.json({error: true, message: err.message});
        }
        // write recipe to file
        // broadcast update to sockets
        (function(recipe){
          serve(function(err){
            if(err){
              console.error(err)
            } else {
              io.emit('order', writeRecipeToFile(recipe));
            }
          });
        })(recipe);
        //send urls to app
        res.json(urls);
      });
  });

  // AJAX =====================================================================

  app.get('/more', function (req, res){
    // get next ten recipes
    // return their JSON data
    var start = req.query.start;
    var num = req.query.num;
    res.json(getRecipes(start, num));
  });

  // GET pages ================================================================

  app.get('/recipes/:id', exposeTemplates, function (req, res){
    var id = req.params.id;
    var recipes = JSON.parse(fs.readFileSync('recipes.json', 'utf8'));
    var data = {};
    for(var i = 0; i != recipes.length; i++){
      if(recipes[i].title === id){
        data = recipes[i];
        data.title = data.title.replace(/\_/g, ' ');
        break;
      }
    }
    res.render('recipe', data);
  });

  app.get('/*', exposeTemplates, function (req, res, next) {
    console.log("PATH: " + req.path);
    if(req.path.match(/\.\w+$/) !== null){
      next();
    } else {
      page = req.path.replace(/\//g, '');
      page = page.length ? "pages/"+page : 'home';
      if(page === 'home'){
        res.locals.recipes = getRecipes(0, 5);
      } else if (page === 'pages/recipes') {
        console.log("RECIPES!");
        res.locals.recipes = getRecipes(0, 10);
      }
      if(page === 'home'){
        if(access_token.length > 0){
          ig.use({access_token: access_token});
          ig.user_self_media_recent(function(err, medias, pagination, remaining, limit) {
            if(err){
              console.error(err);
            } else {
              res.locals.medias = medias;
              res.locals.access_token = access_token;
              res.render(page);
            }
          });
        } else {
          res.render(page);
        }
      } else {
        res.render(page);
      }
    }


  });

  // Utilities ================================================================

  var writeRecipeToFile = function (recipe) {
    var recipes = JSON.parse(fs.readFileSync('recipes.json'));
    var imgp = '/images/';
    var formatted = {title: recipe.title.replace(/ /g, '_'),ingredients: recipe.ingredients,
              steps:recipe.steps, images:[
              imgp+recipe.title.replace(/ /g, '_')+'1.jpg',
              imgp+recipe.title.replace(/ /g, '_')+'2.jpg',
              imgp+recipe.title.replace(/ /g, '_')+'3.jpg']};
    recipes.push(formatted);
    fs.writeFileSync('./recipes.json', JSON.stringify(recipes, null, 2));
    return formatted;
  };

  function getRecipes (start, num) {
    var recipes = JSON.parse(fs.readFileSync('recipes.json', 'utf8'));
    var out = [];
    for(var i = recipes.length-1-start; i > recipes.length-1-start-num; i--){
      if(recipes[i] !== undefined) out.push(recipes[i]);
    }
    var more = false;
    if(out.length == num){
      more = true;
    }
    return {more: more, recipes : out};
  };

  function exposeTemplates (req, res, next) {
    hbs.getTemplates('views/pages')
    .then(function(pages){
      var out = Object.keys(pages).map(function(key){
        return key.replace('.hbs','')
      });
      if(out.length){
        res.locals.pages = out;
      }
      setImmediate(next);
    }).catch(next);
  };
};
