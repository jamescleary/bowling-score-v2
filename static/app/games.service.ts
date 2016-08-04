import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import 'rxjs/add/operator/toPromise';

import { Game } from './game';

@Injectable()
export class GamesService {
    private gamesUrl = '/api/games/';

    constructor(private http: Http) { }

    getGames(): Promise<Game[]> {
        let headers = new Headers({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        });

        return this.http.get(this.gamesUrl, {headers: headers})
            .toPromise()
            .then(response => response.json().map(game_json => {
				return new Game(game_json.pk, game_json.name, game_json.rolls,
								game_json.score);
			}))
            .catch(this.handleError);
    }

    getGame(pk: string) {
		let _pk = Number.parseInt(pk);
        return this.getGames()
            .then(games => games.find(game => game.pk === _pk));
    }

    post(game: Game) {
        let headers = new Headers({
            'Content-Type': 'application/json',
			'Accept': 'application/json',
        });

        return this.http
            .post(this.gamesUrl, JSON.stringify(game), {headers: headers})
			.toPromise()
			.then(res => res.json())
			.catch(this.handleError);
    }

	put(game: Game) {
        let headers = new Headers({
            'Content-Type': 'application/json',
			'Accept': 'application/json',
        });

		let url = `${this.gamesUrl}${game.pk}/`;

        return this.http
				   .put(url, JSON.stringify(game), {headers: headers})
				   .toPromise()
				   .then(game => {
					   let js = game.json();
					   return new Game(js.pk, js.name, js.rolls, js.score);
				   })
				   .catch(this.handleError);
	}

	delete(game: Game) {
        let headers = new Headers({
            'Content-Type': 'application/json'
        });

		let url = `${this.gamesUrl}/${game.pk}`;
		return this.http.delete(url, {headers: headers})
						.toPromise()
						.catch(this.handleError);
	}

	handleError(error) {
		return Promise.reject(error.message || error);
	}

}
