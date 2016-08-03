import { provideRouter, RouterConfig } from '@angular/router';
import { GameListComponent } from './games.component';
import { GameDetailsComponent } from './game-details.component';

const routes: RouterConfig = [
    {
        path: '',
        redirectTo: '/games',
        pathMatch: 'full'
    },
    {
        path: 'games',
        component: GameListComponent
    },
    {
        path: 'games/:name',
        component: GameDetailsComponent
    }
];

export const appRouterProviders = [
    provideRouter(routes)
];
