const socket = io.connect('http://' + document.domain + ':' + location.port);

// Join the game
socket.emit('join_game', { room: 'default' });

socket.on('game_update', function(data) {
    // Update game board and player hand
    document.getElementById('tiles').innerHTML = data.tiles.join(', ');
    const playerTiles = data.player_tiles[socket.id];
    document.getElementById('player-tiles').innerHTML = playerTiles.map(tile => {
        return `<span onclick="placeTile(${tile})">${tile}</span>`;
    }).join(', ');
});

function placeTile(tile) {
    socket.emit('place_tile', { room: 'default', tile: tile });
}