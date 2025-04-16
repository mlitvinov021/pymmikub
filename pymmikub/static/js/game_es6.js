class GameClient {
    constructor(room = 'default') {
        this.room = room;
        this.socket = io.connect(`http://${document.domain}:${location.port}`);
        this.endTurnButton = document.getElementById('end-turn');
        this.boardEl = document.getElementById('combo-grid');
        this.handEl = document.getElementById('player-tiles');
        this.currentPlayerEl = document.getElementById('current-player');
        this.remainingTilesEl = document.getElementById('remaining-tiles');
        this.playerListEl = document.getElementById('player-list');

        this.registerSocketEvents();
        this.socket.emit('join_game', { room: this.room });
    }

    registerSocketEvents() {
        this.socket.on('game_update', (data) => {
            console.log(data)
            const roomData = data[this.room];
            this.updateBoard(roomData.board);
            this.updateHand(roomData.hand.tiles);
            this.updatePlayerList(roomData.players, roomData.current_player);
            this.updateTiles(roomData.tiles)
            this.updateTurn(roomData.current_player, roomData.has_player_moved);
        });

        this.socket.on('turn_update', (data) => {
            this.updateTurn(data.current_player);
            this.updatePlayerList(data.players, data.current_player);
        });
    }

    updateBoard(board) {
        this.boardEl.innerHTML = '';
        board.forEach((comboInfo, comboIndex) => {
            const combo = document.createElement('div');
            combo.className = `combination ${comboInfo.is_valid ? 'valid' : 'invalid'}`;
            combo.dataset.combo = comboIndex + 1;
    
            combo.appendChild(this.createPlacer(comboIndex + 1, 0));
    
            comboInfo.tiles.forEach((tileInfo, tileIndex) => {
                combo.appendChild(this.createTile(tileInfo));
                combo.appendChild(this.createPlacer(comboIndex + 1, tileIndex + 1));
            });
    
            this.boardEl.appendChild(combo);
        });
    }
    
    updateHand(tiles) {
        this.handEl.innerHTML = '';
        this.handEl.appendChild(this.createPlacer(0, 0));
    
        tiles.forEach((tileInfo, tileIndex) => {
            this.handEl.appendChild(this.createTile(tileInfo));
            this.handEl.appendChild(this.createPlacer(0, tileIndex + 1));
        });
    }

    updateTiles(remainingTiles) {
        if (this.remainingTilesEl && remainingTiles !== null) {
            this.remainingTilesEl.textContent = remainingTiles;
        }
    }
    
    updateTurn(currentPlayer, hasMoved = false) {
        if (this.currentPlayerEl) {
            this.currentPlayerEl.textContent = currentPlayer;
        }

        if (this.endTurnButton) {
            this.endTurnButton.disabled = currentPlayer !== this.socket.id;
            this.endTurnButton.textContent = hasMoved ? 'End Turn' : 'Skip Turn';
        }
    }

    updatePlayerList(players, currentPlayer) {
        this.playerListEl.innerHTML = '';
        players.forEach(player => {
            const li = document.createElement('li');
            li.textContent = player;
            li.classList.add('player');
            if (player === currentPlayer) {
                li.classList.add('current');
            }
            this.playerListEl.appendChild(li);
        });
    }

    createTile(tileInfo) {
        const span = document.createElement('span');
        span.id = tileInfo.id;
        span.className = `tile ${tileInfo.color} ${tileInfo.is_new ? 'new' : ''}`;
        span.setAttribute('draggable', 'true');
        span.dataset.tileNumber = tileInfo.number;
        span.dataset.tileColor = tileInfo.color;
        span.dataset.tileIsnew = tileInfo.is_new;
        span.textContent = tileInfo.number;
    
        span.addEventListener('dragstart', this.drag.bind(this));
        return span;
    }
    
    createPlacer(comboIndex, position) {
        const span = document.createElement('span');
        span.className = 'placer';
        span.dataset.combo = comboIndex;
        span.dataset.position = position;
        span.innerHTML = '&nbsp;';
    
        span.addEventListener('drop', this.drop.bind(this));
        span.addEventListener('dragover', this.allowDrop.bind(this));
        span.addEventListener('dragleave', this.leave.bind(this));
    
        return span;
    }
    
    comb(comboIndex, isValid, content) {
        const div = document.createElement('div');
        div.className = `combination ${isValid ? 'valid' : 'invalid'}`;
        div.dataset.combo = comboIndex;
        div.innerHTML = content;
        return div.outerHTML;
    }

    endTurn() {
        this.socket.emit('end_turn', { room: this.room });
    }

    allowDrop(ev) {
        ev.preventDefault();
        ev.target.style.width = '50px';
    }

    drag(ev) {
        ev.dataTransfer.setData("id", ev.target.id);
        ev.dataTransfer.setData("origin", ev.target.parentElement.dataset.combo);
    }

    leave(ev) {
        ev.target.style.width = "5px";
    }

    drop(ev) {
        ev.preventDefault();
        const tileId = ev.dataTransfer.getData("id");
        const origin = parseInt(ev.dataTransfer.getData("origin"));
        const target = parseInt(ev.target.dataset.combo);
        const position = parseInt(ev.target.dataset.position);

        ev.target.style.width = "5px";

        const tileElement = document.getElementById(tileId);
        const tileData = {
            id: tileId,
            number: parseInt(tileElement.dataset.tileNumber),
            color: tileElement.dataset.tileColor,
            is_new: tileElement.dataset.tileIsnew
        };

        this.socket.emit('place_tile', {
            room: this.room,
            tile: tileData,
            origin: origin,
            target: target,
            position: position
        });
    }
}

// Initialize the game client once DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.game = new GameClient();

    document.getElementById('end-turn').addEventListener('click', () => {
        game.endTurn();
    });
});
