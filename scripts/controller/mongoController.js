const mongoose = require('mongoose');
const playerModel = require('../model/playerModel');
var db = mongoose.connection;

mongoose.connection.on('connected', () =>{
    console.log('connected to mongodb');
});


var methods = {};

methods.connect = function(){
    mongoose.connect(config.connection, {
        useNewUrlParser: true,
        useUnifiedTopology: true
    });
}


methods.getLeaderboard = function (id) {
    var player = mongoose.model('player', playerModel.getSchema);
    
    // define an empty query document
    const query = {};
    // sort in descending (-1) order by length
    const sort = { length: -1 };
    const limit = 3;
    const cursor = player.find(query).sort(sort).limit(limit);
    await cursor.forEach(console.dir);
};

module.exports = methods;