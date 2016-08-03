import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import 'rxjs/add/operator/toPromise';

import { Game } from './game';

@Injectable()
export class GamesService {
    private gamesUrl = '/games/';

    constructor(private http: Http) { }

    getGames(): Promise<Game[]> {
        return this.http.get(this.gamesUrl)
            .toPromise()
            .then(response => response.json().data)
            .catch(this.handleError);
    }

    getGame(name: string) {
        return this.getGames()
            .then(games => games.find(game => game.name === name));
    }

    post(game: Game) {
        let headers = new Headers({
            'Content-Type': 'application/json'
        });

        return this.http
            .post(this.gamesUrl, json.stringify(game))
    }
}
