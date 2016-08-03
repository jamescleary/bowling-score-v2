import { Component, OnInit, Input } from '@angular/core';
import { Router } from '@angular/router';

import { Frame, FrameType } from './game';
import { GameService } from './games.service';

@Component({
    selector: 'bowling-frame',
    templateUrl: '/static/frame.component.html'
})
export class FrameComponent implements OnInit {
    @Input() frame: Frame;
    private FrameType = FrameType;
}
