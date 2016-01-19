module.exports=[
  Preheat ${implement} to ${temperature}.
  ${verb.transmuters} a ${volume} ${container}.
  In a ${adjective} ${container}, ${verb.transformers} ${ingredient} in the ${ingredient}.
  ${verb.transformers.present} in ${ingredient} and ${verb.transmuters} for ${duration}.
  ${verb.transformers.present} ${ingredient} and ${ingredient}.
  Heat to boiling, ${verb.transmuters.continuous} ${adverb}.
]



    Reduce heat to medium and cook and stir for 2 minutes more. Season with salt and pepper. Add frozen peas and carrots and cooked chicken. Pour into prepared casserole dish.
    In a medium bowl, mix together 2 cups flour, baking powder, and 3/4 teaspoon salt. Cut in shortening until mixture is crumbly. Stir in milk just until dough is moistened, then drop by spoonfuls onto chicken mixture.
    Bake at 450 degrees F (230 degrees C) for 12 to 15 minutes, or until biscuits are golden brown, and cooked on the bottom. This tends to bubble over so I place a piece of aluminum foil under the pan to catch the drips.

sample 1+ verbs
sample 1+ ingredients
sample 0+ implements

combine verbs and ingredients
  pull 1+ verbs and ingredients, combine
  if only one of the lists is empty, attach remaining in list to last combination

now we have an array of verb-ingredient combinations
[
  {verbs:[verbObj,verbObj], ingredients:[ingredientObj,ingredientObj,ingredientObj]} -> "verb and verb the ing, ing and ing together"
  {verbs:[verbObj], ingredients:[ingredientObj]} -> "verb the ing"
] -> "verb and verb the ing, ing and ing together, and verb the ing"

if tools
  attach a tool qualifier to the front or back of a verb-ing combination
    pick 1+ tools from list
    "with|using a {tool}[[,{tool}] and a {tool}]"
  if any remaining, make another qualifier and attach to another combination, repeat until out of tools or every combination has a qualifier

if containers
  attach a container qualifier to the front or back of a verb-ing combination depending on which article is picked
  if 'in'
    "in a {container}" + combination
  else if 'into'
    combination + 'into a {container}'

optionally attach state qualifier to the end of each combination
"verb and verb the ing, ing and ing together [until {adj}|for {duration}|to {temperature}|(none)], and verb the ing [until {adj}|for {duration}|to {temperature}|(none)]"
