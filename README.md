# chiyoko
Python module to clone a directory hierarchy that processes multimedia files during the cloning

Hey You!
"Who? Me?"
Yes, you. Have an organized directory hierarchy containing all of your pictures and videos and running out of space?
Need to compress those photos and videos while maintaining the organization in the directory? Want to compress your
multimedia files and keep the organization? Then chiyoko.py is the right module for you!!!

"What is chiyoko.py?"
Okay... I'm done with this T.V infomercial thingy.

Name:
    'Chiyoko' is the main character of the 2001, Satoshi Kon movie 'The Millenium Actress'. The name of this script
    is a homage to the great woman and her relentless pursuit of her love through time, and to the great Mr. Satoshi
    Kon for such a wonderful movie.
    This script was written with the belief that even the not-so-important photos lying around in our HDDs today will
    someday turn out to be The Key - "to the most important thing there is". Let's not trade memories for HDD spaces.
    
Dependencies, Platform and Usage:
    This script works only on Linux. If you're using Windows or Mac, and want to use it, just live boot a Linux Distro
    and run this script. This one is your best bet: https://linuxmint.com/download.php (Linux Mint 18.1 XFCE), as it
    comes with all the dependencies pre-installed and you can run this script with this simple command:
             $ python3 chiyoko.py SOURCE DESTINATION -I -V
    
    Dependencies:
      i) imagemagick-common ($sudo apt-get install imagemagick-common)
      ii) avconv ($ sudo apt-get install libav-tools)
      iii) Other GNU utilities that should be on your Linux Distro by default (file, du, tail)
    
    Usage:
      The Script takes two mandatory arguments: SOURCE and DESTINATION
      
      SOURCE is the directory which you want to clone. i.e. The 'All My Childhood Pictures Ever' directory/folder.
      
      DESTINATION is the directory where you want to save the compressed clone of the SOURCE directory. i.e. The
          'Oh-no-I've-run-out-of-all-my-space-and-this-is-the-only-HDD-with-some-remaining' directory/folder.
          
          Special Parameter: Setting DESTINATION to be '__in-place__' does all the processing in the same directory.
          So, you'll have everything in the same directory, but compressed. (This special parameter's syntax has been
          intentionlly made to resemble Python's special variable syntax.)
      
      -I turns on photo processing. Photo processing as in resizes everything to be 1000xautomatic_value size (by default)
       An optional parameter to -I can change the resize scale. I generally use 1300, 1700 and similar numbers for the
       super important pictures, but 1000 works just fine for most cases.
       
      -V turns on video processing. This doesn't take any arguments. The underlying avconv command that does the video
        processing is courtesy of Matthew Bro (@leklachu), a really cool guy.
        
      -h or --help will give you usage information
      
      Using the script without either -I or -V would result in an exact copy of the SOURCE into the DESTINATION. Not
      very useful.
      
    Modifications:
      If the settings aren't working for you, open the script in a text editor and change the two global variables to be
      what you want them to be. I'd try the modified commands on a few guinea files before I modify the script's commands,
      though. Just make sure that you define the command string with a double quote and keep the single quotes around the
      '%s'-es. The single quotes are there to safe-guard against any shell expansions.
      
    Notes and Tips:
      The script can handle all sorts of crazy file names. Thanks to the single quotes, we don't have to fear shell's
      expansions.
      
      If you have a huge directory to process, perhaps use a Raspberry Pi.
      Since this will probably take quite a bit of time, make the computer shutdown after completion of the script on its
      own with this command (for those of you who do not know):
        $ python3 chiyoko.py SOURCE DESTINATION -I -V && sudo -S poweroff <<< "YOURPASSWORDGOESHERE"
        In the aforementioned command, you only have to change the ALLCAPS variables. '$' isn't required but "" (quotes) are.
      
      Maybe listen to "Chiyoko's Theme" while running this script?      
