# QSpice-converter-SVG
QSpice schematic and symbol parser with SVG generation features. Expansible to other formats.

This script is able to parse a QSpice schematic or symbol and transform it into Python dictionary objects in memory, so its fields are accessible by identifiers. It's also capable of composing back a QSpice file from this object in memory. It has SVG path generation functions implemented, so that the schematic can be saved as .svg file, with or without symbol abstraction. The script is patchable by adding modules that start with "qs" to the main module's folder, allowing other functionalities to be added, like conversion to other formats, without the need to modify the original modules. The functionalities for having plottable open path text and conversion to KiCAD format for PCB generation are thought to be added next by the original author.


Usage(command line):
```
qsconvert.py [options] [tasks] [filenames]
```

Example options: /e /fs*=1.5 /m -hs /cc=0xff /w=100
Example tasks: /svg /fsvg /g=3
Displaying help: qsconvert.py /?

If no filenames are informed, the script processes all valid formats from the working folder.
