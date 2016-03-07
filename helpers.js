module.exports = function(exphbs) {
  const self = {};

  self.renderHeaderNav = function (view, pages) {
    var nums = ['zero', 'one', 'two', 'three', 'four', 'five', 'six'];
    var out = '<div class="container"><div class="one-third column">'
    +'<div class="header-logo">'
    +'<h1><a href="/">Quick & <br> Easy Recipes</a></h1></div>'
    +'</div><div class="two-thirds column"><nav class="header-nav">';
    view = view.replace('pages/', '');
    pages.forEach(function(page, i, a){
      var coltype = nums[Math.ceil(12/a.length)];
      out+='<div class="'+coltype+' columns"><div class="nav-link">';
      if(page === view){
        out+='<h3 id="highlight">'+page+'</h3></div>';
      } else {
        out+='<a href="/'+page+'"><h3>'+page+'</a></h3></div>';
      }
      out+='</div>'
    });
    return out + '</nav></div></div>';
  };

  self.renderRecipesList = function (recipes) {
    var out = '<div id="recipes-list" class="row">';
    recipes.forEach(function(r){
      out += '<a class="recipe-link" href="/recipes/'+r.title+'">'
         +'<div class="recipe-entry">'
         + '<img class="recipe-img" src="'+r.images[0]+'"/><div class='
         + '"recipe-text"><h3>'+r.title.replace(/\_/g, ' ') + '</h3>'
         + '</div></div></a>';
    });
    return out + '</div>'
  };

  self.renderIngredients = function (ings) {
    var out = '';
    ings.forEach(function(ing){
      out+="<p>"+ing.quantity.num+" "+ing.quantity.unit.abb+" "
      +ing.name+"</p>";
    });
    return out;
  }

  return self;
}
