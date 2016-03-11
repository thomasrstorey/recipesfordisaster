/*
 * kitchen
 * https://github.com/thomasrstorey/recipesfordisaster
 *
 * Copyright (c) 2016 Thomas R Storey
 * Licensed under the MIT license.


 the key question here is, what is the output of each script?
 editing and saving in-place means duplication in the case of
 scripts that combine ingredients.
 perhaps, don't make an obj until the end? consequtively edit a blend file.
 so for instance chop will take all the input objs, chop them one at a time,



 */

module.exports = function (io) {
  const spawn = require('child_process').spawn;
  const fs = require('fs');
  const crypto = require('crypto');
  const self = {};

  self.execute = function (recipe, cb) {
    // copy all of the ingredients to the kitchen - read and save in place.
    // delete them when the cooking process is over.
    var hash = crypto.createHash('md5').update(recipe.title).digest('hex');
    //execute each step - need to do recursively to ensure sequential
    consumeSteps(recipe.data, hash, function(err){
      if(err){
        return cb(err);
      } else {
        // call the callback
        var modelsURL = "http://quick-and-easy.recipes/models/";
        cb(null, {
          objURL: modelsURL+recipe.title.replace(/ /g, '_')+".obj",
          mtlURL: modelsURL+recipe.title.replace(/ /g, '_')+".mtl",
          texURL: modelsURL+recipe.title.replace(/ /g, '_')+"_color.jpg",
          name: recipe.title }, function(cb){
            // then gather all the models together and shoot some photos
            serve(hash, recipe.title, 'views/static/images/',
            'views/static/models/', function (err) {
              if(err){
                cb(err);
              } else {
                clean(hash);
                cb(null);
              }
            });
          });
      }
    }, true);

    function consumeSteps (steps, hash, cb, first) {
      if(steps.length > 0){
        var step = steps.shift();
        console.dir(step);
        consumeVerbs(step[0].ingredients, step[0].verbs, hash, function(err){
          if(err) return cb(err);
          return consumeSteps(steps, hash, cb);
        }, first);
      } else {
        return cb();
      }
    };

    function consumeVerbs (ings, verbs, hash, cb, first) {
      if(verbs.length > 0){
        var verb = verbs.shift();
        var args = ['-b', 'kitchen.blend', '--python',
                'actions/'+verb.present+'.py', '--', '-i'];
        if(first !== true){
          args[1] = 'dish'+hash+'.blend';
        }
        var inglist = '';
        ings.forEach(function (ing, ingi, inga) {
          if(ingi < inga.length -1){
            inglist+=ing.name.replace(/ /g, '_')+',';
          } else {
            inglist+=ing.name.replace(/ /g, '_')
          }
        });
        args.push(inglist);
        if(first === true){
          args = args.concat(['-o', 'dish'+hash]);
        }
        console.log(args.join(' '));
        var blender = spawn('blender', args, //XXX:make sure env var is set!!
        {cwd: "/home/thomas/recipesfordisaster"});
        // var blender = spawn('blender', args);
        blender.stdout.on('data', function(data){
          console.log(`kitchen: ${data}`);
        });
        blender.stderr.on('data', function(data){
          console.log(`kitchen error: ${data}`);
        });
        blender.on('close', function(code) {
          if(code < 1){
            return consumeVerbs(ings, verbs, hash, cb);
          } else {
            console.log("kitchen exploded!!");
            return cb(new Error(`blender exited with exit code ${code}`));
          }
        });
      } else {
        return cb();
      }
    };

  };

  var copyFile = function (src, dst, cb) {
    var rs = fs.createReadStream(src);
    var ws = fs.createWriteStream(dst);
    rs.on("error", function(err){
      done(err);
    });
    ws.on("error", function(err){
      done(err);
    });
    ws.on("close", function () {
      done();
    });
    rs.pipe(ws);
    function done(err){
      cb(err);
    }
  }

  var serve = function (hash, title, ipath, opath, cb) {
    //call export/render script on dish blend
    var args = ['-b', 'dish'+hash+'.blend', '--python',
            'render_and_export.py', '--', '-t',
            title.replace(/ /g, '_'), '-ip', ipath, '-op', opath];
    console.log(args.join(' '));
    var blender = spawn('blender', args,  //XXX:make sure env var is set!!
    {cwd: "/home/thomas/recipesfordisaster"});
    // var blender = spawn('blender', args);
    blender.stdout.on('data', function(data){
      console.log(`kitchen: ${data}`);
    });
    blender.stderr.on('data', function(data){
      console.log(`kitchen error: ${data}`);
    });
    blender.on('close', function(code) {
      if(code < 1){
        var modelsURL = "http://quick-and-easy.recipes/models/"
        return cb(null);
      } else {
        console.log("kitchen exploded!!");
        return cb(new Error(`blender exited with exit code ${code}`));
      }
    });
  };

  var clean = function (hash) {
    //delete dish blend
    fs.unlink('dish'+hash+'.blend', function(err){
      if(err) console.error(err);
      fs.unlink('dish'+hash+'.blend1', function(err){
        if(err) console.error(err);
      });
    });
  }

  return self;
};
