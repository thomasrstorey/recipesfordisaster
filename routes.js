module.exports = function(app){

  var recipeater = require("./recipeaterbot/lib/recipeaterbot.js");
  var kitchen = require("./kitchen.js");
  var fs = require('fs');

  app.get('/api/order', function (req, res) {
    // res.json({
    //   objURL: "http://quick-and-easy.recipes/models/avocado.obj",
    //   mtlURL: "http://quick-and-easy.recipes/models/avocado.mtl",
    //   texURL: "http://quick-and-easy.recipes/models/avocado.sgi",
    //   name: "avocado"});

      //generate recipe
      var recipe = recipeater.generateRecipe();
      //feed recipe to python/blender
      kitchen.execute(recipe, function(err, urls){
        if(err){
          console.error(err);
          res.json({error: true, message: err.message});
        }
        //write recipe to file
        writeRecipeToFile(recipe);
        //send urls to app
        res.json(urls);
      });
  });

  app.get('/recipes/:id', function (req, res){
    var id = req.params.id;
    var recipes = JSON.parse(fs.readFileSync('recipes.json', 'utf8'));
    var data = recipes[id];
    res.render('recipe', data);
  });

  app.get('/', function (req, res) {
    res.render('home');
  });

  var writeRecipeToFile = function (recipe) {
    var recipes = JSON.parse(fs.readFileSync('recipes.json'));
    var imgp = '/images/';
    recipes.push({ingredients: recipe.ingredients,
              steps:recipe.steps, images:[
              imgp+recipe.title.replace(/ /g, '_')+'1.jpg',
              imgp+recipe.title.replace(/ /g, '_')+'2.jpg',
              imgp+recipe.title.replace(/ /g, '_')+'3.jpg']});
    fs.writeFileSync('./recipes.json', JSON.stringify(recipes, null, 2));
    //TODO: Trigger page update (sockets)
  }
};
