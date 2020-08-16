# mff_auto
Game bot for [Marvel Future Fight](https://play.google.com/store/apps/details?id=com.netmarble.mherosgb&hl=ru) game.
Compatible with **6.3.0** version.

## FAQ
**Q**: What this bot can do?

**A**: **mff_auto** can play almost all game modes: World Bosses, Alliance Battle, Co-op missions, Dimension missions, Timeline battles, Legendary battles, World Boss Invasions, Epic Quests.

Also it can enable *Autoplay++* feature anywhere and do your daily routines.

**Q**: Which Android emulators are supported?

**A**: Currently only [NoxPlayer 6.3.0.5](http://res06.bignox.com/full/20190723/7806c680dd1e4a66990aea06b6dcbcc9.exe?filename=nox_setup_v6.3.0.5_full_intl.exe).

**Q**: Why NoxPlayer version 6.3.0.5?

**A**: This version show itself most stable and it don't change position of installed games with ads.

## Video example

Video footage of all game modes running by **mff_auto**: https://youtu.be/QcgZcAwBL-I

## Installation and usage

- Install [NoxPlayer 6.3.0.5](http://res06.bignox.com/full/20190723/7806c680dd1e4a66990aea06b6dcbcc9.exe?filename=nox_setup_v6.3.0.5_full_intl.exe)
 and then install and run [Marvel Future Fight](https://play.google.com/store/apps/details?id=com.netmarble.mherosgb).

- Set [NoxPlayer](http://res06.bignox.com/full/20190723/7806c680dd1e4a66990aea06b6dcbcc9.exe?filename=nox_setup_v6.3.0.5_full_intl.exe)
 graphics rendering mode to `Speed (DirectX)`: [Tutorial](https://www.bignox.com/blog/change-graphics-rendering-mode-noxplayer/)

- Set [NoxPlayer](http://res06.bignox.com/full/20190723/7806c680dd1e4a66990aea06b6dcbcc9.exe?filename=nox_setup_v6.3.0.5_full_intl.exe)
 screen resolution at least **1280x720**. If you encounter problems then try **1920x1080**.
 
- Set in [Marvel Future Fight](https://play.google.com/store/apps/details?id=com.netmarble.mherosgb) setting **GRAPHICS** to at least **Medium**. Lesser settings will lead to blurried text.

  In the same setting's menu turn off this notifications: `Mission Navigation Auto Popup` and `Future Pass Point Acquired`.

- Download last release: [Link to releases](https://github.com/tmarenko/mff_auto/releases)

- Run `start.bat` and enjoy.

## Development

At current state Marvel Future Fight bot is at beta stage.

- Farming bios in Epic Quest requires setting up `GAME_TASK`, `GAME_TASK_DRAG_FROM`, `GAME_TASK_DRAG_TO` and `GAME_APP`
in `settings\ui\main_menu.json`. This values should be calculated for your emulator's launcher.
- Legendary Battle contains only one free battle (Ragnarok).
- Timeline battle do not check if your team is available for battle. Please setup team manually.
- Alliance and World Boss battles do not check if your characters can do these modes. Make sure that you have strong characters.

## Contribution

Feel free to contribute. Don't forget about [license](LICENSE).

### Running from source code

- Install [Python 3.6.5](https://www.python.org/downloads/release/python-365)
- Install [Tesseract OCR 3.05.02](https://digi.bib.uni-mannheim.de/tesseract) and add path to Tesseract to your `PATH` environment.
- Download source code and install all requirements: ```pip install -r requirements.txt```
- Add `lib` folder to your `PYTHONPATH` or mark it as lib source.

Check `example.py` for examples of running any modes.

### Capture video for debugging

```python
    from lib.players.nox_player import NoxWindow
    from lib.game.game import Game
    from lib.video_capture import NoxCapture
    
    nox = NoxWindow("NoxPlayer")
    game = Game(nox)
    with NoxCapture(nox) as nox_recorder:
        # video file is in `logs` folder
        nox_recorder.pause()
        # pause recording
        nox_recorder.resume()
```
