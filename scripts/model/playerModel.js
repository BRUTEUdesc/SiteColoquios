const mongoose = require('mongoose');


const playerSchema = {
    player: String,
    DiscID: String,
    ranking: Number
};

const playerModel = mongoose.model('player', playerSchema);

var methods = {};

methods.getModel = function(){
    return playerModel;
}

methods.getSchema = function(){
    return playerSchema;
}

module.exports =  methods;