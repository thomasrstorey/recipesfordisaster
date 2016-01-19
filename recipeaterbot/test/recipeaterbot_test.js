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
    var ings = recipeaterbot.generateIngredientsList();
    // console.dir(ings);
    console.log(recipeaterbot.generateStepsList().title);
    console.log(recipeaterbot.writeIngredientList());
    console.log(recipeaterbot.generateStepsList().steps);
    console.dir(recipeaterbot.generateStepsList().data, {depth:null});
    test.equal(typeof ings, 'object', 'should generate an array.');
    test.done();
  },
};
