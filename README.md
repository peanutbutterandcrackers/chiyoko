# chiyoko
__*Python script to clone a directory hierarchy, that also processes it's multimedia files along the way*__

Hey You!

"_Who? Me?_"

Yes, you.<br />
Have an organized directory hierarchy containing all of your pictures and videos and running out of space? "*Yes!*"<br />
Need to compress those photos and videos while maintaining the organization in the directory? "*Yes!*"<br /> Want to compress your
multimedia files and keep the organization? "*Yes!*"<br /> Then chiyoko.py is the right module for you!!!

"*What is chiyoko.py?*"

( Okay... I'm done with this T.V infomercial thingy. )

## Name:
'Chiyoko' is the main character of the 2001, Satoshi Kon movie 'The Millenium Actress'. The name of this script
is a homage to the great woman, and to the great Mr. Satoshi Kon, the genius behind the movie.
This script was written with the belief that even the not-so-important photos lying around in our HDDs today will
someday turn out to be The Key - "to the most important thing there is". Let's not trade memories for HDD spaces.

## Dependencies, Platform and Usage
This script works only on Linux. If you're using Windows or Mac, and want to use it, just live boot a Linux Distro
and run this script. This one is your best bet: https://linuxmint.com/download.php (Linux Mint 18.1 XFCE), as it
comes with all the dependencies pre-installed and you can run this script with this simple command:

```bash
$ python3 chiyoko.py SOURCE DESTINATION -I -V
```

### Dependencies
* imagemagick ```$ sudo apt-get install imagemagick```
* ffmpeg ```$ sudo apt-get install ffmpeg```
* Other GNU utilities that should be on your Linux Distro by default ```file, du, tail, etc.```

### Usage

The Script takes two mandatory arguments: ```SOURCE``` and ```DESTINATION```

```SOURCE``` is the directory which you want to clone. i.e. The '*All My Childhood Pictures Ever*' directory/folder.

```DESTINATION``` is the directory where you want to save the compressed clone of the ```SOURCE``` directory. i.e. The
'_Oh-no-I've-run-out-of-all-my-space-and-this-is-the-only-HDD-with-some-remaining_' directory/folder.

**Special Parameter:** Setting ```DESTINATION``` to be ```'__in-place__'``` does all the processing in the same directory.
So, you'll have everything in the same directory, but compressed. (This special parameter's syntax has been
intentionally made to resemble Python's special variable syntax.)

* ```-I``` turns on photo processing. Photo processing as in resizes everything to be 1300xautomatic_value size (by default) An optional parameter to ```-I``` can change the resize scale. I generally use 1300, 1700 and similar numbers for the super important pictures, but 1000 works just fine for most cases.

* ```-V``` turns on video processing. This doesn't take any arguments.

* ```-h``` or ```--help``` will give you usage information

Using the script without either ```-I``` or ```-V``` would result in an exact copy of the ```SOURCE``` into the ```DESTINATION```, as-is. Not
very useful.

### Modifications
If the settings aren't working for you, open the script in a text editor and change the two global variables to be
what you want them to be. I'd try the modified commands on a few guinea files before I modify the script's commands,
though.

Maybe listen to "Chiyoko's Theme" while running this script?      
