#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of helpers for using a PI device."""

from collections import OrderedDict
from io import open  # Redefining built-in 'open' pylint: disable=W0622
from logging import debug, info, warning
from time import sleep, time

from zialab.instruments.pipython import GCSError, gcserror
from zialab.instruments.pipython.gcscommands import getgcsheader, getitemsvaluestuple
from zialab.instruments.pipython.piparams import applyconfig

__signature__ = 0xb88ce55451588a0561a537d9c4467bbf


class DeviceStartup(object):  # Too many instance attributes pylint: disable=R0902
    """Provide a "ready to use" PI device."""

    DEFAULT_SEQUENCE = (
        'setstages', 'setaxesnames', 'callini', 'enableonl', 'stopall', 'waitonready', 'enableaxes', 'referencewait',
        'resetservo', 'waitonready',)
    SPECIAL_SEQUENCE = {
        'HYDRA': [x for x in DEFAULT_SEQUENCE if x not in ('callini',)],
        'C-887': [x for x in DEFAULT_SEQUENCE if x not in ('stopall',)],
    }

    def __init__(self, pidevice, **kwargs):
        """Provide a "ready to use" PI device.
        @type pidevice : pipython.gcscommands.GCSCommands
        @param kwargs : Optional arguments with keywords that are passed to sub functions.
        """
        debug('create an instance of ControllerStartup(kwargs=%s)', itemstostr(kwargs))
        self.pidevice = pidevice
        self._stages = None
        self._refmodes = None
        self._servo = None
        self._axesnames = None
        self._kwargs = kwargs
        self._databuf = {'servobuf': {}, }
        self.prop = {
            'devname': self.pidevice.devname, 'skipcst': False, 'forcecst': False, 'skipsai': False,
            'forcesai': False, 'showlog': False, 'skipini': False, 'skiponl': False, 'skipeax': False,
            'skipref': False, 'forceref': False,
        }

    @property
    def stages(self):
        """Name of stages as list of strings or None."""
        return self._stages

    @stages.setter
    def stages(self, stages):
        """Name of stages to initialize as string or list (not tuple!) or None to skip.
        Skip single axes with "" or None as item in the list.
        """
        if stages is None:
            self._stages = None
        else:
            self._stages = stages if isinstance(stages, list) else [stages] * len(self.pidevice.allaxes)
        debug('ControllerStartup.stages = %s', itemstostr(self._stages))

    @property
    def refmodes(self):
        """Referencing commands as list of strings or None."""
        return self._refmodes

    @refmodes.setter
    def refmodes(self, refmodes):
        """Referencing command as string (for all stages) or list (not tuple!) or None to skip.
        Skip single axes with "" or None as item in the list.
        """
        if refmodes is None:
            self._refmodes = None
        else:
            self._refmodes = refmodes if isinstance(refmodes, list) else [refmodes] * len(self.pidevice.allaxes)
        debug('ControllerStartup.refmodes = %s', itemstostr(self._refmodes))

    @property
    def servostates(self):
        """Servo states as dict {axis: state} or None."""
        if isinstance(self._servo, bool):
            return dict(list(zip(self.pidevice.axes, [self._servo] * self.pidevice.numaxes)))
        return self._servo

    @servostates.setter
    def servostates(self, servo):
        """Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip."""
        self._servo = servo
        debug('ControllerStartup.servostates = %s', itemstostr(self._servo))

    @property
    def axesnames(self):
        """Name of axes as list of strings or None."""
        return self._axesnames

    @axesnames.setter
    def axesnames(self, axesnames):
        """Name of axes to set as list of strings (not tuple!) or None to skip."""
        if axesnames is None:
            self._axesnames = None
        else:
            assert isinstance(axesnames, list), 'axesnames must be list'
            self._axesnames = axesnames
        debug('ControllerStartup.axesnames = %s', itemstostr(self._axesnames))

    def run(self):
        """Run according startup sequence to provide a "ready to use" PI device."""
        debug('ControllerStartup.run()')
        sequence = self.SPECIAL_SEQUENCE.get(self.prop['devname'], self.DEFAULT_SEQUENCE)
        for func in sequence:
            getattr(self, '%s' % func)()

    def setstages(self):
        """Set stages if according option has been provided."""
        if not self._stages or self.prop['skipcst']:
            return
        debug('ControllerStartup.setstages()')
        allaxes = self.pidevice.qSAI_ALL()
        oldstages = self.pidevice.qCST()
        for i, newstage in enumerate(self._stages):
            if not newstage:
                continue
            axis = allaxes[i]
            oldstage = oldstages.get(axis, 'NOSTAGE')
            if oldstage != newstage or self.prop['forcecst']:
                warnmsg = applyconfig(self.pidevice, axis, newstage)
                if self.prop['showlog'] and warnmsg:
                    warning(warnmsg)
            elif self.prop['showlog']:
                info('stage %r on axis %r is already configured', oldstage, axis)

    def setaxesnames(self):
        """Set stages if according option has been provided."""
        if not self._axesnames or self.prop['skipsai']:
            return
        debug('ControllerStartup.setaxesnames()')
        oldaxes = self.pidevice.qSAI()
        for i, newaxis in enumerate(self.axesnames):
            if newaxis != oldaxes[i] or self.prop['forcesai']:
                self.pidevice.SAI(oldaxes[i], newaxis)

    def callini(self):
        """Call INI command if available."""
        debug('ControllerStartup.callini()')
        if not self.pidevice.HasINI() or self.prop['skipini']:
            return
        self.pidevice.INI()

    def enableonl(self):
        """Enable online state of connected axes if available."""
        debug('ControllerStartup.enableonl()')
        if not self.pidevice.HasONL() or self.prop['skiponl']:
            return
        self.pidevice.ONL(list(range(1, self.pidevice.numaxes + 1)), [True] * self.pidevice.numaxes)

    def stopall(self):
        """Stop all axes."""
        debug('ControllerStartup.stopall()')
        stopall(self.pidevice, **self._kwargs)

    def waitonready(self):
        """Wait until device is ready."""
        debug('ControllerStartup.waitonready()')
        waitonready(self.pidevice, **self._kwargs)

    def resetservo(self):
        """Reset servo if it has been changed during referencing."""
        debug('ControllerStartup.resetservo()')
        if self.servostates is not None:
            setservo(self.pidevice, self.servostates)
        elif self._databuf['servobuf']:
            setservo(self.pidevice, self._databuf['servobuf'])

    def referencewait(self):
        """Reference unreferenced axes if according option has been provided and wait on completion."""
        debug('ControllerStartup.referencewait()')
        if not self.refmodes or self.prop['skipref']:
            return
        self._databuf['servobuf'] = self.pidevice.qSVO()
        toreference = {}  # {cmd: [axes]}
        for i, refmode in enumerate(self._refmodes[:self.pidevice.numaxes]):
            if not refmode:
                continue
            axis = self.pidevice.axes[i]
            refmode = refmode.upper()
            if refmode not in toreference:
                toreference[refmode] = []
            if refmode not in ('POS',) and not self.prop['forceref']:
                qrefcmd = self.pidevice.qREF if refmode == 'REF' else self.pidevice.qFRF
                if qrefcmd(axis)[axis]:
                    debug('axis %r is already referenced', axis)
                    continue
            toreference[refmode].append(self.pidevice.axes[i])
        waitonaxes = []
        for refmode, axes in toreference.items():
            if not axes:
                continue
            if refmode == 'POS':
                self._ref_with_pos(axes)
            else:
                self._ref_with_refcmd(axes, refmode)
                waitonaxes += axes
        waitonreferencing(self.pidevice, axes=waitonaxes, **self._kwargs)

    def _ref_with_refcmd(self, axes, refmode):
        """Enable RON, change servo state if appropriate and reference 'axes' with the 'refmode' command.
        @param axes : Axes to reference as list or tuple of strings, must not be empty.
        @param refmode : Name of command to use for referencing as string.
        """
        debug('ControllerStartup._ref_with_refcmd(axes=%s, refmode=%s)', axes, refmode)
        for axis in axes:
            if self.pidevice.HasRON():
                try:
                    self.pidevice.RON(axis, True)
                except GCSError as exc:
                    if exc == gcserror.E34_PI_CNTR_CMD_NOT_ALLOWED_FOR_STAGE:
                        pass  # hexapod axis
                    else:
                        raise
            try:
                getattr(self.pidevice, refmode)(axis)
            except GCSError as exc:
                if exc == gcserror.E5_PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO:
                    self._databuf['servobuf'][axis] = self.pidevice.qSVO(axis)[axis]
                    self.pidevice.SVO(axis, not self._databuf['servobuf'][axis])
                    getattr(self.pidevice, refmode)(axis)
                else:
                    raise
            if self.pidevice.devname in ('C-843',):
                waitonreferencing(self.pidevice, axes=axis, **self._kwargs)

    def _ref_with_pos(self, axes):
        """Set RON accordingly and reference 'axes' with the POS command to position "0.0".
        @param axes : Axes to reference as list or tuple of strings, must not be empty.
        """
        debug('ControllerStartup._ref_with_pos(axes=%s)', axes)
        assert self.pidevice.HasPOS(), 'controller does not support the POS command'
        self.pidevice.RON(axes, [False] * len(axes))
        self.pidevice.POS(axes, [0.0] * len(axes))
        waitonready(self.pidevice, **self._kwargs)
        self.pidevice.SVO(axes, [True] * len(axes))  # A following qONT will fail if servo is disabled.

    def enableaxes(self):
        """Enable all connected axes if appropriate."""
        debug('ControllerStartup.enableaxes()')
        if not self.pidevice.HasEAX() or self.prop['skipeax']:
            return
        for axis in self.pidevice.axes:
            try:
                self.pidevice.EAX(axis, True)
            except GCSError as exc:
                if exc != gcserror.E2_PI_CNTR_UNKNOWN_COMMAND:
                    raise
        waitonready(self.pidevice, **self._kwargs)


