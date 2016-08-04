import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

import { Frame, FrameType } from './game';

@Component({
    selector: 'bowling-frame',
    templateUrl: '/static/app/frame.component.html',
	styles: [`
		.frame {
			display: flex;
			flex-direction: column;
			margin: .5rem;
			border: 1px solid #e2e2e2;
		}
		.frame .frame-rolls {
			display: flex;
			flex-direction: row;
		}
		.frame .frame-rolls > div {
			border: dotted 1px black;
			padding: 0.25rem;
		}
		.frame-score {
			width: 100%;
		}
		`]
})
export class FrameComponent {
    @Input() frame: Frame;
    private FrameType = FrameType;
}
