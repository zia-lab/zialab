#!/usr/bin/env python3
# ╔═════════════════════════════════════╗
# ║                                     ║
# ║                                     ║
# ║           ____  ____  ____          ║
# ║          / ___||  _ \/ ___|         ║
# ║          \___ \| |_) \___ \         ║
# ║           ___) |  _ < ___) |        ║
# ║          |____/|_| \_\____/         ║
# ║                                     ║
# ║      Stanford Research Systems      ║
# ║                                     ║
# ║              --DG 525--             ║
# ║                                     ║
# ║                                     ║
# ╚═════════════════════════════════════╝

# Created by David on 2020
# In the bottom of this file is attached the header
# file from which the DLL function's prototypes can
# be obtained.

import numpy as np
from ctypes import CDLL, c_long, c_short, c_char, byref, c_int, c_void_p
from ctypes import create_string_buffer
from time import sleep

def round_sigfigs(num, sig_figs):
    """Round to specified number of sigfigs.
    """
    if num != 0:
        return np.round(num, -int(np.floor(np.log10(abs(num)))
                                  - (sig_figs - 1)))
    else:
        return 0

bit_specs = {'0x4000': {'code': 'TIMO', 'meaning': 'Timeout'},
             '0x2000': {'code': 'END',  'meaning': 'EOI or EOS received'},
             '0x1000': {'code': 'SRQI', 'meaning': 'SRQ received'},
             '0x0800': {'code': 'RQS',  'meaning': 'Device requesting service'},
             '0x0400': {'code': 'SPOLL','meaning': "Board's been serially pol"},
             '0x0200': {'code': 'EVENT','meaning': 'An event has occured'},
             '0x0100': {'code': 'CMPL', 'meaning': 'Operation completed'},
             '0x0080': {'code': 'LOK',  'meaning': 'Local lockout'},
             '0x0040': {'code': 'REM',  'meaning': 'Remote state'},
             '0x0020': {'code': 'CIC',  'meaning': 'Controller-in-Charge'},
             '0x0010': {'code': 'ATN',  'meaning': 'ATN line asserted'},
             '0x0008': {'code': 'TACS', 'meaning': 'Talker active'},
             '0x0004': {'code': 'LACS', 'meaning': 'Listener active'},
             '0x0002': {'code': 'DTAS', 'meaning': 'Device trigger state'},
             '0x0001': {'code': 'DCAS', 'meaning': 'Device clear state'},
             '0x8000': {'code': 'ERR',  'meaning': 'Error'}}
config_options = {
    1: {'short_name': 'IbcPAD',
        'hex_code': '0x0001',
        'description': 'Primary Address'},
    2: {'short_name': 'IbcSAD',
        'hex_code': '0x0002',
        'description': 'Secondary Address'},
    3: {'short_name': 'IbcTMO', 'hex_code': '0x0003', 'description': 'Timeout'},
    4: {'short_name': 'IbcEOT',
        'hex_code': '0x0004',
        'description': 'Send EOI with last data byte'},
    5: {'short_name': 'IbcPPC',
        'hex_code': '0x0005',
        'description': 'Parallel Poll configure'},
    6: {'short_name': 'IbcREADDR',
        'hex_code': '0x0006',
        'description': 'Repeat Addressing'},
    7: {'short_name': 'IbcAUTOPOLL',
        'hex_code': '0x0007',
        'description': 'Disable Automatic Serial Polling'},
    8: {'short_name': 'IbcCICPROT',
        'hex_code': '0x0008',
        'description': 'Use CIC Protocol'},
    9: {'short_name': 'IbcIRQ',
        'hex_code': '0x0009',
        'description': 'Interrupt level (or 0)'},
    10: {'short_name': 'IbcSC',
        'hex_code': '0x000A',
        'description': 'Board is system controller'},
    11: {'short_name': 'IbcSRE',
        'hex_code': '0x000B',
        'description': 'Assert SRE for dev calls'},
    12: {'short_name': 'IbcEOSrd',
        'hex_code': '0x000C',
        'description': 'Terminate read on EOS'},
    13: {'short_name': 'IbcEOSwrt',
        'hex_code': '0x000D',
        'description': 'Send EOI with EOS'},
    14: {'short_name': 'IbcEOScmp',
        'hex_code': '0x000E',
        'description': 'Use 7 or 8-bit compare with EOS'},
    15: {'short_name': 'IbcEOSchar',
        'hex_code': '0x000F',
        'description': 'EOS character'},
    16: {'short_name': 'IbcPP2',
        'hex_code': '0x0010',
        'description': 'Use PP Mode 2.'},
    17: {'short_name': 'IbcTIMING',
        'hex_code': '0x0011',
        'description': 'Normal, high or very high timing'},
    18: {'short_name': 'IbcDMA',
        'hex_code': '0x0012',
        'description': 'DMA channel (or 0 for none)'},
    19: {'short_name': 'IbcReadAdjust',
        'hex_code': '0x0013',
        'description': 'Swap bytes on ibrd'},
    20: {'short_name': 'IbcWriteAdjust',
        'hex_code': '0x0014',
        'description': 'Swap bytes on ibwrt'},
    21: {'short_name': 'IbcEventQueue',
        'hex_code': '0x0015',
        'description': 'Use event queue'},
    22: {'short_name': 'IbcSpollBit',
        'hex_code': '0x0016',
        'description': 'Serial poll bit used'},
    23: {'short_name': 'IbcSendLLO',
        'hex_code': '0x0017',
        'description': 'Automatically send LLO'},
    24: {'short_name': 'IbcSPollTime',
        'hex_code': '0x0018',
        'description': 'Serial poll timeout'},
    25: {'short_name': 'IbcPPollTime',
        'hex_code': '0x0019',
        'description': 'Parallel poll timeout'},
    26: {'short_name': 'IbcEndBitIsNormal',
        'hex_code': '0x001A',
        'description': "Don't set END bit on EOS"},
    27: {'short_name': 'IbcUnAddr',
        'hex_code': '0x001B',
        'description': 'UN-ADDRESSING OPTION'},
    31: {'short_name': 'IbcHSCableLength',
        'hex_code': '0x001F',
        'description': 'High Speed cable length/mode'},
    32: {'short_name': 'IbcIst',
        'hex_code': '0x0020',
        'description': 'CURRENT PARALLEL POLL STATUS BIT'},
    33: {'short_name': 'IbcRsv',
        'hex_code': '0x0021',
        'description': 'CURRENT SERIAL POLL BYTE'},
    512: {'short_name': 'IbcBNA',
        'hex_code': '0x0200',
        'description': "A device's access board."},
    513: {'short_name': 'IbcBaseAddr',
        'hex_code': '0x0201',
        'description': "A GPIB board's base I/O address."},
    514: {'short_name': 'IbcDMAChn',
        'hex_code': '0x0202',
        'description': 'ASSIGNED DMA CHANNEL'},
    515: {'short_name': 'IbcIRQLev',
        'hex_code': '0x0203',
        'description': 'ASSIGNED IRQ LEVEL'},
    768: {'short_name': 'IbcBoardType',
        'hex_code': '0x0300',
        'description': 'Board Type'}}


