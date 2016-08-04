import { Component } from '@angular/core';
import { ROUTER_DIRECTIVES } from '@angular/router';
import { GamesService } from './games.service';

@Component({
    selector: 'my-app',
    templateUrl: '/static/app/app.component.html',
    directives: [ROUTER_DIRECTIVES],
	providers: [GamesService],
})
export class AppComponent { }
