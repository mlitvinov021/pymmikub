const socket = io.connect('http://' + document.domain + ':' + location.port);

// Join the game
socket.emit('join_game', { room: 'default' });



socket.on('game_update', function(data) {
    // Update game board and player hand
    document.getElementById('tiles').innerHTML = data.tiles.map(tile => {
        return `<span style="color:${tile[1]}">${tile[0]}</span>`;
    }).join(', ');
    
    const playerTiles = data.player_tiles[socket.id];
    document.getElementById('player-tiles').innerHTML = playerTiles.map(tile => {
        return `<span onclick="placeTile([${tile[0]},'${tile[1]}'])" style="color:${tile[1]}">${tile[0]}</span>`;
    }).join(', ');
    
    const elements = document.querySelectorAll('.combination');

    elements.forEach(element => {
        if (element.childElementCount === 0) {
            element.remove();
        }
    });

    const comboGrid = document.getElementById('combo-grid')

    const newDiv = document.createElement('div');
    newDiv.className = 'combination';
    newDiv.id = 'tiles'
    comboGrid.appendChild(newDiv);
});

function placeTile(tile) {
    socket.emit('place_tile', { room: 'default', tile: tile });
}