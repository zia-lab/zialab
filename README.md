# zialab

Instrument control, GUIs, and glue code as one would in an optical spectroscopy laboratory.

```
WHHdHudMWWSQxWKVTV3dkZBWYdH3SzmW8dWWXkdUk$1XXkH
dkApX26ZwJjssJWk0WkZHXQdXWHjHSM8dU9XzSaHSgHWWHk
gsdWZWs$Y!?`????????`!??7?=?!```??!!?7!`DSWHUXD
MNWSDJk|..              .           !  .uHHH9Wk
NHWXdkWG.&...............,....+J..,    .mN#GdHO
k&zzOHkt ?`     .       ...``    .l    .9WwddIr
wy4dHW6w`?.            `. .      .|    .HSQX$Z0
XHSmHHQdHZXZUAdXrWXfdMHXv=      .J`    .0VIdwdH
HkdWXSkRJfRkWWWbHWHGJvdY :    .7`   ..JWWSZOJOk
d0kXkWWROHdXQHHHHXQWff`  . ..Z!``  .dwWHHX0cJdG
BddHHWAXkWHXpTHSQHdf` `?`..7`     JMDgWW0wWOXQH
OjXH#HUWHmHHWXUd9Y!     .V!    ..WkN1AzU6WH9vWW
jMMH6UXXHSvN2Vdf!     .?`  .  .qmXNvdSkHHH+Jd99
HHWkdHEV4Rkd#Z'     .?!     .dHHWKWOWwdMHndK4kW
NNM#HUZAZH9Zt     .?!     .WKGOXMHKOvdHN0uWKWKS
HH9IZjWSOw= . . .``     .HWZ#kkWKWOke9dHW9WnUOd
MHWiXUud=    :.J`     .WWHHKWdlJX0dyHd0WcXUkWUS
HVVjwdX   .` J\           ``,    `     .JdHKHky
kGOdWWH    .l                          .kWWwfkX
BAdXXu9     @,+ns?J..+.J&J+&JJ&J,...&+vOdkWwWXX
XUdH9w6                      .         .WfGyWTW
Xk9CdCd         `!   .     . !         .J1CJJVU
K1dXSXbRyXbuMMWkdHCwZwGSZUQSHKZJKSH&JtdWzdQkkUV
kjfSWXHkWHXS9ZyWodGkOumAUdXdHWbHHHHdNZXHbwWWXWX
```

# analysis : deconvolutions and the like
+ `trpl.py` : time-resolved spectroscopy with proEM.

# cem : computational electromagnetism
+ `metalenses_x.py` : MEEP, S4 and numpy for simulating metasurfaces

# data : bits of useful spectroscopic information
+ `nist_atomic_spectra_database_levels.csv` : atomic levels from NIST
+ `nist_atomic_spectra_database_lines.csv` : atomic lines from NIST

# gui : graphical user interfaces
+ `picoGeiger2ch.py` : view of countrate from PicoHarp
+ `verdiGUI.py` : GUI for controlling Verdi through RPi
+ `monitor` : general purpose viewer of a time-changing var

# instruments
+ `ADS1x15.py` : to read ADC in Raspberry Pi
+ `DCC165C-HQ.py` : read data from a Thorlabs camera
+ `cryopi.py` : control RPi in cryostat
+ `cube.py` : control Cube laser through serial connection
+ `flipmirror.py` : control flipmirror using Raspberry Pi
+ `funcgen33120A.py` : to-do
+ `hayear_camera.py` : brute-force automation of the hayear camera
+ `innova300.py` : serial connection to the Innova 300.
+ `lakeshore.py` : control the Lakeshore temp controller
+ `madcity.py` : MadCity lab stages
+ `mmeter34401A.py` : agilent 34401A via serial connection
+ `montana.py` : control of the Montana cryostat through ethernet
+ `nanocube.py` : nanopositioning near absolute zero
+ `pda36a.py` : reading optical power from a Thorlabs photodiode
+ `picoharp.py` : control PicoHarp
+ `powerE3631A.py` : to-do
+ `remotePD.py` : flask server for photodiode
+ `sony_camera.py` : brute-force automation of Sony camera
+ `srsDG535.py` : control DG 525 signal generator
+ `vega.py` : to-do
+ `verdi.py` : serial control of Verdi

# man : manuals for instruments
+ ...

# softwarecontrol :
+ `lightfield.py` : controling Lightfield from Python
+ `spe2py.py` : importing spe files into Python
+ `speloader.py` : importing sp2 files into Python

# misc :
+ `Filter.ipynb` : parsing filter data
+ `Filters.xlsx` : transmission data for Semrock filters
+ `filters.pkl` : Pandas dataframe with filter data
+ `sugar.py` : ringing bells and others
