import { provideRouter, RouterConfig } from '@angular/router';
import { GamesListComponent } from './game-list.component';
import { GameDetailComponent } from './game-detail.component';

const routes: RouterConfig = [
    {
        path: '',
        redirectTo: '/games',
        pathMatch: 'full'
    },
    {
        path: 'games',
        component: GamesListComponent
    },
    {
        path: 'games/:pk',
        component: GameDetailComponent
    }
];

export const appRouterProviders = [
    provideRouter(routes)
];