class FrozenClass(object):  # Too few public methods pylint: disable=R0903
    """Freeze child class when self.__isfrozen is set, i.e. values of already existing properties can still
    be changed but no new properties can be added.
    """
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and key not in dir(self):  # don't use hasattr(), it returns False on any exception
            raise TypeError('%r is immutable, cannot add %r' % (self, key))
        object.__setattr__(self, key, value)

    def _freeze(self):
        """After this method has been called the child class denies adding new properties."""
        self.__isfrozen = True


def enum(*args, **kwargs):
    """Return an Enum object of 'args' (enumerated) and 'kwargs' that can convert the values back to its names."""
    enums = dict(list(zip(args, range(len(args)))), **kwargs)
    reverse = dict((value, key) for key, value in enums.items())
    enums['name'] = reverse
    return type('Enum', (object,), enums)


class GCSRaise(object):  # Too few public methods pylint: disable=R0903
    """Context manager that asserts raising of specific GCSError(s).
    @param gcserrorid : GCSError ID or iterable of IDs that are expected to be raised as integer.
    @param mustraise : If True an exception must be raised, if False an exception can be raised.
    """

    def __init__(self, gcserrorid, mustraise=True):
        debug('create an instance of GCSRaise(gcserrorid=%s, mustraise=%s', gcserrorid, mustraise)
        self.__expected = gcserrorid if isinstance(gcserrorid, (list, set, tuple)) else [gcserrorid]
        self.__mustraise = mustraise and gcserrorid

    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, _exctraceback):
        gcsmsg = '%r' % gcserror.translate_error(excvalue)
        if exctype == GCSError:
            if excvalue in self.__expected:
                debug('expected GCSError %s was raised', gcsmsg)
                return True  # do not re-raise
        if not self.__mustraise and excvalue is None:
            debug('no error was raised')
            return True  # do not re-raise
        expected = ', '.join([gcserror.translate_error(errval) for errval in self.__expected])
        msg = 'expected %s%r but raised was %s' % ('' if self.__mustraise else 'no error or ', expected, gcsmsg)
        raise ValueError(msg)


