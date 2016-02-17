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

module.exports = function () {
  const spawn = require('child_process').spawn;
  const fs = require('fs');
  const crypto = require('crypto');
  const self = {};

  self.execute = function (recipe, cb) {
    // copy all of the ingredients to the kitchen - read and save in place.
    // delete them when the cooking process is over.
    var hash = crypto.createHash('md5').update(JSON.stringify(recipe));
    var workspace = "./counter"+hash.digest('hex')+"/";
    recipe.ingredients.forEach(function (ing,ingi,inga) {
      ing.files.forEach(function (file, filei, filea){
        copyFile("./objs/"+file, workspace+file);
      });
    });
    //execute each step - need to do recursively to ensure sequential
    consumeSteps(recipe.data[0], function(err){
      if(err){
        return cb(err);
      } else {
        //gather all the models together and shoot some photos
        prepare(workspace, function (err, urls) {
          if(err) return cb(err);
          clean(workspace);
          return cb(null, urls);
        });
      }
    });
    function consumeSteps (steps, cb) {
      if(steps.length > 0){
        var step = steps.shift();
        consumeVerbs(step.ingredients, step.verbs, function(err){
          if(err) return cb(err);
          return consumeSteps(steps);
        });
      } else {
        return cb();
      }
    };

    function consumeVerbs (ings, verbs, cb) {
      if(verbs.length > 0){
        var verb = verbs.shift();
        var args = ['--background', 'kitchen.blend', '--python',
                './actions/'+verb.present+'.py', '--'];
        ings.forEach(function (ing, ingi, inga) {
          args.push(workspace+ing.files[0]);
        });
        var blender = spawn('blender', args); //XXX:make sure env var is set!!
        blender.stdout.on('data', function(data){
          console.log(`kitchen: ${data}`);
        });
        blender.stderr.on('data', function(data){
          console.log(`kitchen error: ${data}`);
        });
        blender.on('close', function(code) {
          if(code < 1){
            return consumeVerbs(ings, verbs, cb);
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

  var serve = function (workspace) {
    //get list of files in workspace
    //run blender python script with list of all objs
    //move output images and obj + mtl + tex to a public directory
    //return {image URL Array, dish file URL object}
  };

  var clean = function (workspace) {
    //delete workspace directory and everything inside it
  }

  return self;
}
