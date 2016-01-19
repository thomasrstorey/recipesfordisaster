/*
 * recipeaterbot
 * https://github.com/thomasrstorey/recipeater
 *
 * Copyright (c) 2015 Thomas R Storey
 * Licensed under the MIT license.
 */

'use strict';

function Recipeater () {
  var _ = require('lodash');
  var pd = require("probability-distributions");
  var http = require("http");

  var self = {};
  var wares = require('./implements.js'),
     ings = require('./ingredients.js'),
     units = require('./units.js'),
     verbs = require('./verbs.js'),
     adverbs = require('./adverbs.js'),
     adjs = require('./adjectives.js');

  self.Kitchen = {
    ingredients : []
  };

  self.generateIngredientsList = function () {
    var numings = Math.ceil(_.sample(pd.rexp(150, 0.1)))+3;
    for(var i = 0; i != numings; i++) {
      // console.log("30");
      self.Kitchen.ingredients.push(getIngredient());
    }
    return self.Kitchen.ingredients;
  };

  self.generateStepsList = function () {
    var numsteps = Math.ceil(_.sample(pd.rexp(150, 0.1)))+3;
    var steps = '';
    var data = [];
    for (var i = 0; i != numsteps; i++){
      steps += generateSentence(data);
    }
    steps += "Serve " + _.sample(adjs) + ".";
    var title = generateTitle(data);
    var recipe = {title: title, steps : steps, data : data};
    return recipe;
  };

  var generateTitle = function (recipeObj) {
    var numIngs = _.random(1,3);
    var title = '';
    if(numIngs >= 1){
      var chunk = getTitleChunk(recipeObj);
      title += chunk.verb + " ";
      title += chunk.ing;
    }
    if(numIngs >= 2) {
      title += " with ";
      var chunk = getTitleChunk(recipeObj);
      if(_.random(1)) title += chunk.verb + " ";
      title += chunk.ing;
    }
    if(numIngs === 3) {
      title += " and ";
      var chunk = getTitleChunk(recipeObj);
      if(_.random(1)) title += chunk.verb + " ";
      title += chunk.ing;
    }
    function getTitleChunk (combos){
      var chunk = {};
      var combo = _.sample(recipeObj)[0];
      chunk.verb = _.capitalize(_.sample(combo.verbs).past);
      chunk.ing = _.capitalize(_.sample(combo.ingredients).name);
      return chunk;
    }
    return title;
  }

  var generateSentence = function (recipeObj) {
    var sentence = '';

    // sample 1+ verbs, but usually 1
    var vs = _.sample(verbs, Math.ceil(_.sample(pd.rexp(100, 0.8))));
    // sample 1+ ingredients, but usually 1
    var ings = _.sample(self.Kitchen.ingredients,
      Math.ceil(_.sample(pd.rexp(100, 0.8))));
    // sample 0+ tools
    var tools = _.sample(wares.tools,
      Math.abs(Math.floor(_.sample(pd.rnorm(100, 0, 2)))));
    // sample 0+ containers
    var containers = _.sample(wares.cookware,
      Math.abs(Math.floor(_.sample(pd.rnorm(100, 0, 2)))));
    // combine verbs and ingredients
    var combos = [];
    while(vs.length > 0 && ings.length >0){
      //   pull 1+ verbs and ingredients, combine
      var cObj = {verbs:[],
              ingredients:[],
              toolQualifier:false,
              containerQualifier:false,
              stateQualifier:false};
      var vlimit = _.random(1, 3);
      var ilimit = _.random(1, 3);
      for(var i = 0; i != vlimit; i++){
        if(vs.length > 0){
          cObj.verbs.push(vs.pop());
        }
      }
      for(var i = 0; i != ilimit; i++){
        if(ings.length > 0){
          cObj.ingredients.push(ings.pop());
        }
      }
      combos.push(cObj);
    }
    //   if only one of the lists is empty, attach remaining in list to last
    //   combination
    if(vs.length !== ings.length){
      if(vs.length){
        for(var i = 0; i < vs.length; i++){
          combos[combos.length-1].verbs.push(vs.pop());
        }
      } else if(ings.length){
        for(var i = 0; i < ings.length; i++){
          combos[combos.length-1].ingredients.push(ings.pop());
        }
      }
    }

    // now we have an array of verb-ingredient combinations
    // [
    //   {verbs:[verbObj,verbObj], ingredients:[ingredientObj,ingredientObj
    //   ,ingredientObj]} -> "verb and verb the ing, ing and ing together"
    //   {verbs:[verbObj], ingredients:[ingredientObj]} -> "verb the ing"
    // ] -> "verb and verb the ing, ing and ing together, and verb the ing"

    // if tools
    if(tools.length){
    //  attach a tool qualifier to the front or back of a verb-ing combination
    //     pick 1+ tools from list
    //     "with|using a {tool}[[,{tool}] and a {tool}]"
    //   if any remaining, make another qualifier and attach to another
    //   combination, repeat until out of tools or every combination has a
    //   qualifier
      while(tools.length){
        // console.log('tools loop');
        var tlimit = _.random(1,3);
        var toolQualifier = {tools: [],
          article: Math.random()<0.5?"with":"using"};
        for(var i = 0; i != tlimit; i++){
          // console.log("149");
          if(tools.length > 0)toolQualifier.tools.push(tools.pop());
        }
        var c = _.sample(_.filter(combos,
          function(o){return o.toolQualifier===false}));
        // console.dir(c);
        if (c) c.toolQualifier = toolQualifier;

      }
    }


    // if containers
    if(containers.length){
      //   attach a container qualifier to the front or back of a verb-ing
      // combination depending on which article is picked
      //   if 'in'
      //     "in a {container}" + combination
      //   else if 'into'
      //     combination + 'into a {container}'
      while(containers.length){
        // console.log('containers loop');
        var article = Math.random()<0.5?"in":"into";
        var containerQualifier = {container: containers.pop(),
                          article: article};
        var c = _.sample(_.filter(combos,
          function(o){return o.containerQualifier===false}));
        // console.dir(c);
        if(c) c.containerQualifier = containerQualifier;
      }
    }

    // optionally attach state qualifier to the end of each combination
    // "verb and verb the ing, ing and ing together [until {adj}|for
    // {duration}|to {temperature}|(none)], and verb the ing
    // [until {adj}|for {duration}|to {temperature}|(none)]"
    combos.forEach(function(c){
      if(Math.random()<0.33){
        var state = _.random(0, 3);
        if(state === 0){
          c.stateQualifier = getStateQualifier();
        } else if (state === 1) {
          c.stateQualifier = getDurationQualifier();
        } else if( state === 2) {
          c.stateQualifier = getTemperatureQualifier();
        } else if (state === 3) {
          c.stateQualifier = null;
        }
      }
    });
    // console.dir(combos,{depth:null});
    recipeObj.push(combos);
    sentence = renderSentence(combos);
    return sentence;
  }


  var sendToKitchen = function (recipeObj, options, cb) {
    var recipe = JSON.stringify(recipeObj);
    var picurl = '';
    options.headers = {
      "Content-Type" : "application/x-www-form-urlencoded",
      "Content-Length" : recipe.length
    };
    var req = http.request(options, function(res){
      res.setEncoding('utf8');
      res.on('data', function (chunk) {
        picurl += chunk;
      });
      res.on('end', function () {
        return cb(null, chunk);
      });
    });
    req.on('error', function(e) {
      console.log('kitchen failed: ' + e.message);
      return cb(e, null);
    });
    req.write(recipe);
    req.end();
  }

  var getTimeRange = function(){
    var start = Math.ceil(_.sample(pd.rnorm(100, 10, 5)));
    var end = start + Math.ceil(_.sample(pd.rnorm(100, 5, 2)));
    return start + "-" + end;
  }

  var getDurationQualifier = function (){
    var units = ['femtoseconds', 'picoseconds', 'milliseconds', 'seconds',
    'minutes', 'hours', 'days', 'weeks', 'months', 'years', 'decades',
    'centuries', 'eons'];
    return "for " + getTimeRange()+" "+
    _.sample(pd.sample(units, 12, false,
      [1, 1, 1, 4, 8, 6, 1, 1, 1, 1, 1, 1, 1]));
  };

  var getStateQualifier = function (){
    return "until "+_.sample(adjs);
  };

  var getTemperatureQualifier = function (){
    return "to "+_.random(180, 500)+"° F";
  };

  var renderSentence = function (combos){
    var out = '';

    combos.forEach(function(combo, i, arr){
      var toolqstr = '';
      var contqstr = '';
      var verbstr = '';
      var ingstr = '';
      if(combo.toolQualifier){
        var tools = combo.toolQualifier.tools;
        var qualstr = combo.toolQualifier.article+" a";
        while(tools.length){
          // console.log('second tools loop');
          var tool = tools.pop().toLowerCase();
          if(!tools.length && qualstr.length > 7){
            qualstr+="nd a"
          }
          if(isVowel(tool[0])){
            qualstr+="n";
          }
          qualstr += " "+tool+", a";
        }
        toolqstr+=qualstr.slice(0, -3);
      }
      combo.verbs.forEach(function(verb, i, arr){
        if(i!==arr.length-1 && arr.length >2){
          if(i!==0) verbstr+=' ';
          verbstr+=verb.present.toLowerCase()+',';
        } else if(arr.length!==1 && i !== 0){
          verbstr+=' and '+verb.present.toLowerCase();
        } else {
          verbstr += verb.present.toLowerCase();
        }
      });
      combo.ingredients.forEach(function(ing, i, arr){
        if(i!==arr.length-1 && arr.length >2){
          if(i!==0) ingstr+=' ';
          ingstr+=ing.name.toLowerCase()+',';
        } else if(arr.length!==1 && i !== 0){
          ingstr+=' and '+ing.name.toLowerCase();
        } else {
          ingstr += ing.name.toLowerCase();
        }
      });
      if(combo.containerQualifier){
        var containerQ = combo.containerQualifier;
        contqstr += containerQ.article+" a";
        if(isVowel(containerQ.container[0])){
          contqstr+='n'
        }
        contqstr+=' '+containerQ.container.toLowerCase();
      }
      var toolQposition = _.random(0, 1);
      var contQposition = _.random(0, 1);
      out+=verbstr+' the '+ingstr;
      if(combo.toolQualifier){
        if(toolQposition){
          out = toolqstr +", " + out;
        } else {
          out+=" "+toolqstr;
        }
      }
      if(combo.containerQualifier){
        if(combo.containerQualifier.article === 'into'){
          out+=" "+contqstr;
        } else {
          if(contQposition){
            out+=" "+contqstr;
          } else {
            out = contqstr+", "+out;
          }
        }
      }
     if(combo.stateQualifier) out += " "+combo.stateQualifier;
      if(i !== arr.length-1) out += ", and ";
    });
    return _.capitalize(out+". ");
  };

  var isVowel = function(char){
    return _.includes(['a','e','i','o','u','y','A','E','I','O','U','Y'], char);
  };

  self.writeIngredientList = function ( style ) {
    var out = '';
    var ilist = self.Kitchen.ingredients;
    if(style === "html"){

    } else if(style === 'md'){

    } else {
      // plaintext
      ilist.forEach(function(ingredient, index){
        var quantity = ingredient.quantity;
        out += quantity.num+" "+quantity.unit.abb+" "+ingredient.name;
        out += Math.random()<0.1 ? ", "+ingredient.state+"\n" : "\n";
      });
    }
    return out;
  };

  var getIngredient = function () {
    var ingredient = {};
    ingredient.type = _.sample(_.keys(ings));
    ingredient.name = _.sample(ings[ingredient.type]);
    ingredient.quantity = {
      unit: _.sample(units),
      num: Math.ceil(_.sample(pd.rexp(150, 0.1)))
    };
    ingredient.state = _.sample(adjs);
    return ingredient;
  };

  return self;
};

module.exports = Recipeater();
