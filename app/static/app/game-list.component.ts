import { Component, OnInit } from '@angular/core';
import { GamesService } from './games.service';

@Component({
    selector: 'game-list',
    templateUrl: '/static/game-list.component.html'
})
export class GamesListComponent implements OnInit {
    constructor(private router: Router,
                private gamesService: GamesService) { }

    ngOnInit() {
        this.getGames();
    }

    getGames() {
        this.gamesService.getGames().then(games -> this.games = games);
    }

    onSelect(game: Game) { this.selectedGame = game; }

    gotoDetail() {
        this.router.navigate(['/games', this.selectedGame.name]);
    }
}
