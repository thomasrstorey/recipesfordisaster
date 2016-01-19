/*
 * kitchen
 * https://github.com/thomasrstorey/recipesfordisaster
 *
 * Copyright (c) 2016 Thomas R Storey
 * Licensed under the MIT license.
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
        return(err);
      } else {
        var urls = { images:[], models:{} };
        //gather all the models together and shoot some photos
        // TODO: figure this shit out...i guess just run a script that
        // imports all the objs into the photo scene and renders some images
        // then look in a temp directory for a plaintext file with the urls
        // (which will have been previously written by python (alternatively
        // parse from spawn stdout)). Else return null + urls.
        return(null, urls);
      }
    });
    function consumeSteps (steps, cb) {
      if(steps.length > 0){
        var step = steps.shift();
        consumeVerbs(verbs, function(err){
          if(err) return cb(err);
          return consumeSteps(step);
        });
      } else {
        return cb();
      }
    };

    function consumeVerbs (verbs, cb) {
      if(verbs.length > 0){
        var verb = verbs.shift();
        var args = ['--background', 'kitchen.blend', '--python',
                './actions/'+verb.present+'.py', '--'];
        step.ingredients.forEach(function (ing, ingi, inga) {
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
            return consumeVerbs(verbs);
          } else {
            console.log("kitchen exploded!!");
            return(new Error(`blender exited with exit code ${code}`));
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

  return self;
}