class SRSDG535():
    '''Controls the SRSDG535 signal generator using GPIB
    commands sent through the ICS255 GPIB-USB adapter.
    To communicate successfully to the device values for
    the following are needed: self.addr, self.target,
    self.ud, self.tmo, self.mode. These could be found
    programatically, but it is good enough to find them
    using the ICS Explorer, GPIBkbd, and ICS_Spy utilities.
    '''

    ICS_DLL = CDLL("C:\\Program Files (x86)\\ICS_Electronics\\Utilities\\64 Bit\\GPIB-32.DLL")

    _ibclr = ICS_DLL['ibclr']
    _ibclr.restype = c_short
    _ibsre = ICS_DLL['ibsre']
    _ibsre.restype = c_int

    _iblines = ICS_DLL['iblines']
    _iblines.restype = c_int
    _ibask = ICS_DLL['ibask']
    _ibask.restype = c_int

    _ibtmo = ICS_DLL['ibtmo']
    _ibtmo.restype = c_int
    _Send = ICS_DLL['Send']
    _Send.restype = c_void_p

    _SendIFC = ICS_DLL['SendIFC']
    _SendIFC.restype = c_void_p

    def __init__(self):
        self.name = 'SRS-DG535'
        self.addr = 15  # int the GPIB address of the devie
        self.target = 0  # int
        self.ud = 0  # int
        self.tmo = 1  # int
        self.mode = 2
        self.configure()

    def configure(self):
        '''Arguments for the function calls
        used here were found using the ICS_Spy utility
        while using ICS Explorer and GPIBkbd utilities.
        Some of these might even be unnecessary ...'''
        self.ibsre(1)
        self.iblines()
        self.SendIFC()
        self.ibask(1,0)
        self.ibsre(1)
        self.ibtmo()
        print("Setting trigger mode to internal.")
        self.Send('TM 0')
        print("Setting the termination impedance of AB and -AB to 50 Ohm")
        self.Send('TZ 4,0')
        print("Setting the output mode of AB and -AB to be TTL")
        self.Send('OM 4,0')
        print("Setting the termination impedance of CD and -CD to 50 Ohm")
        self.Send('TZ 7,0')
        print("Setting the output mode of CD and -CD to be TTL")
        self.Send('OM 7,0')
        print("Setting view to trigger rate")
        self.Send('DL 0,1,0')

    def set_frequency(self, freq_in_Hz):
        '''Change the trigger frequency.
        Precision below 10Hz is 0.001Hz,
        and above is of 4 digits.'''
        if freq_in_Hz < 10:
            freq_in_Hz = np.round(freq_in_Hz, 3)
        else:
            freq_in_Hz = round_sigfigs(freq_in_Hz, 4)
        if freq_in_Hz > 1000000:
            print("Frequency can't be set higher than 1 MHz")
        elif freq_in_Hz < 0.001:
            print("Frequency can't be set higher lower than 0.001 Hz")
        else:
            self.Send("TR 0,%f" % freq_in_Hz)
        print("Frequency was set to %.1f Hz" % freq_in_Hz)
        self.freq_in_Hz = freq_in_Hz
        return freq_in_Hz

    def set_delay_A(self, delay_in_s):
        '''Set the delay of channel A with respect to T0'''
        if (delay_in_s < 0) or (delay_in_s > 999.999999999995):
            print("Invalid time delay")
        delay_in_s = np.round(delay_in_s, 12)
        self.Send("DT 2,1,%f" % delay_in_s)
        self.delay_A = delay_in_s
        return delay_in_s

    def set_delay_B(self, delay_in_s):
        '''Set the delay of channel B with respect to T0'''
        if (delay_in_s < 0) or (delay_in_s > 999.999999999995):
            print("Invalid time delay")
        delay_in_s = np.round(delay_in_s ,12)
        self.Send("DT 3,1,%f" % delay_in_s)
        self.delay_B = delay_in_s
        return delay_in_s

    def set_delay_C(self, delay_in_s):
        '''Set the delay of channel B with respect to T0'''
        if (delay_in_s < 0) or (delay_in_s > 999.999999999995):
            print("Invalid time delay")
        delay_in_s = np.round(delay_in_s ,12)
        self.Send("DT 5,1,%f" % delay_in_s)
        self.delay_C = delay_in_s
        return delay_in_s
    def set_delay_D(self, delay_in_s):
        '''Set the delay of channel B with respect to T0'''
        if (delay_in_s < 0) or (delay_in_s > 999.999999999995):
            print("Invalid time delay")
        delay_in_s = np.round(delay_in_s ,12)
        self.Send("DT 6,1,%f" % delay_in_s)
        self.delay_D = delay_in_s
        return delay_in_s

    def set_pulse(self, rep_rate_in_Hz, width_in_s, lag_in_s):
        '''Configures a pulse with the given repetition rate, of duration
        width, and starting at time lag after the trigger start.'''
        sleep(0.1)
        self.set_frequency(rep_rate_in_Hz)
        sleep(0.1)
        self.set_delay_A(lag_in_s)
        sleep(0.1)
        self.set_delay_B(lag_in_s+width_in_s)
        self.width = width_in_s
        self.lag = lag_in_s
        return None

    def set_pulseAB(self, rep_rate_in_Hz, width_in_s, lag_in_s):
        '''Configures a pulse with the given repetition rate, of duration
        width, and starting at time lag after the trigger start.'''
        sleep(0.1)
        self.set_frequency(rep_rate_in_Hz)
        sleep(0.1)
        self.set_delay_A(lag_in_s)
        sleep(0.1)
        self.set_delay_B(lag_in_s+width_in_s)
        self.widthAB = width_in_s
        self.lagAB = lag_in_s
        return None

    def set_pulseCD(self, rep_rate_in_Hz, width_in_s, lag_in_s):
        '''Configures a pulse with the given repetition rate, of duration
        width, and starting at time lag after the trigger start.'''
        sleep(0.1)
        self.set_frequency(rep_rate_in_Hz)
        sleep(0.1)
        self.set_delay_C(lag_in_s)
        sleep(0.1)
        self.set_delay_D(lag_in_s+width_in_s)
        self.widthCD = width_in_s
        self.lagCD = lag_in_s
        return None

    def ibclr(self, device):
        # GPIB32_API  int  __stdcall  ibclr (int ud)
        return bit_specs[hex(self._ibclr(c_short(device)))]['code']

    def ibsre(self, mode):
        # GPIB32_API  int  __stdcall  ibsre (int ud, int mode);
        response = self._ibsre(c_int(self.ud), c_int(mode))
        return response

    def iblines(self):
        # GPIB32_API  int  __stdcall  iblines (int ud, short *result);
        self.iblines_result_pointer = c_short(0)
        response = self._iblines(c_int(self.ud),
                                 byref(self.iblines_result_pointer))
        return response

    def ibask(self, item, value):
        # GPIB32_API  int  __stdcall  ibask (int target, int item, int *value);
        self.ibask_value_pointer = c_int(value)
        response = self._ibask(c_int(self.target),
                               c_int(item),
                               byref(self.ibask_value_pointer))
        return response

    def ibtmo(self):
        # GPIB32_API  int  __stdcall  ibtmo (int ud, int value);
        response = self._ibtmo(self.ud, c_int(self.tmo))
        return response

    def SendIFC(self):
        # GPIB32_API  void  __stdcall  SendIFC (int target);
        self._SendIFC(self.target)
        return None

    def Send(self, cmd):
        # GPIB32_API  void  __stdcall  Send (int target, Addr4882_t addr, void *buf, long len, int mode);
        self.cmd_buffer = create_string_buffer(cmd.encode(), len(cmd))
        self._Send(c_int(self.target),
                   c_short(self.addr),
                   byref(self.cmd_buffer),
                   c_long(len(cmd)),
                   c_int(self.mode))
        return None


