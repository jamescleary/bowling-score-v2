import { Component, OnInit, EventEmitter, Input, Output, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Game, Frame, FrameType } from './game';
import { GamesService } from './games.service';
import { FrameComponent } from './frame.component';

@Component({
	selector: 'game-details',
	templateUrl: '/static/app/game-detail.component.html',
	directives: [FrameComponent],
	styles: [`
		.frames { display: flex; }

		`]
})
export class GameDetailComponent implements OnInit {
	game: Game;
	sub: any;
	roll: string;
	error = '';
	_clean = true;
	constructor (private gameService: GamesService,
				 private route: ActivatedRoute) { }

	ngOnInit() {
		this.sub = this.route.params.subscribe(params => {
			if (params['pk'] !== undefined) {
				let pk = params['pk'];
				this.gameService.getGame(pk)
					.then(game => this.game = game);
			} else {
				this.game = new Game(0, "loading...", [], 0);
			}
		});
	}

	ngOnDestroy() {
		this.sub.unsubscribe();
	}

	addRoll() {
		this.error = '';
		try {
			this._clean = true;
			this.game.addRoll(Number.parseInt(this.roll));
		} catch(e) {
			this.error = e;
			this._clean = false;
		} finally {
			if (this._clean) {
				this.gameService.put(this.game)
					.then(game => {console.log(game); this.game = game;})

					.catch(error => {
						let _error = error.json();
						if (_error.rolls) {
							this.error = _error.rolls[0];
						} else {
							this.error = "An unknown error has occured"
						}
						return this.game;
					})
			}
			this.roll = '';
		}
	}
}
