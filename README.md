# HSRCharEval

## About

HSRCharEval, or Honkai: Star Rail Character Evaluation is a program which allows its users to rate their built characters from the game using their stats and a target build to reach.

## Setup / Installation

To use the program either set up an environment with Python or use the binaries available [at the releases](https://github.com/SweetPinkMilkTea/hsrchareval/releases):

### Python environment 

- Clone the repo, for example using `git clone https://github.com/SweetPinkMilkTea/hsrchareval.git` in your CLI
- `cd` into the newly created directory
- Create a virtual environment: `python -m venv .venv`
- Activate the `venv`:
   - `.venv\Scripts\activate.bat` (Windows)
   - `source .venv/bin/activate` (Mac/Linux)
- Install the requirements via `pip install -r requirements.txt`
- Launch the script while the `venv` is active.

> [!NOTE]
> Don't forget that the `venv` needs to be activated every time the program is launched.

### Binaries

> [!NOTE]
> Binaries are only available for Windows.

Head to the releases and choose the version you want to use, ideally the latest, then download the executable.

Once your download concludes you can run the `.exe` anywhere you want.

## Usage

### Guide

Characters entered into the program will be scored by comparing your entered build and the target reference called "breakpoints".

To get started, create breakpoints for the characters you want to evaluate first using Option 5 in the main menu.

The program will ask for target values for various stats. Any stats irrelevant to the performance of a character should be marked by entering `-1`.

> [!TIP]
> The program has been written using recommended builds from [prydwen.gg](https://www.prydwen.gg/star-rail/) in mind. Visit them and use their recommendations for the most consistent program usage.

Once breakpoints are created, continue entering your own character information.

Open the character edit screen with Option 3, and with the "All characters" filter, select the character you have previously created breakpoints for and enter all prompted stats.

> [!TIP]
> If you have entered your UID and your target character is part of your "Starfaring Companions", their stats can be imported without the need to type them out.

Once you are done, visit your character overview located under Option 1.

You will see your character's score, determined on how well it is compared to its breakpoints. Selecting the character in this menu will show both the breakpoints and current values and highlight where improvements are necessary.

### Full

The main menu consists of 8 Options:

#### 1 | Look up characters

Displays all characters you have entered and their score. Select a character by typing its index to see its stats and breakpoint requirements.

#### 2 | Look up teams

Displays all teams you have created and their score derived by the ratings of the characters they consist of. Select a team by typing its index to see the team's characters and their stats.

#### 3 | Create/Edit personal character

Either create or update a character you have. If you have set an UID, importing the values is attempted.

You cannot create a character if no breakpoints have been recorded.

#### 4 | Create/Edit teams

Either create or update a team. A team must be named and consist of 4 characters.

Teams are good to make for comparing the overall quality of teams.

#### 5 | Create/Edit breakpoints

Create or adjust the values used for rating characters here.

Mark stats not relevant to the character by using the value `-1`.

If a stat value is meant to be kept **under** a certain limit, mark it as inverse by typing the max. allowed value first, then typing the stat key (e.g. "SPD","ATK",...) under the inverse prompt. If multiple inverse stats are required, separate the keys with `,`.

#### 6 | Create/Edit 'bridges'

Bridges are used to increase the stats "on top" of a character already existing stats.

This is best used on Eidolons or Relics with conditional effects.

Example:
Acherons E1 increases her Crit Rate by 18% when attacking debuffed enemies. This is not reflected in her stats, as this effect is conditional.

> [!NOTE]
> Don't overuse bridges for things like other characters or hypothetical scenarios.

#### 7 | Quickscan

This option allows for scanning characters without saving. This is best used on temporary character builds or when checking other accounts characters.

#### 0 | Edit configuration

1.  **Fetch new characters**

    Checks [prydwen.gg](https://www.prydwen.gg/star-rail/) for characters not currently present in the current breakpoints and adds them.

> [!NOTE]
> Breakpoints added this way are empty and cannot be used to add characters. You'll need to edit them after importing.

2.  **Set UID**

    Set your UID if you skipped the startup prompt or want to change it. It's used when importing character stats.

3.  **API name translation**
    
    API name mapping is used to find your characters even if their names do not match the local name.

    Edit the name mapping to resolve issues importing characters, you can verify your mappings in this menu as well.

## Contributing

Report issues at the issue section of the repository. Make sure that the issue is reproduceable with the latest version.

To propose features, use the appropriate tag.

To contribute a pull request, keep the implementation simple and limited to the functionality you wish to achieve, while providing sufficient detail.

## Acknowledgements

Thanks to:
- [prydwen.gg](https://www.prydwen.gg/star-rail/) as the main source of inspiration and hosting the recommended endgame values for each character
- [mihomo API](https://github.com/MetaCubeX/mihomo) for the ability to get character values of HSR accounts via UID