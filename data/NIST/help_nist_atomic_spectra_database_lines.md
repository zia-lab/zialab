The ASD database provides access to transition data for atoms and atomic
ions. For more information on the Lines data accessible by the database
consult the [Introduction to and Contents of the ASD
Database](https://www.nist.gov/pml/atomic-spectra-database-contents).

This section starts with the description of the input parameters of the
Lines Search Form. For the description of the output, either in tabular
or graphical form, see the [Lines Output](#LINES_OUT) section.

------------------------------------------------------------------------------------

The ASD Lines Search Form, referred to as the "Lines Form," provides
access to transition data for atoms and ions, either in tabular or
graphical form. Tabular output is available for wavelengths, relative
intensities, radiative transition probabilities and related quantities,
as well as energy level classifications and bibliographic references.
Graphical output is available in the forms of Grotrian diagrams, line
identification plots, and Saha-LTE spectrum plots. For some spectra,
there is also graphical information on dependences of certain line
intensity ratios on electron density and/or temperature in the emitting
plasma. This information can be useful for plasma diagnostics.

When loaded in the browser, the Lines Search Form displays only the
[Main search parameters](#LINES_INP_MAIN) block. At the bottom of this
block, there are buttons "**Reset Input**," "**Retrieve Data**," "**Show
[Graphical Options](#LINES_GRAPH_OPTS)**," and "**Show [Advanced
Settings](#LINES_ADVANCED_OPTS)**." When the "Show ..." buttons are
clicked, the corresponding blocks of input options appear on the screen,
and the buttons change their names to "Hide ..."

The Lines Form prompts the user for the following pieces of information:

-   [Main search parameters](#LINES_INP_MAIN)
    -   [Spectra](#LINES_SPECTRA) of interest (e.g., Na I, Na II,
        Mg I-III, Mn-Co Ar-like)
    -   [Lower and upper limits of the wavelength/wavenumber
        range](#LINES_INP_WL_LIM)
    -   Wavelength units: angstroms (Å), nanometers (nm; default), or
        micrometers (μm); selected from a pulldown menu in the Lines
        Form. The units apply both to the output wavelengths and to the
        lower/upper limits of the wavelength range.
-   [Graphical Output Options](#LINES_GRAPH_OPTS)
    -   [Dynamic Plot options](#LINES_INP_DYN)
        -   [Line Identification Plot](#LINES_INP_ID_PLOT)
        -   [Saha-LTE Spectrum Plot](#LINES_INP_SAHA_PLOT)
    -   [Grotrian Diagram options](#LINES_INP_GROTRIAN)
-   [Advanced Settings](#LINES_ADVANCED_OPTS)
    -   [Output options](#LINE_OUTPUT_OPTS)
    -   [Optional search criteria](#LINE_OPTIONAL)
    -   [Additional search criteria](#LINE_CRITERIA)

For the description of the output, see the [Lines Output](#LINES_OUT)
section.

* * * * *

### Main Search Parameters

At a minimum, the user must enter [spectra](#LINES_SPECTRA) of interest
(e.g., H I) and then press the [Enter] key or click "Retrieve Data".
This will result in a tabular output page with transition data.
Alternatively, the user can click on the "Make Grotrian Diagram" button
to produce an interactive graphical diagram. The [Dynamic
Plots](#LINES_INP_DYN) require some additional settings, such as
[wavelength limits](#LINES_INP_WL_LIM) and units.

### Selecting Spectra for Line Searches

On the Lines Form, to specify an element, simply enter the element
symbol (e.g., Fe). Element symbols and Roman numerals need not be
capitalized. Multiple elements are separated by a semicolon. To indicate
the spectrum of a given element, enter either a Roman numeral or an
Arabic numeral after the element name. The Roman numerals must be
separated from the element symbol by a space. (**Note**: Fe I = Fe0+,
Fe II = Fe1+, etc.). Alternatively, the spectrum may be specified by the
name of its isoelectronic sequence (e.g., Si Li-like = Si XII,
Si Na-like = Si IV). The absence of a Roman or Arabic numeral or an
isoelectronic sequence name after an element symbol indicates all stages
of ionization. Spectra of the same element are separated by a comma,
while spectra of different elements are separated by a semicolon. A
range of spectra is indicated by using a hyphen between stages of
ionization or between names of isoelectronic sequences.

If the user has not provided enough information to specify spectra, an
error message will be displayed.

### Examples of Spectral Notation (Case Insensitive)

  -------------------------------- ----- ----------------------------------------------------------------------------------------------------------------------------
  Na I                                   Neutral sodium
  na 0                                   Neutral sodium
  Na I; Fe I                             Neutral sodium and neutral iron
  Fe I-III                               Fe, ionization stages one, two, and three
  Fe I-III,V                             Fe, ionization stages one, two, three, and five
  Fe                                     All ionization stages of iron
  198Hg I                                Neutral isotope 198 of mercury
  C I; N II; O III                       List of spectra specifying neutral carbon, nitrogen II, and oxygen III.
  C-O C-like                             List of carbon-like spectra of all elements between carbon and oxygen (produces the same results as the previous example).
  C-O I-III                              List of spectra of neutral, singly-ionized, and doubly-ionized elements between carbon and oxygen.
  C-N I-II; Ne IV-V                      List of spectra specifying C I, C II, N I, N II, Ne IV, and Ne V.
  Mg He-like-Li-like; Al Li-like         List of spectra specifying Mg X, Mg XI, and Al XI.
  -------------------------------- ----- ----------------------------------------------------------------------------------------------------------------------------

* * * * *

### Lower and upper limits of the wavelength/wavenumber range

By default, the Search Form prompts the user to enter the lower and
upper limits of line wavelengths in the units selected in the
"**Wavelength Units**" menu. The user can select the "Wavenumber" option
in the drop-down menu of the limit types. Then the expected input in the
"**Lower**" and "**Upper**" input boxes is for the limiting wavenumbers
in units of cm^−1^. The limits can be left blank if the
[Spectra](#LINES_SPECTRA) box is non-blank and no [Graphical Output
Options](#LINES_GRAPH_OPTS) are set.

Note that the wavelength units set in the drop-down menu in the Main
Parameters section apply not only to the wavelength limits, but also to
the output wavelengths. By default, the wavelengths are included in the
output. The user can change the choice of the output columns in the
output and set a number of other options (e.g., whether the wavelengths
are in standard air or in vacuum) in the [Advanced
Settings](#LINES_ADVANCED_OPTS) section of the Search Form. These
settings will be displayed if the user clicks on the "**Show Advanced
Settings**" button.

For the description of the tabular output of the Lines Form, see the
[Output Line Tables](#OUTPUT_LINE) section.

### Graphical Output Options

There are two sets of graphical output options in the Lines Search:

-   Dynamic Plots: [Line Identification](#LINES_INP_ID_PLOT) and
    [Saha/LTE spectrum](#LINES_INP_SAHA_PLOT) plots;
-   [Grotrian Diagrams](#LINES_INP_GROTRIAN)

To show these graphical options, the user must click on the "Show
Graphical Options" button in the Main Parameters section. The contents
and use of the graphical output are explained in the [Graphical
Output](#LINES_OUT_GRAPH) section.

#### Dynamic Plot Options

These options allow graphical display of two types of dynamically
created plots, i.e., line identification plots and Saha-LTE (local
thermodynamic equilibrium) plasma emission plots. The plots are created
as PDF files and require appropriate software (e.g., Adobe Acrobat
Reader or xpdf) for graph display. See the [Graphical
Output](#LINES_OUT_GRAPH) section for the details on the output.\

-   *Line Identification Plot*\
     \
     Selecting this option would produce a PDF file showing positions of
    all spectral lines of the chosen [Spectra](#LINES_SPECTRA) within
    the chosen [wavelength or wavenumber range](#LINES_INP_WL_LIM).\
    \
     The contents and use of the Line Identification Plots are explained
    in the corresponding [Output](#LINES_OUT_ID) section. \
    \
-   *Saha-LTE Spectrum*\
    \
     Selecting this option would produce a PDF file showing line
    emission from an optically thin plasma having the chosen values of
    electron temperature and electron density. The plasma emission is
    generated in arbitrary units. If only one ion/atom is chosen for
    plot generation, then the populations of the energy levels are
    calculated according to the Boltzmann formula ***N~i~* =
    *N*~0~/*g*~0~·*g~i~*·exp(−*E~i~*/*T*~e~)** where *N~i~* is the level
    population, *N*~0~ is the population of the ground state level,
    *g~i~* and *g*~0~ are the statistical weights of the levels, *E~i~*
    is the energy of the level with respect to the ground state in eV,
    and *T*~e~ is the electron temperature in eV to be entered in the
    text field. In this case the electron density *N*~e~ is not required
    to be entered.\
     \
     If several ions/atoms are chosen for plot generation (e.g., "C I-V"
    is entered in the [Spectra](#LINES_SPECTRA) input box), then first
    the ionization distribution between different ions is calculated
    according to the Saha formula (see, e.g., H.R. Griem, Principles of
    Plasma Spectroscopy, 1997), and then within each ion, the
    populations are calculated using the Boltzmann distribution formula.
    In this case both electron temperature and electron density are
    mandatory parameters.\
     \
     The spectrum may be convoluted with the Doppler (Gaussian) line
    profile for each of the spectral lines. To do that, the user must
    check the **Doppler-broadened spectrum** box in the Lines Search
    Form and (optionally) specify the **Ion Temperature** (in eV)
    corresponding to the desired broadening. In practice, experimental
    spectra are broadened by many different mechanisms, e.g.,
    instrumental broadening. To produce a synthetic spectrum resembling
    experimental ones, the user may need to specify an unphysically
    large Ion Temperature. The only meaning of this parameter is the
    broadening it produces.\
     \
     By default (if no Ion Temperature was specified), the entered
    electron temperature ***T~e~*** is used for calculation of the line
    width parameter. An ion temperature ***T~i~*** may be entered if
    ***T~i~*** ≠ ***T~e~***.\
     \
     If a Doppler-broadened spectrum is requested by the user, the
    spectrum will be calculated on a grid with the step size defined by
    the total number of spectral lines of the selected spectra in the
    requested range and by the broadening of each spectral line (i.e.,
    Ion Temperature). The greater the number of lines, the greater is
    the number of grid points required. The greater is the Ion
    Temperature, the lesser grid points are required. To reduce the load
    on our database servers, we are limiting the total number of data
    points in the spectrum grid. If the user's selection requires too
    many grid points, the ASD codes will choose a greater Ion
    Temperature corresponding to the maximum allowed grid points, and a
    warning about it will be displayed in the output.\
     \
     If several chemical elements are involved in the string entered in
    the [Spectra](#LINES_SPECTRA) input box, an additional form will
    appear, requesting the user to enter the percentage abundances of
    each element in the mixture. Such an additional form will also
    appear if the requested Spectra contain hydrogen or deuterium. For
    these spectra, the user must specify whether the resolved fine
    structure or configuration-average wavelengths should be used for
    their lines. For other elements, ASD does not have both these types
    of wavelengths mixed in the tables, so this prompt will not appear.\
     \
     The contents of the output Saha-LTE plots and tables accompanying
    them are explained in the corresponding [Output](#SAHAPLOT) section.

#### Java Grotrian Diagrams

In order to have this feature operational, a user must have the most
current Java Runtime Environment installed on his/her computer. This
software is available for free download from [this
link](http://java.com/).

As of 2017, most browsers stopped supporting Java applets, which are
currently used in ASD to display Grotrian diagrams. One exception is
Internet Explorer, which still displays them in the Microsoft Windows
operating system. However, it requires the user to properly set the Java
security options in the Windows Control Panel. Namely, the Security
Level must be set to "High" and the website https://physics.nist.gov
must be added to the exception list in the Security tab of the Java
settings control. The ASD Team is planning to replace the Java applet
implementation of the Grotrian diagrams with another graphical software.
For now, to enable Grotrian Diagrams on your system, follow the steps
below. You must use the Windows operating system.

1.  Uninstall all versions of Java you have on your computer.
2.  If Internet Explorer is not installed, or its version is \<11,
    install the latest 32-bit version of Internet Explorer and open it.
3.  Go to java.com and install the latest Java version from the big red
    button they display at the top of the screen.
4.  Close all open windows of the Internet Explorer.
5.  Open the Java32 panel in the Windows Control panel.
6.  In the Java tab of the panel, verify that the installed version does
    not have "x64" anywhere in its description. If it does contain
    "x64," go back to the first step and try again.
7.  In the Security tab of Java32, set the Security Level to the lowest
    possible.
8.  Add https://physics.nist.gov to the exceptions list if it is not
    already there.
9.  Close the Internet Explorer and restart it.

The output content and features of interactive Grotrian diagrams are
explained in the [Plotting Java Grotrian diagrams](#OUTPUT_JAVA)
section. The options of the input form are explained below.

***Grotrian Diagram Options on the Lines Form page*** \

-   *Java subwindow size*\
     A user can choose the size of the subwindow showing the Grotrian
    diagram (GD). There are four sizes available (in pixels): 640×640,
    800×640, 1024×768, and 1280×1024.\
    \
-   *Grouping by configuration*\
     Normally the levels are grouped into series according to their
    atomic core configuration. For instance, in O I the levels belonging
    to configurations 2p^3^(^4^S°)nl and 2p^3^(^2^D°)nl would be
    assigned to different series. For ions with multiple cores, it may
    be more convenient to have such levels grouped according to
    configuration only (i.e., the occupation numbers in each electronic
    shell). If such an option is selected by clicking the "**Group by
    configurations**" checkbox, then for the O I case mentioned above
    those levels would belong to the same series of 2p^3^nl.\
    \
-   *Term multiplicity*\
     This option allows display of the levels belonging only to a
    particular term subsystem of the ion. The text entered in the text
    field should be a valid beginning of an atomic term designation. For
    example, entering "3" would result in display of only triplet levels
    and transitions between them, while entering "1P" would produce GD
    only for levels belonging to the ^1^P terms and corresponding
    transitions.\
    \
-   *Show only radiative linked levels*\
     By default, all levels belonging to the chosen ion are displayed in
    the GD. Selecting this option would result in display of only those
    levels that are connected by radiative transitions.\
    \
-   *Make Grotrian Diagram*\
     Pressing the "Make Grotrian Diagram" button creates a Java Grotrian
    diagram on a new page.

### Advanced Settings

The options shown in this block of the Lines Form are divided into three
groups:

-   [Output Options](#LINE_OUTPUT_OPTS) controlling the general layout
    of the output,
-   [Optional Search Criteria](#LINE_OPTIONAL) controlling the range of
    selected data, and
-   [Additional Search Criteria](#LINE_CRITERIA) controlling the scope
    and type of the selected and displayed data.

#### Output Options

The following options apply to all lines and levels searches and are
collectively referred to as output options.

-   Choice of display using an HTML table, an ASCII fixed-column-width
    table, a [CSV or tab-delimted data file](#CSV).
-   Choice of removing Javascript tags in the output (convenient for an
    ASCII table when saving the output into a file)
-   Energy level units. The user may choose between cm^−1^ (default),
    eV, or Rydberg.
-   Choice of viewing the (scrollable) data all at once, or one page at
    a time.
-   Choice of page size. The number of lines displayed on each page of
    the output may be modified so that they would fit the user's screen
    size.
-   Output ordering. The output can be sorted according to either
    [wavelength](#WAVELENGTH_ORD) or [multiplet](#MULTIPLET_ORD) order.
    The multiplet order is available if only ***one*** ion or atom is
    specified in the [Spectra](#LINES_SPECTRA) box.\

    ***Wavelength ordering***

    All spectra are intermingled according to wavelength ordering. A
    spectrum must be provided if no wavelength range is indicated.\

    ***Multiplet ordering***

    Multiplets are transitions that share the same term and
    configuration. Multiplets have been ordered in the transition
    probability compilations according to energies and *g* values of the
    lower and upper levels, and have been assigned arbitrary multiplet
    numbers that reflect this order.

    To view multiplet-ordered data, the user must select the
    "**Multiplet ordering**" radio box.

    In some cases, a multiplet is missing from the numbered list. In
    general, this is because some property of a compiled wavelength or
    level involved is consistent with other more recent compilations,
    such as the NIST energy level data.

    Only the lines with energy level classification are displayed in the
    multiplet-ordered output, and therefore the total number of lines
    shown at the top of the page may be different for wavelength and
    multiplet orderings.

The default is to display output in its entirety as an HTML formatted
table. By default, the levels are displayed in cm^−1^.

For instructions on how to modify options associated with viewing data,
refer to the section [options for viewing data](help.html#VIEWDATA). \

#### Optional Search Criteria

The following search criteria may be specified:

-   Maximum lower level energy.
-   Maximum upper level energy.
-   Preference of whether the transition strength bounds will apply to
    *A~ki~* (default), *f~ik~*, *S*, or log(*gf*) values.
-   Minimum and/or maximum transition strength.
-   Accuracy minimum for *A~ki~*, *f~ik~*, *S*, or log(*gf*).
-   Relative intensity minimum.

#### Additional Search Criteria

The following options apply to all line searches and are collectively
referred to as additional search criteria options.

-   Line selection options:

    -   All lines of data meeting the search criteria,
    -   Only lines with transition probability data,
    -   Only lines with energy level classifications, or
    -   Only lines with observed wavelengths.
    -   Only lines with [plasma-diagnostics
        data](#LINES_OUT_DIAGNOSTICS).

    The default is to display all lines of data meeting the search
    criteria, regardless of whether the lines contain transition
    probability data, energy level classifications, or
    plasma-diagnostics data.

-   Choice of display of the plasma-diagnostics data:

    Plasma diagnostics data were added to ASD when version 5.3 was
    released. For the list of spectra that include these data, refer to
    the [Version History](verhist.shtml) (search for the word
    "diagnostics"). To include the diagnostics data in the Lines output,
    check the corresponding checkbox.

-   Choice of bibliographic information output:

    If the corresponding checkbox is checked, the bibliographic
    references for transition probabilities (TP) and spectral lines will
    be shown in two separate columns.

-   Choice of display of wavelength data:
    -   Observed wavelength
    -   [Ritz](#RITZ) wavelength
    -   The default is to suppress the display of the "observed-Ritz"
        column of data. Checking the "**observed-Ritz**" option will
        cause that column of data to be generated in the output.\
        \
-   Choice of wavelength type:

    The default is to display wavelengths in:\
        Vacuum (\< 200 nm), Air (200 nm to 2,000 nm), Vacuum
    (\> 2,000 nm).

    For wavelength ordered output, the table headings for the wavelength
    columns change as needed to reflect the change in wavelength type.

    For multiplet ordered output, the type of the output value
    (wavelength in air or vacuum or wavenumber, which is always in
    vacuum) and the measurement units are specified in a separate column
    next to the values.

    Alternative choices are:

    -   Vacuum (\< 200 nm), Air (200 nm to 1,000 nm),
        Wavenumber (\> 1,000 nm)
    -   Vacuum (\< 1,000 nm), Wavenumber (\> 1,000 nm)
    -   Vacuum (\< 200 nm), Air (200 nm to 2,000 nm),
        Vacuum (\> 2,000 nm)
    -   Vacuum (all wavelengths)
    -   Vacuum (\< 185 nm), Air ( (\> 185 nm))
    -   Wavenumber (all wavelengths)

    Note that the formula we use for the [refractive index of air](#AIR)
    was experimentally verified in the wavelength range between 185 nm
    and 1690 nm. The refractive index of air is not known for
    wavelengths outside of this range, where air strongly absorbs all
    radiation. For this reason, wavelengths shorter than 185 nm and
    1690 nm cannot be displayed in air. For wavelengths \>1690 nm,
    output of wavelengths in air is allowed, because the formula for the
    refractive index of air behaves smoothly in this range. However, the
    users should be cautious when using such wavelengths, as their
    validity is uncertain.

To change the default, the user simply needs to click on one of the
radio buttons. The user will also need to check appropriate checkboxes
if individual columns of wavelength information are desired:

-   Choice of display of transition strength information. The default is
    to display the following columns of data:

    -   *A~ki~*,
    -   Accuracy,
    -   Relative intensity.

    By default, the *A~ki~* (or *g~k~A~ki~*) are displayed in units of
    s^−1^. They can be displayed in units of 10^8^ s^−1^ if a proper
    checkbox is checked.\
     \
     To suppress display of the Relative Intensity data column, the
    corresponding checkbox can be unchecked.

    Although the *f~ik~*, *S*, and log(*gf*) values are not displayed by
    default, if the corresponding checkboxes are clicked, then those
    data values will be displayed.

-   Choice of transition type:\
     \
     By default, both electric dipole-allowed (E1) and forbidden (M1,
    E2, M2,...) transitions are displayed in the output. To display only
    allowed or only forbidden transitions, a user must uncheck the
    checkbox corresponding to the unwanted type of transitions.\
     \
-   Choice of level information: For lines output, the default is to
    display:

    -   Configurations,
    -   Terms,
    -   Energies, and
    -   *J* values.

    To suppress display of the information listed above, the
    corresponding checkbox can be unchecked.

* * * * *

### Output Line Tables

The output on the screen is HTML-formatted by default, but a
significantly faster ASCII format may also be selected. The output will
be even faster and more suitable for saving and viewing in other
software, such as Excel or other spreadsheet viewers, if the **No
Javascript** box is checked in the [Optional Search
Criteria](#LINE_OPTIONAL) section in the [Advanced
Settings](#LINES_ADVANCED_OPTS) block of the Lines Input Form. This box
is automatically checked when the user selects the ASCII format.
However, it can be unchecked if the output is intended solely for
browsing purposes. The links to the online content of the bibliographic
references are included in the output only if the **No Javascript** box
is not checked. \

***Help popup windows***\

The output may contain some symbols or combinations thereof colored in
red. This means that moving a mouse over such symbols would result in
appearance of a small popup window showing some explanatory text
provided the Javascript language is enabled in the browser options or
preferences. Moving the mouse out would remove the popup window unless a
user clicked on the red symbols. In that case, the popup window remains
visible until the next mouse click on the same symbols. For the
[Ritz](#RITZ) wavelengths, such popup windows appear also for the brown
asterisk and pink plus symbols after the [Ritz](#RITZ) wavelengths (see
[below](#FIGURES)).\

#### Explanation of the Lines Tables

(By Column Heading)

-   [Ion](#OUTELEMENT)
-   [Observed Wavelength, Ritz Wavelength, and Obs.-Ritz
    Wavelength](#OUTWAVELENGTH)
-   [Wavelength Uncertainties](#OUTUNC)
-   [Wavenumbers](#OUTWN)
-   [Rel. Int](#OUTRELINT): Relative Intensity
-   [Transition Strengths](#OUTAKI), [Accuracy](#OUTACC)
-   [*E~i~*-*E~k~*](#OUTENERGIES): Lower level and upper level energies
-   [Configurations](#OUTCONFIGS): Configurations of the lower and upper
    levels
-   [Terms](#OUTTERMS)~ ~: Terms of the lower and upper levels
-   [*J*-values](#OUTJ): the total electronic angular momenta of the
    lower and upper levels
-   [*g~i~*-*g~k~*](#OUTG): Lower level statistical weight
    (*g~i~*=2*J~i~*+1) - upper level statistical weight
    (*g~k~*=2*J~k~*+1)
-   [Type](#OUTTYPE): Transition type and multipolarity: electric
    dipole, magnetic quadrupole, etc.
-   [TP Ref.](/PhysRefData/ASD/Html/lineshelp.html#RTP)
-   [Line Ref.](/PhysRefData/ASD/Html/lineshelp.html#RTP)
-   [Plasma diagnostics data](#LINES_OUT_DIAGNOSTICS)
-   [Line Identification Plots](#LINES_OUT_ID)
-   [Saha-LTE plots](#SAHAPLOT)

* * * * *

#### Ion

This column contains the spectrum name containing an element symbol and
a Roman numeral denoting the spectrum number (I for neutral atom, II for
singly ionized, etc.). This column appears only if multiple spectra have
been specified in the Lines Form input. \

#### Observed Wavelength, Ritz Wavelength, and Obs.-Ritz Wavelength\

The [Ritz](#RITZ) wavelengths are the wavelengths derived from the lower
and upper levels of the transitions. They are available only if both
levels of the transition are known. If they are available, they usually
are more accurate than the observed wavelengths, especially in the
vacuum ultraviolet spectral region. The accuracy of the Ritz wavelengths
depends on the quality of the energy level values. In some cases, the
observed wavelength may be more accurate than the Ritz one, which is
indicated by the number of given [significant figures](#FIGURE) or by
the [uncertainties](#OUTUNC).

The user may choose to display both [Ritz](#RITZ) and observed
wavelengths. The Obs-Ritz value may also be displayed. By default,
wavelengths are given for vacuum wavelengths below 200 nm and above
2000 nm, with standard-air wavelengths in between. Conversion between
the air and vacuum wavelengths used in ASD is explained [here](#AIR).

#### Uncertainties of Observed and Ritz Wavelengths\

Uncertainties of the data can be displayed, if they are available in
ASD, when the corresponding box is checked in the input form (it is
checked by default). If such information is not available, the implied
uncertainty is defined by the number of [significant figures](#FIGURE)
given: it is generally between 2.5 and 25 units of the least significant
figure. However, there are exceptions to this rule. In many cases,
uncertainties of the relative positions of spectral lines can be
measured more accurately than the wavelengths or wavenumbers. This may
require additional significant figures in the wavelength values to avoid
loss of accuracy. The quality of the [Ritz](#RITZ) wavelengths can also
be assessed by estimating the average deviation "Obs.-Ritz" for the
given spectral region. Sometimes, the uncertainties of both observed and
Ritz wavelengths can be retrieved from the bibliographic references
provided for each line or from the Primary Data Source references at the
top of the output page. The user can always choose the best available
wavelength from the ASD output.

All uncertainties given in ASD are meant to be on the level of one
standard deviation.

#### Wavenumbers\

There are two options for displaying wavenumbers in the output page:

-   The "**Wavenumber (all wavelengths)**" radio button can be selected
    in the [Additional Criteria](#LINE_CRITERIA) section of the
    [Advanced Settings](#LINES_ADVANCED_OPTS) block of the Lines Search
    Form.\
     \
     In this case, instead of the observed and [Ritz](#RITZ) wavelengths
    and their uncertainties, the wavenumbers and their uncertainties
    will be displayed, and the "Obs-Ritz" column will contain the
    differences between the observed and Ritz wavenumbers.\
     \
-   The "**Wavenumber**" box can be checked in the [Additional
    Criteria](#LINE_CRITERIA) section of the [Advanced
    Settings](#LINES_ADVANCED_OPTS) block of the Lines Search Form.\
     \
     This option will have an effect only if the "**Wavenumber (all
    wavelengths)**" was not selected (see above). An additional column
    containing the wavenumbers will be included in the output table to
    provide a quick reference to the wavenumber scale corresponding to
    the observed and [Ritz](#RITZ) wavelengths. For lines that have an
    observed wavelength, the value given in this column is the observed
    wavenumber as it is stored in ASD. In some spectra, these values are
    directly quoted from the literature sources for the corresponding
    lines, and their precision may be greater than that of the observed
    wavelengths. However, in most cases they were calculated from the
    observed wavelengths (using the standard [air to vacuum](#AIR)
    conversion where appropriate) and rounded according to the "rule of
    25."\
     \
     For lines that do not have an observed wavelength, the value given
    is the [Ritz](#RITZ) wavenumber, and it is shown in italics.

The [Ritz](#RITZ) wavenumbers in the ASD output are always calculated
from the energy levels stored in ASD.

* * * * *

#### Significant Figures

The number of significant figures in the ASD output values is determined
by two considerations:

-   Uncertainty of the value should be no less than 2.5 units of the
    least significant figure of the value. This is dictated by
    statistical properties of rounded decimal numbers. All uncertainties
    given in ASD are meant to be on the level of one standard deviation.
-   The given energy levels and wavelengths should be internally
    consistent.

About 90 % of data stored in ASD conforms to the [rule of 25](#RULE25):
the uncertainty is between 2.5 and 25 units of the least significant
figure. Most of the exceptions are of the three origins:

-   Legacy data.\
     \
     Some early researchers rounded their measured data too harshly with
    the intention of giving the data thought to be valid to the last
    given figure. Besides the fact that it is impossible in principle
    (there is always a finite probability that the rounded value
    contains an incorrect last digit), such rounding precludes the use
    of the results in rigorous statistical analyses.\
     \
-   Systematic errors in measurements.\
     \
     In some cases, absolute positions of measured wavelengths contain
    poorly known systematic shifts and thus are of poor accuracy, but
    separations between them could be measured much more accurately.
    This requires giving additional figures in the wavelength values to
    avoid loss of accuracy.\
     \
-   Theoretical data.\
     \
     It is especially difficult to estimate uncertainties of purely
    theoretical data. Systematic errors caused by approximations used in
    the calculation may lead to poor absolute accuracy, but the
    intervals between the calculated energy levels may be much more
    accurate. In such cases, we may give more significant figures than
    justified by the total uncertainty. This concerns the [Ritz](#RITZ)
    wavelengths derived from purely theoretical levels.

More details are given below for the number of significant figures given
for observed and [Ritz](#RITZ) wavelength and wavenumbers and their
uncertainties.

#### *Wavelengths*

Precision of the given wavelengths is governed by their uncertainties,
so we start with the determination of the uncertainty. If the
uncertainty has been critically evaluated and is stored in ASD, we use
this stored uncertainty value. Otherwise, we estimate the uncertainty of
an observed wavelength as ten units of the least significant figure of
the wavelength. For [Ritz](#RITZ) wavelengths with no critically
evaluated uncertainty, we start with determining the uncertainties of
the energy levels. If their critically evaluated values are available in
ASD, we use them; otherwise, we estimate them as ten units of the least
significant figure of the energy. Then we combine the level
uncertainties in quadrature to obtain an estimated uncertainty of the
Ritz wavenumber. This is used to derive the estimated uncertainty of the
Ritz wavelength.

When there is no stored [Ritz](#RITZ) wavelength value in ASD, it is
calculated online from the available energies of the lower and upper
levels, and either an asterisk "\*" or a plus "+" is appended to the
Ritz wavelength value. The former simply indicates that this value was
calculated online, while the latter points out that there are no
critically evaluated values of the level uncertainties in ASD, and their
estimation involves a number of trailing zeros in the stored energies,
which were presumed insignificant. Therefore, the actual accuracy of the
Ritz wavelengths followed by "+" may be higher. This involves only the
energy values that do not contain a decimal point, usually in highly
ionized atoms.

The subsequent procedure depends on the type of wavelength to be
displayed: in vacuum or air.

-   If the wavelength is to be displayed in vacuum,
    -   Observed wavelengths are displayed with the same relative
        precision as they are stored, regardless of the uncertainty. The
        latter is given with the same precision as the wavelength.
    -   [Ritz](#RITZ) wavelengths are always calculated from the energy
        levels. If we have a stored critically evaluated value of the
        Ritz wavelength, its precision is preserved in the output.
        Otherwise, it is rounded according to the [rule of 25](#RULE25)
        using the stored or estimated uncertainty value. Estimated
        uncertainties are not displayed in ASD, as they are not
        critically evaluated. Critically evaluated uncertainties are
        displayed with the same precision as the Ritz wavelengths.\
         \
         Precision of the stored [Ritz](#RITZ) wavelengths overrides the
        [rule of 25](#RULE25) for the following reason:\
         \
         There are many cases when the energy levels derived from
        observed wavelengths are strongly correlated, i.e., the
        intervals between them are known more accurately than the energy
        levels themselves (which are defined as separations from the
        ground level). In such cases, more significant figures may be
        required to adequately represent the data precision.
-   If the wavelength is to be displayed in air,
    -   If the uncertainty of the [air refractive index](#AIR) δ*n*/*n*
        is less than 10 % of the relative uncertainty of the wavelength,
        the wavelength uncertainty is not modified, and the precision of
        the output values is determined by the same rule as for vacuum
        wavelengths (see above).
    -   Otherwise, the relative uncertainty of the wavelength δ*λ*/*λ*
        is combined in quadrature with δ*n*/*n*. If the latter is
        smaller than half of the wavelength uncertainty stored in ASD,
        the number of significant figures in both the wavelength and its
        increased uncertainty will be preserved as stored in ASD.
        Otherwise, both are rounded according to [rule of 25](#RULE25).
        ASD displays critically evaluated uncertainties only.

####  *Wavenumbers*

Observed wavenumbers stored in ASD are always shown as is, in units of
cm^−1^. They may differ from the values derived from the observed
wavelengths by a few units of the least significant figure due to
rounding errors. If there is no stored value in ASD, but there is an
observed wavelength, the observed wavenumber is calculated from the
wavelength, and its value is rounded according to the [rule of
25](#RULE25) using the stored or estimated uncertainty of the observed
wavelength.

The [Ritz](#RITZ) wavenumbers are calculated from the energy levels
stored in ASD. Their precision is entirely determined by their
uncertainties, either stored in ASD (if they were critically evaluated)
or estimated from the uncertainties of the energy levels by combining in
quadrature the uncertainties of the lower and upper level of the
transition. If there are no stored critically evaluated uncertainties of
the levels, they are estimated as ten units of the least significant
figure of the level value. Then the wavenumber value is rounded
according to the [rule of 25](#RULE25).

#### Definition of Ritz wavelength and wavenumber

"Ritz" wavenumbers are derived from level energies via the Ritz
principle: the wavenumber *σ* of the emitted or absorbed photon is equal
to the difference between the upper and lower energies *E~k~* and
*E~i~*,

*σ* = *E~k~* − *E~i~*.

The Ritz wavelength *λ* in vacuum is equal to the inverse of *σ*. If *σ*
is in units of cm^−1^, and *λ* is in nanometers,

*λ*~vac~ [nm] = 10^7^/(*σ* [cm^−1^]).

Wavelengths in air are decreased by the [refractive index of air](#AIR).

#### Rounding Rule of 25

A numerical value given in decimal representation is considered to be
properly rounded if its uncertainty in the unit of the least significant
figure is between 2.5 and 25.

If the rounding is too harsh, i.e., the uncertainty is smaller than 2.5
units of the least significant figure, the value of the uncertainty is
statistical meaningless and the rounded value cannot be used in rigorous
statistical analyses. See more about it in A. E. Kramida, [Comput. Phys.
Commun. **182**, 419–434
(2011)](http://dx.doi.org/10.1016/j.cpc.2010.09.019).

If the rounding is too mild, i.e., the uncertainty is greater than 2.5
units of the least significant figure, the precision of the value cannot
be used to estimate the uncertainty. In cases when there are strong
correlations between the given values, mild rounding may be needed to
adequately represent the *relative* uncertainties of the presented data.

#### Conversion between air and vacuum wavelengths

In vacuum, the wavelength *λ*~vac~ is directly determined by the
wavenumber *σ* (see [above](#RITZ)). In air, it is decreased by the
refractive index *n*:

*λ*~air~  = *λ*~vac~/*n*.

In ASD, the index of refraction of air is derived from the
five-parameter formula given by E.R. Peck and K. Reeder, [J. Opt. Soc.
Am. **62**, 958 (1972)](http://dx.doi.org/10.1364/JOSA.62.000958). These
authors fitted data between 185 nm and 1700 nm. The conversion between
air and vacuum wavelength entails an ambiguity near the boundary of the
air region. For example, a wavelength of 200.0648 nm in vacuum
corresponds to 200.0000 nm in "standard air" (i.e., 15 °C, 101 325 Pa
pressure, with 0.033 % CO~2~). Conversely, an air wavelength of
199.9352 &nm corresponds to 200.0000 nm in vacuum. In this database, as
the default, the following convention is adopted in terms of the energy
difference or wavenumber, *σ*=*E~k~*-*E~i~*:

  ----------------------------------------- -----------------------
  For *σ* ≥ 50,000 cm^−1^                   → vacuum wavelengths,
  For 5000 cm^−1^ \< *σ* \< 50,000 cm^−1^   → air wavelengths,
  For *σ* ≤ 5000 cm^−1^                     → vacuum wavelengths.
  ----------------------------------------- -----------------------

\

Thus, if the tabulated wavelength lies within 200 ± 0.0648 nm, one must
check the energy difference to ascertain whether it is for vacuum or
air.

The relative uncertainty δ*λ*/*λ* of the formula of Peck & Reeder is
5×10^−9^ for wavelengths *λ* \> 400 nm and increases according to the
approximate formula

δ*λ*/*λ* ≈ (0.35734 + 38.24/(*λ* − 180.29) + 0.000023*λ*)×10^−8^

for shorter wavelengths (*λ* is in nm). The maximum uncertainty is about
9×10^−8^ at 185 nm.

It should be noted that a number of other formulas for the refractive
index of air exist in the literature. In particular, the formulas given
by K. P. Birch and M. J. Downs, [Metrologia **31**, 315–316
(1994)](http://dx.doi.org/10.1088/0026-1394/31/4/006) have a five times
lower uncertainty than the formula of Peck & Reeder, but only in a
restricted wavelength range from 350 nm to 650 nm. Their validity in the
extended wavelength region covered by the Peck & Reeder formula has
never been verified.

Similarly, the "corrected" formulas given by P. E. Ciddor, [Appl. Opt.
**35**, 1566–1573 (1996)](http://dx.doi.org/10.1364/AO.35.001566) are
valid only in the wavelength range from 350 nm to 1200 nm and give
increasingly large errors for shorter wavelengths: about −1.0×10^−8^ at
228 nm and −1.6×10^−6^ at 185 nm.

#### Relative Intensity

Relative intensities are source dependent and typically are useful only
as guidelines for low density sources.

These are values intended to represent the strengths of the lines of a
spectrum as they would appear in emission. The values in the Database
are taken from the cited publications. Usually, they are not normalized
in any way. In some cases, the intensity values were derived from
observed photometric signals. This would be true for spectra measured by
Fourier transform spectroscopy or in special cases where spectra were
recorded photometrically. However, in most cases the values represent
blackening of photographic emulsions used to record an observed
spectrum. These values can be semi-quantitative in that the transmission
of the blackened emulsion was quantitatively measured and used to
determine the intensity values. In other cases, the blackening was
estimated visually and the estimates were used for the intensity values.
Thus, the values can range from being approximately quantitative to only
qualitative. *Since the Database does not contain information on the
origin of the relative intensities, the relative intensities should be
considered as qualitative values that describe the appearance of a
particular spectrum in emission*.

The following points should be kept in mind when using the relative
intensities:

1.  There is no common scale for relative intensities. The values in the
    database are taken from the values given by the authors of the cited
    publications. Since different authors use different scales, the
    relative intensities have meaning only within a given spectrum; that
    is, within the spectrum of a given element in a given stage of
    ionization.
2.  The relative intensities are most useful in comparing strengths of
    spectral lines that are not separated widely. This results from the
    fact that most relative intensities are not corrected for spectral
    sensitivity of the measuring instruments (spectrometers,
    photomultipliers, photographic emulsions).
3.  The relative intensities for a spectrum depend on the light source
    used for the excitation. These values can change from source to
    source, and this is another reason to regard the values as being
    only *qualitative*.

Descriptors to the relative intensities have the following meaning:

         *    Intensity is shared by several lines (typically, for multiply classified lines).
         :    Observed value given is actually the rounded Ritz value, e.g., Ar IV, λ = 443.40 Å.
         -    Somewhat lower intensity than the value given.
         a    Observed in absorption.
         b    Band head.
         bl   Blended with another line that may affect the wavelength and intensity.
         B    Line or feature having large width due to autoionization broadening.
         c    Complex line.
         d    Diffuse line.
         D    Double line.
         E    Broad due to overexposure in the quoted reference
         f    Forbidden line.
         g    Transition involving a level of the ground term.
         G    Line position roughly estimated.
         H    Very hazy line.
         h    Hazy line (same as "diffuse").
         hfs  Line has hyperfine structure.
         i    Identification uncertain.
         j    Wavelength smoothed along isoelectronic sequence.
         l    Shaded to longer wavelengths; NB: This may look like a "one" at the end
              of the number!
         m    Masked by another line (no wavelength measurement).
         p    Perturbed by a close line. Both wavelength and intensity may be affected.
         q    Asymmetric line.
         r    Easily reversed line.
         s    Shaded to shorter wavelengths.
         t    Tentatively classified line.
         u    Unresolved from a close line.
         w    Wide line.
         x    Extrapolated wavelength

Other characters occasionally appearing in the intensity column are
explained in the quoted literature.

The difficulty of obtaining reliable relative intensities can be
understood from the fact that in optically thin plasmas the intensity of
a spectral line is proportional to:

*I~ik~ ![Proportional to](/Images/propto.gif) N~k~A~ki~h*ν*~ik~*,

where *N~k~* is the number of atoms in the upper level *k* (population
of the upper level), *A~ki~* is the transition probability for
transitions from upper level *k* to lower level *i*, and *h*ν*~ik~* is
the photon energy (or the energy difference between the upper level and
lower level). Although both *A~ki~* and **ν*~ik~* are well defined
quantities for each line of a given atom, the population values *N~k~*
depend on plasma conditions in a given light source, and they are thus
different for different sources.

#### Transition Strengths

Either transition probability "*A~ki~*" weighted transition probability
"*g~k~A~ki~*" (s^−1^ or 10^8^ s^−1^), absorption oscillator strength or
f value ("*f~ik~*"), line strength "*S*", or "log(*gf*)" can be
displayed. Note that *f~ik~*, *S*, and log(*gf*) are not displayed by
default. Also note that log(*gf*) is shorthand for log~10~(*g~i~
f~ik~*).

> *A~ki~* represents the emission transition probability. In the following formulas, it is assumed to be in units of 10^8^ sec^−1^.
> :   \
> *f~ik~* is the absorption oscillator strength or *f*-value.
> :   *f~ik~* = *A~ki~* **·**1.49919**·**10^−16^ *g~k~*/*g~i~* *λ*^2^,
>     for all multipole types,\
>      where *λ* is the wavelength in ångströms\
>     \
> log(*gf*) is the log~10~(*g~i ~f~ik~*), where *g~i~* = 2*J~i~* + 1.
> :   \
> *S* is the line strength. It is the electric dipole matrix element squared and is independent of the transition wavelength.
> :   \
> More details on these quantities can be found in [this review](https://physics.nist.gov/Pubs/AtSpec/index.html).
> :   

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

#### Accuracy

An estimated accuracy is listed for each transition strength, indicated
by a code letter as given in the table below: \
\

  --------- ---- ------
  **AAA**   ≤    0.3%
  **AA**    ≤    1%
  **A+**    ≤    2%
  **A**     ≤    3%
  **B+**    ≤    7%
  **B**     ≤    10%
  **C+**    ≤    18%
  **C**     ≤    25%
  **D+**    ≤    40%
  **D**     ≤    50%
  **E**     \>   50%.
  --------- ---- ------

The uncertainties are obtained from critical assessments, and in
general, reflect estimates of predominantly systematic effects discussed
in the NIST critical compilations, cited in the
[Bibliography](/PhysRefData/datarefs/datarefs_search_form.html).
Accuracies are not available for values listed in the CRC handbook.

If the accuracy is followed by a prime (′), then a multiplet in the
original compilation has been separated into its component lines and the
transition probability was derived from the compiled value assuming
spin-orbit coupling. This may decrease the listed accuracy, especially
for weaker transitions.

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*

#### *Conversion between transition probabilities and line strengths*

Transition multipole: Multiply *A~ki~* by listed factor to get *S*: \

` E1   Electric dipole                 4.935525·10−19 gk λ3 M1   Magnetic dipole                 3.707342·10−14 gk λ3 E2   Electric quadrupole             8.928970·10−19 gk λ5 M2   Magnetic quadrupole             6.707037·10−14 gk λ5 E3   Electric octupole               3.180240·10−18 gk λ7 M3   Magnetic octupole                2.38885·10−13 gk λ7 `

where *λ* is the [wavelength](#OUTWAVELENGTH) in angstroms and *g~k~* is
the statistical weight of the upper level. The numerical factor for the
electric quadrupole conversion from *A~ki~* to *S* follows a more modern
convention than that used in the original publications, which will be
used in future NIST publications.

#### *E~i~*-*E~k~*

Lower level and upper level energies of the transition are displayed in
the units specified. Note that, if the units other than cm^−1^ are
requested in the [Lines Search Form](#LINES_ADVANCED_OPTS),
uncertainties of the [conversion factors](levelshelp.html#LOUTUNC) are
combined in quadrature with the uncertainties of the energy levels,
which may result in loss of precision. However, the [Ritz](#RITZ)
wavelengths and wavenumbers are always calculated from the stored energy
levels in units of cm^−1^, so their precision is not affected.

If the "No Javascript" checkbox is not checked, the level energies
appear in the output as active links, even if the ASCII format is
chosen. Clicking on such an active level-value link will open a new tab
containing a list of all lines originating from or terminating on this
level.

#### Configurations

Configurations of the lower and upper levels are displayed. For ASCII
output, periods are inserted in the configuration labels whenever
necessary to avoid ambiguity due to the lack of superscripts, and
angular brackets enclose *J* values of the parent term.

#### [Terms](/PhysRefData/ASD/Html/levelshelp.html#LOUTTERM)~ ~

Terms of the lower and upper levels are displayed. A superscript "°" in
the HTML output or an asterisk in the ASCII output indicates odd parity.

#### *J*-values

The ***J***-values represent the total electronic angular momentum of
the lower and upper levels.

#### *g~i~*-*g~k~*

*g~i~*-*g~k~* represents statistical weight of the lower level
(*g~i~*=2*J~i~*+1) and statistical weight of the upper level
(*g~k~*=2*J~k~*+1).\

#### Type

This filed is blank for allowed (electric-dipole, or E1) transitions,
including the spin-changing (intercombination) transitions. Types of
forbidden transitions are denoted as follows:

` M1    - Magnetic dipole. E2    - Electric quadrupole. M2    - Magnetic quadrupole. E3    - Electric octupole. M3    - Magnetic octupole. M1+E2 - Mixed magnetic dipole and electric quadrupole transition.         The selection rules for these two types of transitions are the same, so         both types of transitions can contribute to the observed intensity and         radiative rate Aki. The line strength is undefined for such mixed transitions. 2P    - Two-photon transition. HF    - Hyperfine-induced transition (may occur only in isotopes with a         non-zero nuclear magnetic moment). UT    - Forbidden transition of an unspecified type.`

Transitions that are strongly forbidden in isolated atoms may be enabled
by environmental effects such as external electric or magnetic fields.
Such forbidden transitions would be denoted as type = UT in ASD.

The conversion formulas between transition probabilities and line
strengths for different types of allowed and forbidden transitions are
given [here](#MULTIPOLE).

#### TP Ref. and Line Ref.

There may be several reference codes separated by comma in each of these
columns. If the "**No Javascript**" box was not checked in the [Lines
Search Form](#LINES_ADVANCED_OPTS), each bibliographic code links to a
popup window showing a bibliographic reference for transition
probability or for the observed spectral line.\
 \

#### Plasma diagnostics data

For those lines that have diagnostic data in ASD, an additional column
of the [Lines Tabular Output](#OUTPUT_LINE) contains links to detailed
information about the line pairs whose relative intensities can be used
to determine the plasma temperature and/or density. The diagnostic data
include plots of intensity ratios versus electron temperature or density
and specifications of the validity range of these plots.\
 \

### Graphical Output

###  Dynamic Plots

#### Line Identification Plot

If the "Line Identification Plot" option has been selected on the [Lines
Form](#LINES_FORM), two links will appear at the very bottom of the
[tabular output](#OUTPUT_LINE) page, i.e., a link to a PDF file
containing an image of the plot and a link to a new popup window
displaying the wavelengths of the spectral lines shown on the PDF plot.

The Line Identification Plot is a stick plot showing the line positions
for all chosen ions in the given wavelength range. It can be used to
diagnose which ions produce spectral lines is an observed spectrum. For
that, the image should be magnified or reduced to approximately the same
wavelength scale as in the experimental spectrum. Then the patterns of
intervals between the observed spectral lines could be matched with
those in one or more of the ion spectra in the Line Identification Plot,
which can help the user to identify the observed lines.

If there are too many lines in the chosen spectra, the user can use the
"**Relative intensity minimum**" or other options in the [Optional
Search Criteria](#LINE_OPTIONAL) section in the [Advanced
Settings](#LINES_ADVANCED_OPTS) block of the Lines Input Form to reduce
the number of shown lines.

#### Saha-LTE Spectrum Plots

The Saha-LTE plot shows the distribution of calculated intensities in
the plasma emission spectrum for the chosen ions within the selected
wavelength range.

If the "Saha-LTE Plot" option has been selected on the Lines Form, two
or more links will appear at the very bottom of the [tabular
output](#OUTPUT_LINE) page. One of them is a link to a PDF file
containing an image of the plot. One of the other links with text
"**Relative Line Intensities**" is to a new popup window displaying the
wavelengths of the spectral lines shown on the PDF plot and their
relative intensities. If the user requested a **Doppler-broadened
spectrum** (by checking the corresponding box in the Lines Form), there
will be two additional links, one to table of calculated intensities of
each ion in the Doppler-broadened spectrum, and one to a table showing
the distribution of intensities in the total spectrum (sum of
contributions from each ion). Both these tables are two-column plane
fixed-column-width ASCII files with the first column having the
wavelength grid points and the second column having relative intensities
in arbitrary units. These tables can be used to plot the spectra with
other software.

The header of the plot shown in the PDF file shows the user-defined
parameters: composition of the element mixture in the plasma, electron
temperature and density, as well as the total number of lines in the
synthetic spectrum. If a **Doppler-broadened spectrum** was requested,
the header also shows the ion temperature used to calculate the Doppler
broadening. It may be greater than the [Ion
Temperature](#LINES_INP_IONTEMP) specified by the user in the Lines
Input Form, if the number of required points in the grid was too large
for the given selection of spectral lines. In such cases, to display
narrower lines (corresponding to a lower ion temperature), the user
needs to reduce the selected [wavelength range](#LINES_INP_WL_LIM),
reduce the number of requested [spectra](#LINES_SPECTRA), or use some
line-filtering options in the [Optional Search Criteria](#LINE_OPTIONAL)
section in the [Advanced Settings](#LINES_ADVANCED_OPTS) block of the
Lines Input Form.

If higher resolution (narrower lines) is needed, and only neutral,
singly-ionized, or doubly-ionized atoms are involved, consider using the
[LIBS Interface](../LIBS/libs-form.html) of ASD. Although this interface
does not allow drawing spectra for a particular ionization stage, its
plots can be calculated on the user's computer with much higher
resolution, and they have flexible interactive features.

###  Plotting Java Grotrian diagrams

***Working with the Grotrian diagram plot***\

Basically, only a computer mouse and a space bar are used for
interaction with this plot. \

-   *Default view*\
    \
     Initially all levels and transitions are shown on the plot. Each
    energy level is shown by a horizontal bar. The colors (black and
    blue) have no meaning and are used simply to help with visualization
    of the plot. The X-axis corresponds to different level series, and
    the Y-axis shows the level energy in cm^−1^. The radiative
    transitions between the levels are shown as slanted gray lines. The
    ionization limits are shown as magenta horizontal lines. At the top
    of the plot, the total number of levels, lines and ionization limits
    is displayed. These parameters are automatically updated when
    zooming in or out. In the bottom right part of the plot, the maximum
    and minimum values of the transition probability for the displayed
    lines are given in the input text fields. The "Submit" and "Reset"
    buttons are used for setting the limits for transition
    probabilities, while the "Isolate" button is used to single out one
    level and all relevant transitions. The green field ("zoom field"
    below) next to the Y-axis is used for zooming in and out. Below, the
    top right part of the plot will be referred to as the "info field."\

-   *Selecting, deselecting and cycling over objects*\
     \
     Mouse: \
    -   Clicking on any **level** colors it and all relevant transitions
        in red. In addition, the basic data on this level, e.g., energy,
        configuration, etc., are displayed in the info field.
    -   Clicking on any **line** colors the line and the lower and upper
        level in red. In addition, the basic data on the levels and line
        (wavelength, transition probability, etc.) are shown in the info
        field.
    -   Consecutive clicking on **two levels** is equivalent to clicking
        on the corresponding spectral line. If there is no line
        connecting the levels, no Line information is shown in the info
        field although the data on both levels is displayed.
    -   Clicking anywhere in the white background of the GD subwindow
        **deselects** the already selected object(s).\
        \

    Space bar:\
    -   If no objects have been selected, pressing a space bar selects a
        first spectral line in the following order: the levels are
        assumed to be arranged first according to the X-axis label (from
        left to right) and then according to the level energy. Since the
        ground state always has a zero energy, pressing the bar would
        normally highlight a line originating from the ground state.
    -   If a line has been selected, pressing a space bar cycles over
        all spectral lines on the plot in the order described above,
        that is, (i) for the same lower level, the upper level is
        updated, and (ii) after all lines for a particular lower level
        have been cycled through, the lower level is updated, and so on.
    -   If a level has been selected, pressing a space bar cycles over
        all energy levels within the levels series.
    -   The data shown in the info field is the same as for the mouse
        selection.\
        \
-   *Zooming in and out*\
     \
     The green field to the right of the Y-axis is used for zooming in.
    The upper and lower limits for the energy levels are set up by
    clicking the mouse in the zoom field. The upper and lower limits are
    shown by horizontal blue lines. When both limits are selected, the
    "Zoom" button above the Y-axis becomes highlighted and clicking on
    it with the mouse results in updating the subwindow. This procedure
    can be repeated infinitely. After zooming in, the "Reset" button on
    the above the Y-axis becomes highlighted, and clicking on it
    restores the *original* plot.\
    \
-   *Filtering A-values*\
     \
     To choose the limits for the radiative transition probabilities, a
    user must enter new values in the "minA" and "maxA" text fields in
    the bottom right part of the plot and press the "Submit" button. By
    default, the minimum and maximum values of transition probabilities
    for all lines shown on the plot are displayed in those fields. The
    "Reset" button restores the default limits.\
    \
-   *Isolating a level*\
     \
     In order to isolate one energy level with all radiatively connected
    levels, one has first to select a level by a mouse click. Then, the
    "Isolate" button in the bottom right part of the plot becomes
    highlighted, and pressing it would result in displaying the red
    group of levels and lines only. If necessary, a user can then
    perform zoom or transition probability limiting procedures on this
    subset of levels. After isolating a level, the "Isolate" button
    changes its label to "Show All," and pressing this new button would
    show all available levels and transitions.

