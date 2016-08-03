import { Component, OnInit, EventEmitter, Input, Output, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Game, Frame, FrameType } from './game';
import { GamesService } from './games.service';
import { FrameComponent } from './frame.component';

@Component({
	selector: 'game-details',
	templateUrl: '/static/game-details.component.html',
})
export class GameDetailComponent implements OnInit {
	@Input() game: Game;
	sub: any;
	constructor (private gameService: GamesService,
				 private route: ActivatedRoute) { }

	ngOnInit() {
		this.sub = this.route.params.subscribe(params => {
			if (params['name'] !== undefined) {
				let name = params['name'];
				this.gameService.getGame(name)
					.then(game => this.game = game);
			} else {
				this.game = new Game(0, 'unnamed', [], 0);
			}
		});
	}

	ngOnDestroy() {
		this.sub.unsubscribe();
	}

	addRoll(roll: number) {
		
	}
}
