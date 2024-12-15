const socket = io.connect('http://' + document.domain + ':' + location.port);
const room = 'default'

// Join the game
socket.emit('join_game', { room: room });


socket.on('game_update', function(data) {
    // Update game board
    console.log(data);
    document.getElementById('combo-grid').innerHTML = data[room].board.map((combo, comboIndex) => {
        const tiles = data[room].board[comboIndex].map((tileInfo, tileIndex) => {
            const newTile = tile(tileInfo);
            const newPlacer = placer(comboIndex + 1, tileIndex + 1);
            return newTile + newPlacer;
        }).join('');
        
        if (tiles.length === 0) {
            return comb(placer(comboIndex + 1, 0));
        }

        return comb(placer(comboIndex + 1, 0) + tiles);
    }).join('');

    // Update player hand
    document.getElementById('player-tiles').innerHTML = placer(0, 0) + data[room].hand.map((tileInfo, tileIndex) => {
        const newTile = tile(tileInfo);
        const newPlacer = placer(0, tileIndex + 1);
        return newTile + newPlacer;
    }).join('');
});


function placeTile(tileId, combo, position) {
    const tileNumber = document.getElementById(tileId).dataset.tileNumber;
    const tileColor = document.getElementById(tileId).dataset.tileColor;

    socket.emit('place_tile', { room: room, tile: [parseInt(tileNumber), tileColor], combo: combo, position: position });
}

// TODO: ability to change order of tiles in player hand, client-side
function shuffleHand(tileId, position) {
    console.log('tried to shuffle hand');
}


function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}


function allowDrop(ev) {
    ev.preventDefault();
    ev.target.style.width = '50px';
}


function drag(ev) {
    ev.dataTransfer.setData("id", ev.target.id);
}


function leave(ev) {
    ev.target.style.width = "5px";
}


function drop(ev) {
    ev.preventDefault();

    const tileId = ev.dataTransfer.getData("id");
    const combo = parseInt(ev.target.dataset.combo);
    const position = parseInt(ev.target.dataset.position);

    ev.target.style.width = "5px";

    if(combo === 0) {
        shuffleHand(tileId, position);
    }
    else {
        placeTile(tileId, combo, position);
    }
}


function tile(tileInfo) {
    var tile = document.createElement('span');
    tile.setAttribute('id', generateUUID());
    tile.setAttribute('draggable', 'true');
    tile.setAttribute('ondragstart', 'drag(event)');
    tile.setAttribute('class', 'tile ' + tileInfo[1]);
    tile.setAttribute('data-tile-number', tileInfo[0]);
    tile.setAttribute('data-tile-color', tileInfo[1]);
    tile.appendChild(document.createTextNode(tileInfo[0]));
    return tile.outerHTML;
}


function placer(combo, position) {
    var placer = document.createElement('span');
    placer.setAttribute('ondrop', 'drop(event)');
    placer.setAttribute('ondragover', 'allowDrop(event)');
    placer.setAttribute('ondragleave', 'leave(event)');
    placer.setAttribute('class', 'placer');
    placer.setAttribute('data-combo', combo);
    placer.setAttribute('data-position', position);
    placer.appendChild(document.createTextNode(`\u00a0`));
    return placer.outerHTML;
}


function comb(content) {
    var combo = document.createElement('div');
    combo.setAttribute('class', 'combination');
    combo.innerHTML = content;
    return combo.outerHTML;
}