def startup(pidevice, stages=None, refmodes=None, servostates=True, **kwargs):
    """Define 'stages', stop all, enable servo on all connected axes and reference them with 'refmodes'.
    Defining stages and homing them is done only if necessary.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param stages : Name of stages to initialize as string or list (not tuple!) or None to skip.
    @param refmodes : Referencing command as string (for all stages) or list (not tuple!) or None to skip.
    @param servostates : Desired servo states as boolean (for all stages) or dict {axis: state} or None to skip.
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    """
    devstartup = DeviceStartup(pidevice, **kwargs)
    devstartup.stages = stages
    devstartup.refmodes = refmodes
    devstartup.servostates = servostates
    devstartup.run()


def writewavepoints(pidevice, wavetable, wavepoints, bunchsize=None):
    """Write 'wavepoints' for 'wavetable' in bunches of 'bunchsize'.
    The 'bunchsize' is device specific. Please refer to the controller manual.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param wavetable : Wave table ID as integer.
    @param wavepoints : Single wavepoint as float convertible or list/tuple of them.
    @param bunchsize : Number of wavepoints in a single bunch or None to send all 'wavepoints' in a single bunch.
    """
    wavepoints = wavepoints if isinstance(wavepoints, (list, set, tuple)) else [wavepoints]
    if bunchsize is None:
        bunchsize = len(wavepoints)
    for startindex in range(0, len(wavepoints), bunchsize):
        bunch = wavepoints[startindex:startindex + bunchsize]
        pidevice.WAV_PNT(table=wavetable, firstpoint=startindex + 1, numpoints=len(bunch),
                         append='&' if startindex else 'X', wavepoint=bunch)


