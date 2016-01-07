module.exports = function(app){

  app.get('/api/order', function (req, res) {
    res.json({
      objURL: "http://quick-and-easy.recipes/models/avocado.obj",
      mtlURL: "http://quick-and-easy.recipes/models/avocado.mtl",
      texURL: "http://quick-and-easy.recipes/models/avocado.jpg",
      name: "avocado"});
  });

  app.get('/', function (req, res) {
    res.render('home');
  });
};
