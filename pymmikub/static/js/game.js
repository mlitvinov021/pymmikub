const socket = io.connect('http://' + document.domain + ':' + location.port);

const room = 'default'

// Join the game
socket.emit('join_game', { room: room });


socket.on('game_update', function(data) {
    // Update game board and player hand
    document.getElementById('tiles').innerHTML = data[room].board.map(combo => {
        return combo.map(tile => {
            return `<span class="tile ${tile[1]}" style="color:${tile[1]}">${tile[0]}</span>`;
        }).join('');
    }).join('\n')

    const playerTiles = data[room].hand;
    document.getElementById('player-tiles').innerHTML = playerTiles.map(tile => {
        return `<span onclick="placeTile([${tile[0]},'${tile[1]}'], 0, 0)" class="tile ${tile[1]}" style="color:${tile[1]}">${tile[0]}</span>`;
    }).join('');
    
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


function placeTile(tile, combo, position) {
    socket.emit('place_tile', { room: room, tile: tile, combo: combo, position: position });
}