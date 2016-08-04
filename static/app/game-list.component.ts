import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GamesService } from './games.service';
import { Game } from './game';

@Component({
    selector: 'game-list',
    templateUrl: '/static/app/game-list.component.html',
	styles: [`
		ul.games li a {cursor: pointer;}
		`]
})
export class GamesListComponent implements OnInit {
	games: Game[];
	editing = false;
	newGame = '';
    constructor(private router: Router,
                private gamesService: GamesService) { }

    ngOnInit() {
        this.gamesService
			.getGames()
			.then(games => this.games = games);
    }

    getGames() {
        this.gamesService.getGames().then(games => this.games = games);
    }

	addNew() {
		this.editing = true;
	}

	cancelNew() {
		this.editing = false;
		this.newGame = '';
	}

	saveNew() {
		let game = new Game(0, this.newGame, [], 0);
		this.gamesService.post(game)
			.then(game => this.gotoDetail(game));
	}

    gotoDetail(game: Game) {
        this.router.navigate(['/games', game.pk]);
    }
}
