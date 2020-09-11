# CSS Tetris
> A CSS based QFTASM interpreter

CSS Tetris uses the space-toggler hack, a way of expressing logical ANDs and ORs using certain properties of CSS3 variables, to implement a limited version of the Quest for Tetris processor, and thus provide an extremely impractical way for someone with a great deal of patience to (theoretically) play Tetris in the browser. It also showcases a fundamental limitation to the Turing completeness of CSS - there is no way to automatically feed the outputs back into the inputs, so all state between cycles must be stored in HTML through human input, in this via lots of checkboxes and labels.

This project was inspired by CSS Sweeper, a minesweeper game written using the same tricks, but extends the concept further towards general computation, at the cost of practicality. It also owes a lot to the work of the Quest for Tetris team, who designed the processor and wrote the code that actually implements Tetris for it.

## Todo List
- Fix indirect operand access (check pc=13)
- Record timelapse of Tetris being played
