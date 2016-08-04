export class Game {
	pk: number;
	name: string;
	rolls: number[];
	frames: Frame[];
	score: number;
	curFrame: Frame;

    constructor(pk: number, name: string, rolls: number[],
                score: number) {
        this.pk = pk;
        this.name = name;
        this.rolls = rolls;
        this.frames = [];
        this.score = score;
        this.curFrame = new Frame(false);
		this.evaluateFrames();
    }

	addRoll(roll: number) {
		if (roll < 0 || roll > 10) {
			throw "Please use a number between 0 and 10";
		} else if (this.curFrame.type === FrameType.Half && 
				   10 - this.curFrame.score() < roll) {
			throw ("Please use a number between 0 and " + 
				   (10 - this.curFrame.score()));
		} else if (this.frames.length === 10 && !this.frames[9].canAddRoll()) {
			throw("Game Over!");
		}
		this.rolls.push(roll);
		this.evaluateFrames();
	}

	evaluateFrames() {
		this.curFrame = new Frame(false);
		this.frames = [];
		for (let i = 0; i < this.rolls.length; i++) {
			let roll = this.rolls[i];
			this.curFrame.addRoll(roll);
			if ([ FrameType.New, FrameType.Half ].indexOf(this.curFrame.type) < 0) {
				if (this.curFrame.type === FrameType.Strike) {
					this.curFrame.addRolls(this.rolls.slice(i + 1, i + 3));
				} else if (this.curFrame.type === FrameType.Spare) {
					this.curFrame.addRolls(this.rolls.slice(i + 1, i + 2));
				} else if (this.curFrame.type === FrameType.FinalFrame) {
					this.curFrame.addRolls(this.rolls.slice(i));
					this.frames.push(this.curFrame);
					break;
				}
				this.frames.push(this.curFrame);
				this.curFrame = new Frame(this.frames.length >= 9);
			} else if (this.rolls.slice(i).length === 1) {
				this.frames.push(this.curFrame);
			}
        }
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

	score(): number {
		return this.rolls.reduce((a, b) => a + b, 0);
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
