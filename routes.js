module.exports = function(app, hbs, io){

  var recipeater = require("./recipeaterbot/lib/recipeaterbot.js");
  var kitchen = require("./kitchen.js");
  var fs = require('fs');
  var ig = require('instagram-node').instagram();
  var secrets = require('./secrets.js');

  // Instagram Shit ===========================================================

  ig.use(secrets);
  var redirect_uri = 'http://quick-and-easy.recipes/handleauth';
  var access_token = '';

  // This is where you would initially send users to authorize
  app.get('/authorize_user', function(req, res) {
    res.redirect( ig.get_authorization_url(redirect_uri) );
  });
  // This is your redirect URI
  app.get('/handleauth', function(req, res) {
    ig.authorize_user(req.query.code, redirect_uri, function(err, result) {
      if (err) {
        console.log(err.body);
        res.send("Didn't work");
      } else {
        access_token = result.access_token;
        ig.use({access_token: access_token});
        ig.add_user_subscription('http://quick-and-easy.recipes/instagram',
        function(err, result, remaining, limit){
          if(err) console.error(err);
          console.dir(result);
        });
        res.send('You made it!!');
      }
    });
  });

  app.get('/instagram', function (req, res){
    res.send(req.query['hub.challenge']);
  });


  app.post('/instagram', function (req, res){
    console.dir(req.body);
    // io.emit sub data
  });

  // EntreAR App API ==========================================================

  app.get('/api/order', function (req, res) {
      //generate recipe
      var recipe = recipeater.generateRecipe();
      //feed recipe to python/blender
      kitchen.execute(recipe, function(err, urls){
        if(err){
          console.error(err);
          res.json({error: true, message: err.message});
        }
        // write recipe to file
        // broadcast update to sockets
        io.emit('order', writeRecipeToFile(recipe));
        //send urls to app
        res.json(urls);
      });
  });

  // AJAX =====================================================================

  app.post('/contact', function (req, res){
    // send me an email
    // send response
  });

  app.post('/signup', function (req, res){
    // add email address to email list
    // send introductory email
    //send response
  });

  app.get('/more', function (req, res){
    // get next ten recipes
    // return their JSON data
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

  app.get('/*', exposeTemplates, function (req, res) {
    page = req.path.replace(/\//g, '');
    page = page.length ? "pages/"+page : 'home';
    if(page === 'home'){
      res.locals.recipes = getRecipes(0, 5);
    } else if (page === 'pages/recipes') {
      console.log("RECIPES!");
      res.locals.recipes = getRecipes(0, 10);
    }
    if(page === 'home' || page === 'community'){
      if(access_token.length > 0){
        ig.user_media_recent('user_id',
        function(err, medias, pagination, remaining, limit) {
          if(err){
            console.error(err);
          } else {
            res.locals.medias = medias;
          }
        });
      }
    }
    res.render(page);
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
    for(var i = recipes.length-(start+1); i > recipes.length-(start+1)-num; i--){
      out.push(recipes[i]);
    }
    return out;
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
