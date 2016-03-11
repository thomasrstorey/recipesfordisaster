var socket = io();

socket.on('instagram', function(data){
  updateFeed(data);
});

function updateFeed (data) {
    var data = JSON.parse(data).data;
    var ids = [];
    // get current feed
    var feed = document.getElementsByClassName("instagram-link");
    for (var i = 0; i != feed.length; i++){
      ids.push(feed[i].getAttribute("id"));
    }
    // compare to incoming data
    data.forEach(function(media){
      var exists = false;
      ids.forEach(function(id){
        if(id === media.id) exists = true;
      });
      if(!exists){
        pushToFeed(media);
      }
    });
}

function pushToFeed (datum) {
  var igdiv = document.getElementById('instagram');
  var a = document.createElement("a");
  a.setAttribute("href", datum.link);
  a.setAttribute("id", datum.id);
  a.className = "instagram-link";
  var img = document.createElement("img");
  img.setAttribute("src", datum.images.low_resolution.url);
  img.className = "instagram-img";
  a.appendChild(img);
  igdiv.insertBefore(a, igdiv.firstChild);
}

socket.on('order', function(data){
  var rl = document.getElementById('recipes-list');
  var a = document.createElement("a");
  a.setAttribute("href", "/recipes/"+data.title);
  a.className = "recipe-link"
  var entry = document.createElement("div");
  entry.className = "recipe-entry pushDown";
  var img = document.createElement("img");
  img.setAttribute("src", data.images[0]);
  img.className = "recipe-img";
  var txt = document.createElement("div");
  txt.className = "recipe-text";
  var h3 = document.createElement("h3");
  h3.innerHTML = data.title.replace(/\_/g, ' ');
  txt.appendChild(h3);
  entry.appendChild(img);
  entry.appendChild(txt);
  a.appendChild(entry);
  rl.insertBefore(a, rl.firstChild);
});