def getaxeslist(pidevice, axes):
    """Return list of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list or tuple of them or None for all axes.
    @return : List of axes from 'axes' or all axes or empty list.
    """
    axes = pidevice.axes if axes is None else axes
    if not axes:
        return []
    if not isinstance(axes, (list, set, tuple)):
        axes = [axes]
    return list(axes)  # convert tuple to list


def ontarget(pidevice, axes):
    """Return dictionary of on target states for open- or closedloop 'axes'.
    If qOSN is not supported open loop axes will return True.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list/tuple of axes to get values for or None for all axes.
    @return : Dictionary of boolean ontarget states of 'axes'.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return {}
    if pidevice.HasqSVO():
        servo = pidevice.qSVO(axes)
    else:
        servo = dict(list(zip(axes, [False] * len(axes))))
    closedloopaxes = [axis for axis in axes if servo[axis]]
    openloopaxes = [axis for axis in axes if not servo[axis]]
    isontarget = {}
    if closedloopaxes:
        if pidevice.HasqONT():
            isontarget.update(pidevice.qONT(closedloopaxes))
        elif pidevice.HasIsMoving():
            ismoving = pidevice.IsMoving(closedloopaxes).values()
            isontarget.update(dict(list(zip(closedloopaxes, [not x for x in ismoving]))))
    if openloopaxes:
        if pidevice.HasqOSN():
            stepsleft = pidevice.qOSN(openloopaxes).values()
            isontarget.update(dict(list(zip(openloopaxes, [x == 0 for x in stepsleft]))))
        else:
            isontarget.update(dict(list(zip(openloopaxes, [True] * len(openloopaxes)))))
    return isontarget


def waitonready(pidevice, timeout=60, predelay=0, polldelay=0.1):
    """Wait until controller is on "ready" state and finally query controller error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    sleep(predelay)
    if not pidevice.HasIsControllerReady():
        return
    maxtime = time() + timeout
    while not pidevice.IsControllerReady():
        if time() > maxtime:
            raise SystemError('waitonready() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    pidevice.checkerror()


# Too many arguments pylint: disable=R0913
def waitontarget(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all closedloop 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    axes = [x for x in axes if pidevice.qSVO(x)[x]]
    maxtime = time() + timeout
    while not all(list(pidevice.qONT(axes).values())):
        if time() > maxtime:
            raise SystemError('waitontarget() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


def waitonfastalign(pidevice, name=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param name : Name of the process as string or list/tuple.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    maxtime = time() + timeout
    while any(list(pidevice.qFRP(name).values())):
        if time() > maxtime:
            raise SystemError('waitonfastalign() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


def waitonwavegen(pidevice, wavegens=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param wavegens : Integer convertible or list/tuple of them or None.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    maxtime = time() + timeout
    while any(list(pidevice.IsGeneratorRunning(wavegens).values())):
        if time() > maxtime:
            raise SystemError('waitonwavegen() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


def waitonautozero(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    maxtime = time() + timeout
    while not all(list(pidevice.qATZ(axes).values())):
        if time() > maxtime:
            raise SystemError('waitonautozero() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


# Too many arguments pylint: disable=R0913
def waitonreferencing(pidevice, axes=None, timeout=180, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until referencing of 'axes' is finished or timeout.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis or list/tuple of axes to wait for motion to finish or None for all axes.
    @param timeout : Timeout in seconds as floatfor trajectory and motion, defaults to 180 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitontarget(pidevice, axes=axes, timeout=timeout, predelay=predelay)
    maxtime = time() + timeout
    if pidevice.devname in ('C-843',):
        pidevice.errcheck = False
    while not all(list(pidevice.qFRF(axes).values())):
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonreferencing() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    if pidevice.devname in ('C-843',):
        pidevice.errcheck = True
    sleep(postdelay)


def setservo(pidevice, axes, states=None, toignore=None, **kwargs):
    """Set servo of 'axes' to 'states'. Calls RNP for openloop axes and waits for servo
    operation to finish if appropriate. EAX is enabled for closedloop axes.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes: Axis or list/tuple of axes or dictionary {axis : value}.
    @param states : Bool or list of bools or None.
    @param toignore : GCS error as integer to ignore or list of them.
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    @return : False if setting the servo failed.
    """
    if not pidevice.HasSVO():
        return False
    axes, states = getitemsvaluestuple(axes, states)
    if pidevice.HasRNP():
        axestorelax = [axis for axis, state in list(pidevice.qSVO(axes).items()) if not state]
        if axestorelax:
            pidevice.RNP(axestorelax, [0.0] * len(axestorelax))
            waitonready(pidevice, **kwargs)
    eaxaxes = [axes[i] for i in range(len(axes)) if states[i]]
    enableaxes(pidevice, axes=eaxaxes, **kwargs)
    success = True
    toignore = [] if toignore is None else toignore
    toignore = [toignore] if not isinstance(toignore, list) else toignore
    toignore += [gcserror.E5_PI_CNTR_MOVE_WITHOUT_REF_OR_NO_SERVO, gcserror.E23_PI_CNTR_ILLEGAL_AXIS]
    for i, axis in enumerate(axes):
        try:
            pidevice.SVO(axis, states[i])
        except GCSError as exc:  # no GCSRaise() because we want to log a warning
            if exc in toignore:
                warning('could not set servo for axis %r to %s: %s', axis, states[i], exc)
                success = False
            else:
                raise
    waitonready(pidevice, **kwargs)
    return success


def enableaxes(pidevice, axes, **kwargs):
    """Enable all 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : String or list/tuple of strings of axes to enable.
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    """
    if not pidevice.HasEAX():
        return
    axes = getaxeslist(pidevice, axes)
    for axis in axes:
        try:
            pidevice.EAX(axis, True)
        except GCSError as exc:
            if exc == gcserror.E2_PI_CNTR_UNKNOWN_COMMAND:
                pass  # C-885
            else:
                raise
    waitonready(pidevice, **kwargs)


# Too many arguments pylint: disable=R0913
def waitonphase(pidevice, axes=None, timeout=60, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'axes' are on phase.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axes to wait for as string or list/tuple, or None to wait for all axes.
    @param timeout : Timeout in seconds as float, defaults to 60 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    maxtime = time() + timeout
    while not all([x > -1.0 for x in pidevice.qFPH(axes).values()]):
        if time() > maxtime:
            raise SystemError('waitonphase() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


# Too many arguments pylint: disable=R0913
def waitonwalk(pidevice, channels, timeout=300, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until qOSN for channels is zero.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param channels : Channel or list or tuple of channels to wait for motion to finish.
    @param timeout : Timeout in seconds as float, defaults to 300 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    channels = channels if isinstance(channels, (list, set, tuple)) else [channels]
    maxtime = time() + timeout
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    while not all(list(x == 0 for x in list(pidevice.qOSN(channels).values()))):
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonwalk() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    sleep(postdelay)


# Too many arguments pylint: disable=R0913
def waitonoma(pidevice, axes=None, timeout=300, predelay=0, polldelay=0.1):
    """Wait on the end of an open loop motion of 'axes'.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Axis as string or list/tuple of them to get values for or None to query all axes.
    @param timeout : Timeout in seconds as float, defaults to 300 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    axes = getaxeslist(pidevice, axes)
    numsamples = 5
    positions = []
    maxtime = time() + timeout
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    while True:
        positions.append(list(pidevice.qPOS(axes).values()))
        positions = positions[-numsamples:]
        if len(positions) < numsamples:
            continue
        isontarget = True
        for vals in zip(*positions):
            isontarget &= sum([abs(vals[i] - vals[i + 1]) for i in range(len(vals) - 1)]) < 0.01
        if isontarget:
            return
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonoma() timed out after %.1f seconds' % timeout)
        sleep(polldelay)


# Too many arguments pylint: disable=R0913
def waitontrajectory(pidevice, trajectories=None, timeout=180, predelay=0, postdelay=0, polldelay=0.1):
    """Wait until all 'trajectories' are done and all axes are on target.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param trajectories : Integer convertible or list/tuple of them or None for all trajectories.
    @param timeout : Timeout in seconds as floatfor trajectory and motion, defaults to 180 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param postdelay : Additional delay time in seconds as float after reaching desired state.
    @param polldelay : Delay time between polls in seconds as float.
    """
    maxtime = time() + timeout
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    while any(list(pidevice.qTGL(trajectories).values())):
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitontrajectory() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    waitontarget(pidevice, timeout=timeout, predelay=0, postdelay=postdelay, polldelay=polldelay)


def waitonmacro(pidevice, timeout=300, predelay=0, polldelay=0.1):
    """Wait until all macros are finished, then query and raise macro error.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param timeout : Timeout in seconds as float, defaults to 300 seconds.
    @param predelay : Time in seconds as float until querying any state from controller.
    @param polldelay : Delay time between polls in seconds as float.
    """
    maxtime = time() + timeout
    waitonready(pidevice, timeout=timeout, predelay=predelay)
    assert pidevice.HasqRMC() or pidevice.HasIsRunningMacro(), 'device does not support wait on macro'
    while True:
        if pidevice.HasqRMC() and not pidevice.qRMC().strip():
            break
        if pidevice.HasIsRunningMacro() and not pidevice.IsRunningMacro():
            break
        if time() > maxtime:
            stopall(pidevice)
            raise SystemError('waitonmacro() timed out after %.1f seconds' % timeout)
        sleep(polldelay)
    if pidevice.HasMAC_qERR():
        errmsg = pidevice.MAC_qERR().strip()
        if errmsg and int(errmsg.split('=')[1].split()[0]) != 0:
            raise GCSError(gcserror.E1012_PI_CNTR_ERROR_IN_MACRO, message=errmsg)


def stopall(pidevice, **kwargs):
    """Stop motion of all axes and mask the "error 10" warning.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param kwargs : Optional arguments with keywords that are passed to sub functions.
    """
    pidevice.StopAll(noraise=True)
    waitonready(pidevice, **kwargs)  # there are controllers that need some time to halt all axes


def moveandwait(pidevice, axes, values=None, timeout=120):
    """Call MOV with 'axes' and 'values' and wait for motion to finish.
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : Dictionary of axis:target or list/tuple of axes or axis.
    @param values : Optional list of values or value.
    @param timeout : Seconds as float until SystemError is raised.
    """
    pidevice.MOV(axes, values)
    if isinstance(axes, dict):
        axes = list(axes.keys())
    waitontarget(pidevice, axes=axes, timeout=timeout)


def movetomiddle(pidevice, axes=None):
    """Move 'axes' to its middle positions but do not wait "on target".
    @type pidevice : pipython.gcscommands.GCSCommands
    @param axes : List/tuple of strings of axes to get values for or None to query all axes.
    """
    axes = getaxeslist(pidevice, axes)
    if not axes:
        return
    rangemin = pidevice.qTMN(axes)
    rangemax = pidevice.qTMX(axes)
    targets = {}
    for axis in axes:
        targets[axis] = rangemin[axis] + (rangemax[axis] - rangemin[axis]) / 2.0
    pidevice.MOV(targets)


def savegcsarray(filepath, header, data):
    """Save data recorder output to a GCSArray file.
    @param filepath : Full path to target file as string.
    @param header : Header information from qDRR() as dictionary or None.
    @param data : Datarecorder data as one or two dimensional list of floats or NumPy array.
    """
    debug('save %r', filepath)
    try:
        data = data.tolist()  # convert numpy array to list
    except AttributeError:
        pass  # data already is a list
    if not isinstance(data[0], list):  # data must be multi dimensional
        data = [data]
    if header is None:
        header = OrderedDict([('VERSION', 1), ('TYPE', 1), ('SEPARATOR', 32), ('DIM', len(data)),
                              ('NDATA', len(data[0]))])
    sep = chr(header['SEPARATOR'])
    out = ''
    for key, value in header.items():
        out += '# %s = %s \n' % (key, value)
    out += '# \n# END_HEADER \n'
    for values in map(list, zip(*data)):  # transpose data
        out += sep.join(['%f' % value for value in values]) + ' \n'
    out = out[:-2] + '\n'
    piwrite(filepath, out)


def readgcsarray(filepath):
    """Read a GCSArray file and return header and data.
    @param filepath : Full path to file as string.
    @return header : Header information from qDRR() as dictionary.
    @return data : Datarecorder data as two columns list of floats.
    """
    debug('read %r', filepath)
    headerstr, datastr = [], []
    with open(filepath, 'r', encoding='utf-8', newline='\n') as fobj:
        for line in fobj:
            if line.startswith('#'):
                headerstr.append(line)
            else:
                datastr.append(line)
    header = getgcsheader('\n'.join(headerstr))
    sep = chr(header['SEPARATOR'])
    numcolumns = header['DIM']
    data = [[] for _ in range(numcolumns)]
    for line in datastr:
        if not line.strip():
            continue
        values = [float(x) for x in line.strip().split(sep)]
        for i in range(numcolumns):
            data[i].append(values[i])
    return header, data


def itemstostr(data):
    """Convert 'data' into a string message.
    @param data : Dictionary or list or tuple or single item to convert.
    """
    if data is False:
        return 'False'
    if not data:
        return 'None'
    msg = ''
    if isinstance(data, dict):
        for key, value in list(data.items()):
            msg += '%s: %s, ' % (key, value)
    elif isinstance(data, (list, set, tuple)):
        for value in data:
            msg += '%s, ' % value
    else:
        msg = str(data)
    msg = msg.rstrip(', ')
    return msg


def piwrite(filepath, text):
    """Write 'text' to 'filepath' with preset encoding.
    @param filepath : Full path to file to write as string, existing file will be replaced.
    @param text : Text to write as string or list of strings (with trailing line feeds).
    """
    if isinstance(text, list):
        text = ''.join(text)
    with open(filepath, 'w', encoding='utf-8', newline='\n') as fobj:
        fobj.write(text.encode('utf-8').decode('utf-8'))
