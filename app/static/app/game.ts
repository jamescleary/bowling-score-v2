export class Game {
	id: number;
	name: string;
	rolls: number[];
	frames: Frame[];
	score: number;
	curFrame: Frame;

    constructor(id: number, name: string, rolls: number[],
                score: number) {
        this.id = id;
        this.name = name;
        this.rolls = rolls;
        this.frames = [];
        this.score = score;
        this.curFrame = new Frame(false);
		this.evaluateFrames();
    }

	evaluateFrames() {
		this.curFrame = new Frame(false);
		this.frames = [];
        this.rolls.forEach((roll, i) => {
			this.curFrame.addRoll(roll);
			if ([FrameType.New, FrameType.Half].indexOf(this.curFrame.type) < 0) {
				if (this.curFrame.type === FrameType.Strike) {
					this.curFrame.addRolls(this.rolls.slice(i + 1, i + 3));
				} else if (this.curFrame.type === FrameType.Spare) {
					this.curFrame.addRoll(this.rolls[i+1]);
				} else if (this.curFrame.type === FrameType.FinalFrame) {
					this.curFrame.addRolls(this.rolls.slice(i+1));
				}
				this.frames.push(this.curFrame);
				this.curFrame = new Frame(frames.length >= 9);
			} 
        })
	}
}

export enum FrameType {
    New,
    Half,
    OpenFrame,
    Spare,
    Strike,
    FinalFrame,
    Invalid
}

const noChangeFrames = [
    FrameType.OpenFrame,
    FrameType.Spare,
    FrameType.Strike,
    FrameType.FinalFrame
]

export class Frame {
    type: FrameType;
    rolls: number[];

    constructor(isFinal: Boolean) {
        if (isFinal) {
            this.type = FrameType.FinalFrame;
        } else  {
			this.type = FrameType.New;
		}
		this.rolls = [];
    }

    addRoll(roll: number): Frame {
        if (this.canAddRoll()) {
            this.rolls.push(roll);
            this.updateType();
        }
        return this;
    }

	addRolls(rolls: number[]): Frame {
		rolls.forEach(roll => this.addRoll(roll));
		return this;
	}

    updateType() {
        if (noChangeFrames.indexOf(this.type) >= 0)  {
            return;
        } else if (this.rolls[0] == 10) {
            this.type = FrameType.Strike;
        } else if (this.rolls.length === 0){
            this.type = FrameType.New;
        } else if (this.rolls.length === 1){
            this.type = FrameType.Half;
        } else if (this.rolls[0] + this.rolls[1] === 10) {
            this.type = FrameType.Spare;
        } else {
            this.type = FrameType.OpenFrame;
        }
        return;
    }

    canAddRoll(): boolean {
        switch (this.type) {
        case FrameType.Strike: return this.rolls.length < 3;
        case FrameType.Spare: return this.rolls.length < 3;
        case FrameType.New:
        case FrameType.Half:
            return true;
        case FrameType.OpenFrame:
            return false;
        case FrameType.FinalFrame:
            return ((this.rolls.length < 2) ||
                    (this.rolls.length === 2 &&
                     (this.rolls[0] === 10 ||
                      this.rolls[0] + this.rolls[1] === 10)));
        default:
            return false;
        }
    }
}
