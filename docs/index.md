# Sodalite documentation
## Yet another file explorer
Have you ever played [crawl](https://crawl.develz.org/)?
That's a terminal based roguelike dungeon crawler.  
What makes it stand out is it's extremely efficient menu navigation philsophy. 

![dcss inventar management](crawl.png)

*Dungeon Crawl Stone Soup: For selecting an item, press it's automatically assigned key.*

After a while, the keys will burn into one's muscle memory - using the game's interface feels extremely efficient.  
`sodalite` brings the same asset to your file system: Navigation at the speed of thought.

## Navigate the file system
When opening `sodalite`, you will see the listing of the current directory.   
Pressing one of the keys displayed in front of the entries will take you there.
![Sodalite](sodalite.png)

On the right side, the current possible actions with their corresponding keybindings are displayed. 
All actions are freely configurable. 

Whenever `sodalite` encounters an entry the first time, it will automatically assign a free key to this entry.  
If you'd rather like to assign a specific key to an entry, you can do that in `assign mode`.  
> **TIP:** Assign the most intuitive and/or reachable keys to your most frequently used entries, and stick with this assignment. 
Once setup, and muscle memory kicks in, all directories will be reachable in a blink of an eye.

#### Keybindings
| Action            | Description                                  | Key              |
| ----------------- | -----------                                  | ---------------- |
| go to             | navigate to directory with key               | `a-zA-Z`         |
| go to home        | navigate to $HOME                            | `` ` ``, `~`     |
| go to parent      | equivalent to `cd ..`                        | `.`              |
| go to previous    | Go to previous entry (backward in history)   | `Control + H`    |
| go to next        | Go to next entry (forward in history)        | `Control + L`    |
| exit              | exit `sodalite` and `cd` into current dir    | `ESC`, `ENTER`   |
| abort             | exit `sodalite` without changing current dir | `Control + c`    |
| assign mode       | Reassign keys of entries                     | `=`              |
| filter            | Search for entries                           | `/`              |
| page down         | Scroll to next page                          | `Control + f`    |
| page up           | Scroll to previous page                      | `Control + b`    |
| half page down    | Scrolls down half a page                     | `Control + d`    |
| half page up      | Scrolls down half a page                     | `Control + u`    |

###### Filtering
| Action            | Description                         | Key              |
| ----------------- | -----------                         | ---------------- |
| submit            | keeps filter and quits filter mode  | `ENTER`          |
| cancel            | clears filter and quits filter mode | `ESC`            |

###### Assign mode
| Action            | Description                                | Key              |
| ----------------- | -----------                                | ---------------- |
| submit            | chooses selected entry                     | `ENTER`          |
| move up           | Move selection upwards                     | `Control + P`    |
| move down         | Move selection downwards                   | `Control + N`    |
| cancel            | Cancels reassignment and quits assign mode | `ESC`            |



[&larr; README](../README.md)

