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
            return comb(comboIndex + 1, placer(comboIndex + 1, 0));
        }

        return comb(comboIndex + 1, placer(comboIndex + 1, 0) + tiles);
    }).join('');

    // Update player hand
    document.getElementById('player-tiles').innerHTML = placer(0, 0) + data[room].hand.map((tileInfo, tileIndex) => {
        const newTile = tile(tileInfo);
        const newPlacer = placer(0, tileIndex + 1);
        return newTile + newPlacer;
    }).join('');
});


function allowDrop(ev) {
    ev.preventDefault();
    ev.target.style.width = '50px';
}


function drag(ev) {
    ev.dataTransfer.setData("id", ev.target.id);
    ev.dataTransfer.setData("origin", ev.target.parentElement.dataset.combo);
}


function leave(ev) {
    ev.target.style.width = "5px";
}


function drop(ev) {
    ev.preventDefault();

    const tileId = ev.dataTransfer.getData("id");
    const origin = parseInt(ev.dataTransfer.getData("origin"));
    const target = parseInt(ev.target.dataset.combo);
    const position = parseInt(ev.target.dataset.position);

    ev.target.style.width = "5px";

    placeTile(tileId, origin, target, position);
}


function placeTile(tileId, origin, target, position) {
    const tileNumber = document.getElementById(tileId).dataset.tileNumber;
    const tileColor = document.getElementById(tileId).dataset.tileColor;

    socket.emit('place_tile', { room: room, tile: {id: tileId, number: parseInt(tileNumber), color: tileColor, is_new: true}, origin: origin, target: target, position: position });
}


function tile(tileInfo) {
    var tile = document.createElement('span');
    tile.setAttribute('id', tileInfo.id);
    tile.setAttribute('draggable', 'true');
    tile.setAttribute('ondragstart', 'drag(event)');
    tile.setAttribute('class', 'tile ' + tileInfo.color + ' ' + (tileInfo.is_new ? 'new' : ''));
    tile.setAttribute('data-tile-number', tileInfo.number);
    tile.setAttribute('data-tile-color', tileInfo.color);
    tile.setAttribute('data-tile-isnew', tileInfo.is_new);
    tile.appendChild(document.createTextNode(tileInfo.number));
    return tile.outerHTML;
}


function placer(comboIndex, position) {
    var placer = document.createElement('span');
    placer.setAttribute('ondrop', 'drop(event)');
    placer.setAttribute('ondragover', 'allowDrop(event)');
    placer.setAttribute('ondragleave', 'leave(event)');
    placer.setAttribute('class', 'placer');
    placer.setAttribute('data-combo', comboIndex);
    placer.setAttribute('data-position', position);
    placer.appendChild(document.createTextNode(`\u00a0`));
    return placer.outerHTML;
}


function comb(comboIndex, content) {
    var combo = document.createElement('div');
    combo.setAttribute('class', 'combination');
    combo.setAttribute('data-combo', comboIndex);
    combo.innerHTML = content;
    return combo.outerHTML;
}