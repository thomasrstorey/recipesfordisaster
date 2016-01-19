'use strict';

var recipeaterbot = require('../lib/recipeaterbot.js');

/*
  ======== A Handy Little Nodeunit Reference ========
  https://github.com/caolan/nodeunit

  Test methods:
    test.expect(numAssertions)
    test.done()
  Test assertions:
    test.ok(value, [message])
    test.equal(actual, expected, [message])
    test.notEqual(actual, expected, [message])
    test.deepEqual(actual, expected, [message])
    test.notDeepEqual(actual, expected, [message])
    test.strictEqual(actual, expected, [message])
    test.notStrictEqual(actual, expected, [message])
    test.throws(block, [error], [message])
    test.doesNotThrow(block, [error], [message])
    test.ifError(value)
*/

exports['awesome'] = {
  setUp: function(done) {
    // setup here
    done();
  },
  'no args': function(test) {
    test.expect(1);
    // tests here
    var recipe = recipeaterbot.generateRecipe();

    console.log(recipe.title);
    console.log(recipeaterbot.writeIngredientList());
    console.log(recipe.steps);
    console.log(recipe.ingredients);
    console.dir(recipe.data, {depth:null});
    test.equal(typeof recipe, 'object', 'should generate an array.');
    test.done();
  },
};