######### ICSdeclh.h ##############

#/*
# * Name: ICSDecl.H
# *
# * C header for Windows GPIB-32 library
# *
# * (c) Copyright 2001-2011  ICS Electronics
# * All rights reserved.
# *
# * This header file should be included in all Windows C/C++ programs that
# *		 call the GPIB-32 library.
# *
# */
#
#
#
#
##ifndef ICSDECL
#
##ifdef GPIB32_EXPORTS
##define GPIB32_API __declspec(dllexport)
##define EXTERN
##else
##define GPIB32_API __declspec(dllimport)
##define EXTERN      extern "C"
##pragma comment(lib, "GPIB-32.LIB")
##endif
#
#
#
##endif
#
#
#
#
#typedef int (__stdcall NotifyCallback )(int ud, int ibsta, int iberr, long ibcntl, void *refdata);
#
##define TALK_BASE   0x40
##define LSTN_BASE   0x20
#
#// Used in ibcntl if ibnotify callback function return mask value invalid
##define IBNOTIFY_REARM_FAILED    0xE00A003F
#
#
#
#
#/* GPIB Commands  */
##define GTL  0x01
##define SDC  0x04
##define PPC  0x05
##define GET  0x08
##define TCT  0x09
##define LLO  0x11
##define DCL  0x14
##define PPU  0x15
##define SPE  0x18
##define SPD  0x19
##define UNL  0x3f
##define UNT  0x5f
##define PPE  0x60
##define PPD  0x70
#
#/* Bit specifiers for ibsta status variable and wait mask  */
##define ERR   (unsigned) 0x8000   /* Error                     */
##define TIMO  0x4000   /* Timeout                   */
##define END   0x2000   /* EOI or EOS received       */
##define SRQI  0x1000   /* SRQ received              */
##define RQS   0x0800   /* Device requesting service */
##define SPOLL 0x0400   /* Board's been serially polled  */
##define EVENT 0x0200   /* An event has occured      */
##define CMPL  0x0100   /* Operation completed       */
##define LOK   0x0080   /* Local lockout             */
##define REM   0x0040   /* Remote state              */
##define CIC   0x0020   /* Controller-in-Charge      */
##define ATN   0x0010   /* ATN line asserted         */
##define TACS  0x0008   /* Talker active             */
##define LACS  0x0004   /* Listener active           */
##define DTAS  0x0002   /* Device trigger state      */
##define DCAS  0x0001   /* Device clear state        */
#
#/* System error code */
##define EDVR  0         /* DOS error                                */
##define ECIC  1         /* board should be CIC                      */
##define ENOL  2         /* No Listeners detected                    */
##define EADR  3         /* Board not addressed correctly            */
##define EARG  4         /* Invalid argument specified               */
##define ESAC  5         /* Board should be system controller        */
##define EABO  6         /* I/O operation aborted                    */
##define ENEB  7         /* Invalid interface board sprecified       */
##define EOIP 10         /* I/O operation already running            */
##define ECAP 11         /* Board does not have requested capability */
##define EFSO 12         /* Erro retunred from file system           */
##define EBUS 14         /* Command error on bus                     */
##define ESTB 15         /* Serial poll response byte lost           */
##define ESRQ 16         /* SRQ is still asserted                    */
##define ETAB 20         /* No device responding with ETAB           */
##define ELCK 21         /* Handle is locked                         */
##define EHDL 23         /* Invalid handle                           */
##define EINT 247        /* No interrupt configured on board.        */
##define EWMD 248        /* Windows is not in enhanced mode          */
##define EVDD 249        /* CBGPIB.386 is not installed              */
##define EOVR 250        /* Buffer overflow                          */
##define ESML 251        /* Two library calls running simultaneously */
##define ECFG 252        /* Board type doesn't match GPIB.CFG        */
##define ETMR 253        /* No Windows timers available              */
##define ESLC 254        /* No Windows selectors available           */
##define EBRK 255        /* Ctrl-Break pressed, exiting program      */
#
#/* EOS mode bits                                           */
##define BIN  0x1000
##define XEOS 0x0800
##define REOS 0x0400
#
#/* Timeout values and meanings                             */
##define TNONE    0      /* No timeout        */
##define T10us    1      /* 10  microseconds  */
##define T30us    2      /* 30  microseconds  */
##define T100us   3      /* 100 microseconds  */
##define T300us   4      /* 300 microseconds  */
##define T1ms     5      /* 1   milliseconds  */
##define T3ms     6      /* 3   milliseconds  */
##define T10ms    7      /* 10  milliseconds  */
##define T30ms    8      /* 30  milliseconds  */
##define T100ms   9      /* 100 milliseconds  */
##define T300ms  10      /* 300 milliseconds  */
##define T1s     11      /* 1   seconds       */
##define T3s     12      /* 3   seconds       */
##define T10s    13      /* 10  seconds       */
##define T30s    14      /* 30  seconds       */
##define T100s   15      /* 100 seconds       */
##define T300s   16      /* 300 seconds       */
##define T1000s  17      /* 1000 seconds      */
#
#
#/*  IBLN Constants                                  */
##define NO_SAD   0      /* No secondary addresses   */
##define ALL_SAD -1      /* All secondary addresses  */
#
#typedef short Addr4882_t;   /* Address type for 488.2 calls */
#
#/* Macro to create an entry in address list (type Addr4882_t) for 488.2
#  functions. Combines primary and secondary addresses into a single address */
##define  MakeAddr(pad, sad)   ((Addr4882_t)(((pad)&0xFF) | ((sad)<<8)))
##define  GetPAD(adr)    ((adr) & 0xff)
##define  GetSAD(adr)    (((adr) >> 8) & 0xff)
#
#/* Miscellaneous                                      */
##define S    0x08           /* parallel poll  bit            */
##define LF   0x0a           /* linefeed character            */
##define NOADDR    (Addr4882_t)(-1)
##define NULLend   0         /* Send() EOTMODE - Do nothing at the end of a transfer.*/
##define NLend     1         /* Send() EOTMODE - Send NL with EOI after a transfer.  */
##define DABend    2         /* Send() EOTMODE - Send EOI with the last DAB.         */
##define STOPend   0x0100    /* Receive()( termination */
##define EventDTAS 1         /* used by IBEVENT() */
##define EventDCAS 2         /* used by IBEVENT() */
#
#
#/*  These constants are used with ibconfig() to specify one of the
#    configurable options. */
##define  IbcPAD           0x0001    /* Primary Address                   */
##define  IbcSAD           0x0002    /* Secondary Address                 */
##define  IbcTMO           0x0003    /* Timeout                           */
##define  IbcEOT           0x0004    /* Send EOI with last data byte      */
##define  IbcPPC           0x0005    /* Parallel Poll configure           */
##define  IbcREADDR        0x0006    /* Repeat Addressing                 */
##define  IbcAUTOPOLL      0x0007    /* Disable Automatic Serial Polling  */
##define  IbcCICPROT       0x0008    /* Use CIC Protocol                  */
##define  IbcIRQ           0x0009    /* Interrupt level (or 0)            */
##define  IbcSC            0x000A    /* Board is system controller        */
##define  IbcSRE           0x000B    /* Assert SRE for dev calls          */
##define  IbcEOSrd         0x000C    /* Terminate read on EOS             */
##define  IbcEOSwrt        0x000D    /* Send EOI with EOS                 */
##define  IbcEOScmp        0x000E    /* Use 7 or 8-bit compare with EOS   */
##define  IbcEOSchar       0x000F    /* EOS character                     */
##define  IbcPP2           0x0010    /* Use PP Mode 2.                    */
##define  IbcTIMING        0x0011    /* Normal, high or very high timing  */
##define  IbcDMA           0x0012    /* DMA channel (or 0 for none)       */
##define  IbcReadAdjust    0x0013    /* Swap bytes on ibrd                */
##define  IbcWriteAdjust   0x0014    /* Swap bytes on ibwrt               */
##define  IbcEventQueue    0x0015    /* Use event queue                   */
##define  IbcSpollBit      0x0016    /* Serial poll bit used              */
##define  IbcSendLLO       0x0017    /* Automatically send LLO            */
##define  IbcSPollTime     0x0018    /* Serial poll timeout               */
##define  IbcPPollTime     0x0019    /* Parallel poll timeout             */
##define  IbcEndBitIsNormal 0x001A   /* Don't set END bit on EOS          */
##define  IbcUnAddr        0x001B    /* UN-ADDRESSING OPTION              */
##define  IbcHSCableLength 0x001F    /* High Speed cable length/mode      */
##define	 IbcIst           0x0020    /* CURRENT PARALLEL POLL STATUS BIT  */
##define	 IbcRsv           0x0021    /* CURRENT SERIAL POLL BYTE          */
#
##define  IbcBNA           0x0200    /* A device's access board.          */
##define  IbcBaseAddr      0x0201    /* A GPIB board's base I/O address.  */
##define	 IbcDMAChn        0x0202    /* ASSIGNED DMA CHANNEL              */
##define	 IbcIRQLev        0x0203    /* ASSIGNED IRQ LEVEL                */
#
##define  IbcBoardType     0x0300    /* Board Type */
#
#/* These are included for the sake of compatability with NI's library */
##define IbaPAD              0x0001
##define IbaSAD              0x0002
##define IbaTMO              0x0003
##define IbaEOT              0x0004
##define IbaPPC              0x0005
##define IbaREADDR           0x0006
##define IbaAUTOPOLL         0x0007
##define IbaCICPROT          0x0008
##define IbaIRQ              0x0009
##define IbaSC               0x000A
##define IbaSRE              0x000B
##define IbaEOSrd            0x000C
##define IbaEOSwrt           0x000D
##define IbaEOScmp           0x000E
##define IbaEOSchar          0x000F
##define IbaPP2              0x0010
##define IbaTIMING           0x0011
##define IbaDMA              0x0012
##define IbaReadAdjust       0x0013
##define IbaWriteAdjust      0x0014
##define IbaEventQueue       0x0015
##define IbaSpollBit         0x0016
##define IbaSendLLO          0x0017
##define IbaSPollTime        0x0018
##define IbaPPollTime        0x0019
##define IbaEndBitIsNormal   0x001A
##define IbaUnAddr           0x001B
##define IbaHSCableLength    0x001F
##define	IbaIst              0x0020
##define	IbaRsv              0x0021
#
##define IbaBNA              0x0200
##define IbaBaseAddr         0x0201
##define IbaDMAChannel       0x0202
##define	IbaIRQLevel         0x0203
#
##define  IbaBoardType       0x0300
#
#/* These bits specify which lines can be monitored by IBLINES */
##define  ValidEOI  (unsigned int) 0x0080
##define  ValidATN  (unsigned int) 0x0040
##define  ValidSRQ  (unsigned int) 0x0020
##define  ValidREN  (unsigned int) 0x0010
##define  ValidIFC  (unsigned int) 0x0008
##define  ValidNRFD (unsigned int) 0x0004
##define  ValidNDAC (unsigned int) 0x0002
##define  ValidDAV  (unsigned int) 0x0001
#
##define  BusDAV    (unsigned int) 0x0100
##define  BusNDAC   (unsigned int) 0x0200
##define  BusNRFD   (unsigned int) 0x0400
##define  BusIFC    (unsigned int) 0x0800
##define  BusREN    (unsigned int) 0x1000
##define  BusSRQ    (unsigned int) 0x2000
##define  BusATN    (unsigned int) 0x4000
##define  BusEOI    (unsigned int) 0x8000
#
#
#
#// NI 488.1 IB type functions
#GPIB32_API  int  __stdcall  ibask (int target, int item, int *value);
#GPIB32_API  int  __stdcall  ibbna (int ud, char name[]);
#GPIB32_API  int  __stdcall  ibbnaA (int ud, char name[]);
#GPIB32_API  int  __stdcall  ibbnaW (int ud, wchar_t name[]);
#GPIB32_API  int  __stdcall  ibcac (int ud, int method);
#GPIB32_API  int  __stdcall  ibclr (int ud);
#GPIB32_API  int  __stdcall  ibcmd (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibcmda (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibconfig (int target, int item, int value);
#GPIB32_API  int  __stdcall  ibdev (int brd, int pad, int sad, int tmo, int eot, int eos);
#GPIB32_API  int  __stdcall  ibdma (int ud, int mode);
#GPIB32_API  int  __stdcall  ibeos (int ud, int mode);
#GPIB32_API  int  __stdcall  ibeot (int ud, int mode);
#GPIB32_API  int  __stdcall  ibevent (int ud, int *event);
#GPIB32_API  int  __stdcall  ibfind (char name[]);
#GPIB32_API  int  __stdcall  ibfindA (char name[]);
#GPIB32_API  int  __stdcall  ibfindW (wchar_t name[]);
#GPIB32_API  int  __stdcall  ibgts (int ud, int mode);
#GPIB32_API  int  __stdcall  ibist (int ud, int mode);
#GPIB32_API  int  __stdcall  iblines (int ud, short *result);
#GPIB32_API  int  __stdcall  ibln (int ud, int pad, int sad, short *result);
#GPIB32_API  int  __stdcall  ibloc (int ud);
#GPIB32_API  int  __stdcall  ibnotify (int ud, int mask, NotifyCallback *callback, void *refData);
#GPIB32_API  int  __stdcall  ibonl (int ud, int mode);
#GPIB32_API  int  __stdcall  ibpad (int ud, int pad);
#GPIB32_API  int  __stdcall  ibpct (int ud);
#GPIB32_API  int  __stdcall  ibppc (int ud, int mode);
#GPIB32_API  int  __stdcall  ibrd (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibrdi (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibrdia (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibrda (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibrdf (int ud, char filename[]);
#GPIB32_API  int  __stdcall  ibrdfA (int ud, char filename[]);
#GPIB32_API  int  __stdcall  ibrdfW (int ud, wchar_t  filename[]);
#GPIB32_API  int  __stdcall  ibrpp (int ud, char *mode);
#GPIB32_API  int  __stdcall  ibrsc (int ud, int mode);
#GPIB32_API  int  __stdcall  ibrsp (int ud, char *result);
#GPIB32_API  int  __stdcall  ibrsv (int ud, int mode);
#GPIB32_API  int  __stdcall  ibsad (int ud, int sad);
#GPIB32_API  int  __stdcall  ibsic (int ud);
#GPIB32_API  int  __stdcall  ibsre (int ud, int mode);
#GPIB32_API  int  __stdcall  ibstop (int ud);
#GPIB32_API  int  __stdcall  ibtmo (int ud, int value);
#GPIB32_API  int  __stdcall  ibtrg (int ud);
#GPIB32_API  int  __stdcall  ibwait (int ud, int mask);
#GPIB32_API  int  __stdcall  ibwrt (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibwrti (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibwrtia (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibwrta (int ud, void *buf, long length);
#GPIB32_API  int  __stdcall  ibwrtf (int ud, char filename[]);
#GPIB32_API  int  __stdcall  ibwrtfA (int ud, char filename[]);
#GPIB32_API  int  __stdcall  ibwrtfW (int ud, wchar_t filename[]);
#
#
#// NI 488.2 functions
#GPIB32_API  void  __stdcall  AllSpoll (int target, Addr4882_t *addrs, short *res);
#GPIB32_API  void  __stdcall  DevClear (int target, Addr4882_t device);
#GPIB32_API  void  __stdcall  DevClearList (int target, Addr4882_t *addrs);
#GPIB32_API  void  __stdcall  EnableLocal (int target, Addr4882_t *addrs);
#GPIB32_API  void  __stdcall  EnableRemote (int target, Addr4882_t *addrs);
#GPIB32_API  void  __stdcall  FindLstn ( int intfc, Addr4882_t pads[], Addr4882_t results[], int limit);
#GPIB32_API  void  __stdcall  FindRQS (int target, Addr4882_t addrs[], short *result);
#GPIB32_API  void  __stdcall  PassControl (int target, short talker);
#GPIB32_API  void  __stdcall  PPoll (int target, short *result);
#GPIB32_API  void  __stdcall  PPollConfig (int target, Addr4882_t addr, int line, int sense);
#GPIB32_API  void  __stdcall  PPollUnconfig (int target, Addr4882_t addrs[]);
#GPIB32_API  void  __stdcall  RcvRespMsg (int target, char buf[], long length, int term);
#GPIB32_API  void  __stdcall  ReadStatusByte (int target, Addr4882_t addr, short *result);
#GPIB32_API  void  __stdcall  Receive (int target, Addr4882_t addr, void *buf, long len, int mode);
#GPIB32_API  void  __stdcall  ReceiveSetup (int target, Addr4882_t addr);
#GPIB32_API  void  __stdcall  ResetSys (int target, Addr4882_t addrs[]);
#GPIB32_API  void  __stdcall  Send (int target, Addr4882_t addr, void *buf, long len, int mode);
#GPIB32_API  void  __stdcall  SendCmds (int target, void *buffer, long length);
#GPIB32_API  void  __stdcall  SendDataBytes (int target, void *buffer, long length, int mode);
#GPIB32_API  void  __stdcall  SendIFC (int target);
#GPIB32_API  void  __stdcall  SendList (int target, Addr4882_t addrs[], void *buffer, long length, int mode);
#GPIB32_API  void  __stdcall  SendLLO (int target);
#GPIB32_API  void  __stdcall  SendSetup (int target, Addr4882_t addrs[]);
#GPIB32_API  void  __stdcall  SetRWLS (int target, Addr4882_t addrs[]);
#GPIB32_API  void  __stdcall  TestSRQ (int target, short *result);
#GPIB32_API  void  __stdcall  TestSys (int target, Addr4882_t addrs[], short results[]);
#GPIB32_API  void  __stdcall  Trigger (int target, Addr4882_t addr);
#GPIB32_API  void  __stdcall  TriggerList (int target, Addr4882_t addrs[]);
#GPIB32_API  void  __stdcall  WaitSRQ (int target, short *result);
#
#
#GPIB32_API  int   __stdcall  RegisterGpibGlobalsForThread (long *ibsta, long *iberr, long *ibcnt, long *ibcntl);
#GPIB32_API  int   __stdcall  UnregisterGpibGlobalsForThread (void);
#
#GPIB32_API  int   __stdcall  ThreadIbcnt (void);
#GPIB32_API  long  __stdcall  ThreadIbcntl (void);
#GPIB32_API  int   __stdcall  ThreadIberr (void);
#GPIB32_API  int   __stdcall  ThreadIbsta (void);
#
#
#GPIB32_API  short  __stdcall  DLLibask (short Target, short Item, short *Value);
#GPIB32_API  short  __stdcall  DLLibbna (short Device, char *intfcName);
#GPIB32_API  short  __stdcall  DLLibcac (short Intfc, short Sync);
#GPIB32_API  short  __stdcall  DLLibclr (short Device);
#GPIB32_API  short  __stdcall  DLLibcmd (short Intfc, char *Cmdstr, long Count);
#GPIB32_API  short  __stdcall  DLLibcmda (short Intfc, char *Cmdstr, long Count);
#GPIB32_API  short  __stdcall  DLLibconfig (short Target, short Item, short Value);
#GPIB32_API  short  __stdcall  DLLibdev ( short Index, short Pad, short Sad, short Timeout, short Eot, short Eos);
#GPIB32_API  short  __stdcall  DLLibdma (short Intfc, short Dma);
#GPIB32_API  short  __stdcall  DLLibeos (short Target, short Eos);
#GPIB32_API  short  __stdcall  DLLibeot (short Target, short Eot);
#GPIB32_API  short  __stdcall  DLLibfind(char *devname);
#GPIB32_API  short  __stdcall  DLLibfindA (char *devname);
#GPIB32_API  short  __stdcall  DLLibgts (short Intfc, short Handshake);
#GPIB32_API  short  __stdcall  DLLiblines (short Intfc, short *CLines);
#GPIB32_API  short  __stdcall  DLLibln (short Intfc, short Pad, short Sad, short *Listen);
#GPIB32_API  short  __stdcall  DLLibloc (short Target);
#GPIB32_API  short  __stdcall  DLLibonl (short Target, short Online);
#GPIB32_API  short  __stdcall  DLLibpad (short Target, short PAddr);
#GPIB32_API  short  __stdcall  DLLibpct (short Device);
#GPIB32_API  short  __stdcall  DLLibppc (short Target, short Cmd);
#GPIB32_API  short  __stdcall  DLLibrd (short Target, char *Str, long Count);
#GPIB32_API  short  __stdcall  DLLibrda (short Target, char Str, long Count);
#GPIB32_API  short  __stdcall  DLLibrdf (short Target, char *FName);
#GPIB32_API  short  __stdcall  DLLibrdfA (short Target, char *FName);
#GPIB32_API  short  __stdcall  DLLibrsc (short Intfc, short Ctrl);
#GPIB32_API  short  __stdcall  DLLibrsp (short Device, short *Resp);
#GPIB32_API  short  __stdcall  DLLibrsv (short Target, short SPByte);
#GPIB32_API  short  __stdcall  DLLibsad (short Target, short SAddr);
#GPIB32_API  short  __stdcall  DLLibsic (short Intfc);
#GPIB32_API  short  __stdcall  DLLibsre (short Intfc, short Ren);
#GPIB32_API  short  __stdcall  DLLibstop (short Target);
#GPIB32_API  short  __stdcall  DLLibtmo (short Target, short Tmo);
#GPIB32_API  short  __stdcall  DLLibtrg(short Device);
#GPIB32_API  short  __stdcall  DLLibwait (short Target, short Mask);
#GPIB32_API  short  __stdcall  DLLibwrt (short Target, void *Str, long Count);
#GPIB32_API  short  __stdcall  DLLibwrta (short Target, void *Str, long Count);
#GPIB32_API  short  __stdcall  DLLibwrti (short Target, void *Str, long Count);
#GPIB32_API  short  __stdcall  DLLibwrtia (short Target, void *Str, long Count);
#GPIB32_API  short  __stdcall  DLLibwrtf (short Target, char *Fname);
#GPIB32_API  short  __stdcall  DLLibwrtfA (short Target, char *Fname);
#
#
#GPIB32_API  void  __stdcall  DLLAllSpoll (short Intfc, Addr4882_t *List, short *Res);
#GPIB32_API  void  __stdcall  DLLDevClear (short Intfc, short Addr);
#GPIB32_API  void  __stdcall  DLLDevClearList (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLEnableLocal (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLEnableRemote (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLFindLstn (short Intfc, Addr4882_t *List, Addr4882_t *Results, short Limit);
#GPIB32_API  void  __stdcall  DLLFindRQS (short Intfc, Addr4882_t *List, short *Result);
#GPIB32_API  void  __stdcall  DLLReadStatusByte (short Intfc, short Addr, short *Result);
#GPIB32_API  void  __stdcall  DLLPassControl (short Intfc, short Addr);
#GPIB32_API  void  __stdcall  DLLPPoll (short Intfc, short *Result);
#GPIB32_API  void  __stdcall  DLLPPollConfig(short Intfc, short Addr, short Line, short Sense);
#GPIB32_API  void  __stdcall  DLLPPollUnconfig (short Intfc, short List[]);
#GPIB32_API  void  __stdcall  DLLRcvRespMsg (short Intfc, char *Buf, long Len, short Term);
#GPIB32_API  void  __stdcall  DLLReceive (short Intfc, short Addr, char *Buf, long Len, short Term);
#GPIB32_API  void  __stdcall  DLLReceiveSetup (short Intfc, short Addr);
#GPIB32_API  void  __stdcall  DLLResetSys (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLSend (short Intfc, short Addr, char *Buf, long Len, short Term);
#GPIB32_API  void  __stdcall  DLLSendCmds (short Intfc, char *Buf, long Len);
#GPIB32_API  void  __stdcall  DLLSendIFC (short Intfc);
#GPIB32_API  void  __stdcall  DLLSendDataBytes (short Intfc, char *Buf, long Len, short Term);
#GPIB32_API  void  __stdcall  DLLSendList (short Intfc, Addr4882_t *List, char *Buf, long Len, short Term);
#GPIB32_API  void  __stdcall  DLLSendLLO (short Intfc);
#GPIB32_API  void  __stdcall  DLLSendSetup (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLSetRWLS (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLTestSRQ (short Intfc, short *Result);
#GPIB32_API  void  __stdcall  DLLTestSys (short Intfc, Addr4882_t *List, short *Result);
#GPIB32_API  void  __stdcall  DLLTrigger (short Intfc, short Addr);
#GPIB32_API  void  __stdcall  DLLTriggerList (short Intfc, Addr4882_t *List);
#GPIB32_API  void  __stdcall  DLLWaitSRQ (short Intfc, short *Result);
#
#
#// NI defined status variables
#extern  GPIB32_API	  unsigned short  ibsta;
#extern  GPIB32_API             short  iberr;
#extern  GPIB32_API             short  ibcnt;
#extern  GPIB32_API             long   ibcntl;
