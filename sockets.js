module.exports = function (app, io) {

  io.on('connection', function(socket){
    socket.on('disconnect', function(){
    });
  });

};
