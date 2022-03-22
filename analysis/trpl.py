import time, pickle, os, untangle
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, LogNorm
from scipy.optimize import curve_fit
from scipy.signal import medfilt
from ..misc.sugar import wav2RGB
from io import StringIO
from IPython.display import Image

zlab_dir = 'D:/Google Drive/Zia Lab/'

def slice_and_dice(spectrum, center_wave, pad_px, wavemin='auto', wavemax='auto',times=[]):
    def lifetime_fit(t,tau,A,B):
        return A*np.exp(-(t)/tau)+B
    fsize=15
    waves = spectrum['counts']['waves']
    center_wave_idx = np.argmin(np.abs(spectrum['counts']['waves']-center_wave))
    top_wave = waves[center_wave_idx+pad_px]
    bottom_wave = waves[center_wave_idx-pad_px]
    cake_slice = spectrum['avg_signal_filtered'][:,center_wave_idx-pad_px:center_wave_idx+pad_px+1]
    std_slice = spectrum['avg_signal_std'][:,center_wave_idx-pad_px:center_wave_idx+pad_px+1]
    if times == []:
        the_times = np.mean(spectrum['bkg']['offset_timetags'][:spectrum['frames_per_rep']],axis=1)/1000.
    else:
        the_times = times
    totalo = np.abs(np.sum(cake_slice,axis=1))
    errors = np.sqrt(np.abs(np.sum(std_slice**2,axis=1)))

    good_times_idx = the_times>=(spectrum['excitation_duration_in_s']*1000)
    good_times = the_times[good_times_idx]
    good_times = good_times-good_times[0]
    good_counts = totalo[good_times_idx]
    good_errors = errors[good_times_idx]
    not_null_counts_idx = (good_counts != 0)
    good_counts = good_counts[not_null_counts_idx]
    good_times = good_times[not_null_counts_idx]
    good_errors = good_errors[not_null_counts_idx]
    opt_params, opt_cov = curve_fit(lifetime_fit,
                   good_times,
                   good_counts,
                   sigma=good_errors,
                   p0=np.array([1.,max(totalo),totalo[-10]]))
    good_fit = lifetime_fit(good_times,*opt_params)
    par_error =  np.sqrt(np.diag(opt_cov))

    rainbow = np.array([wav2RGB(wave) for idx, wave in enumerate(spectrum['counts']['waves'])])
    spectacular = np.abs(medfilt(spectrum['avg_signal'],3))
    spectacular = spectacular/np.max(spectacular)
    vacuum = np.array([[[0,0,0,1-c] for c in b] for b in spectacular])
    fig,ax = plt.subplots(nrows=3,ncols=1,figsize=(10,10))
    if wavemin == 'auto':
        wavemin = min(waves)
    if wavemax == 'auto':
        wavemax = max(waves)
    ax[0].imshow([waves],
          extent=[min(waves),max(waves),0,the_times[-1]],
          origin='lower',
          cmap=ListedColormap(rainbow))
    ax[0].imshow(vacuum,extent=[min(waves),max(waves),0,the_times[-1]],
           aspect=16,origin='lower')
    ax[0].plot([spectrum['counts']['waves'][0],spectrum['counts']['waves'][-1]],
             [spectrum['excitation_duration_in_s']*1000]*2,
            'r--',alpha=0.85)
    ax[0].set_xlabel('$\lambda$/nm',fontsize=fsize)
    ax[0].set_ylabel('t / ms',fontsize=fsize)
    ax[0].set_xlim(wavemin,wavemax)

    ax[1].imshow(cake_slice.T,
               extent=[0,
                       the_times[-1],
                       spectrum['counts']['waves'][center_wave_idx-pad_px],
                       spectrum['counts']['waves'][center_wave_idx+pad_px]],
              origin='lower',
              cmap='gray',
              aspect=0.1)
    ax[1].set_ylabel('$\lambda$/nm',fontsize=fsize)
    ax[1].set_xlabel('t / ms',fontsize=fsize)

    ax[2].plot(the_times,totalo ,'o',ms=1)
    ax[2].plot([spectrum['excitation_duration_in_s']*1000]*2,[0,max(totalo)],'ro--')
    ax[2].plot(good_times+spectrum['excitation_duration_in_s']*1000,good_fit)
    ax[2].set_ylim(0,max(totalo))
    ax[2].set_xlabel('t / ms',fontsize=fsize)
    ax[2].set_ylabel('counts/AU',fontsize=fsize)
    ax[2].set_xlim(1,2)
    plt.text(0.8,0.9,'$C(t) = A*e^{-(t-t_0)/\\tau} + B$\n$\\tau$ = (%.3f $\pm$ %.3f) ms\n A = (%.0f $\pm$ %.0f)\n B = (%.0f $\pm$ %.0f)\n$\lambda$ : [%.1f - %.1f] nm' % (opt_params[0],par_error[0],
                                                                                                            opt_params[1],par_error[1],
                                                                                                            opt_params[2],par_error[2],
                                                                                                            bottom_wave,top_wave),
             ha='center',va='top',transform=ax[2].transAxes,fontsize=0.9*fsize)
    ax[0].plot([center_wave]*2,[0,max(the_times)],'w--',alpha=0.2)
    plt.subplots_adjust(hspace=-0.1)
    return fig

def numcrunch(spectrum, lifetime_regression = True, pad_size=2, save_figs=True):
    '''imports data from spe files'''
    fig_width = 15
    print("Loading data from .spe files...")
    print(">>> Loading counts...")
    spectrum['counts']['avg'], spectrum['counts']['timetags'], spectrum['counts']['waves'], spectrum['counts']['stds'] = quick_loader_with_stats('counts',spectrum)
    print(">>> Loading background...")
    spectrum['bkg']['avg'], spectrum['bkg']['timetags'], spectrum['bkg']['waves'], spectrum['bkg']['stds'] = quick_loader_with_stats('bkg',spectrum)

    print("Computing time offsets across frames and repetitions...")
    spectrum['counts']['offset_timetags'] = np.zeros(spectrum['counts']['timetags'].shape)
    spectrum['bkg']['offset_timetags'] = np.zeros(spectrum['bkg']['timetags'].shape)
    for rep in range(spectrum['reps']):
        idx_start = spectrum['frames_per_rep']*rep
        idx_end = idx_start + spectrum['frames_per_rep']
        spectrum['counts']['offset_timetags'][idx_start:idx_end] =  (spectrum['counts']['timetags'][idx_start:idx_end]
                                                              - spectrum['counts']['timetags'][idx_start][0])
        spectrum['bkg']['offset_timetags'][idx_start:idx_end] =  (spectrum['bkg']['timetags'][idx_start:idx_end]
                                                              - spectrum['bkg']['timetags'][idx_start][0])
    # Compute kcps rates along with uncertainties
    spectrum['counts']['avg_rate'] = (spectrum['counts']['avg'])/spectrum['exposure_in_ms']
    spectrum['bkg']['avg_rate'] = (spectrum['bkg']['avg'])/spectrum['exposure_in_ms']
    spectrum['avg_signal'] = spectrum['counts']['avg_rate']-spectrum['bkg']['avg_rate']
    spectrum['avg_signal_std'] = (np.sqrt(spectrum['bkg']['stds']**2+spectrum['counts']['stds']**2))/spectrum['exposure_in_ms']
    spectrum['avg_signal_filtered'] = np.abs(medfilt(spectrum['avg_signal'],3))
    spectrum['waves'] = spectrum['counts']['waves']
    waves = spectrum['waves']
    spectrum['energies'] = 1240./spectrum['waves']
    energies = spectrum['energies']
    spectrum['times'] = np.mean(spectrum['bkg']['offset_timetags'][:spectrum['frames_per_rep']],axis=1)/1000.

    # figures
    spectrum['figs'] = {}
    axis_label_fontsize = 15
    tick_labels_fontsize = 13

    # counts histograms
    fig, ax = plt.subplots(nrows=2, ncols=1,figsize=(fig_width,fig_width))
    min_counts = np.percentile(spectrum['bkg']['avg_rate'].flatten()*spectrum['exposure_in_ms'],5)
    max_counts = np.percentile(spectrum['bkg']['avg_rate'].flatten()*spectrum['exposure_in_ms'],95)
    min_signal = np.percentile(spectrum['avg_signal_filtered'].flatten()*spectrum['exposure_in_ms'],5)
    max_signal = np.percentile(spectrum['avg_signal_filtered'].flatten()*spectrum['exposure_in_ms'],95)
    signal_bins = np.linspace(min_signal,max_signal,80)
    bins = np.linspace(min_counts,max_counts,80)
    ax[0].hist(spectrum['counts']['avg_rate'].flatten()*spectrum['exposure_in_ms'],
             label='counts',bins=bins,histtype='step',color='blue')
    ax[0].hist(spectrum['bkg']['avg_rate'].flatten()*spectrum['exposure_in_ms'],
             label='background',bins=bins,histtype='step',color='red')
    ax[0].legend()
    ax[0].set_xlabel('Counts during exposure',fontsize=axis_label_fontsize)
    ax[0].set_ylabel('Frequency',fontsize=axis_label_fontsize)
    ax[0].tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax[0].tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax[0].set_xlim(min_counts,max_counts)
    ax[1].hist(spectrum['avg_signal_filtered'].flatten()*spectrum['exposure_in_ms'],
             label='counts - background',bins=signal_bins,histtype='step',color='black')
    ax[1].legend()
    ax[1].set_xlabel('Counts during exposure',fontsize=axis_label_fontsize)
    ax[1].set_ylabel('Frequency',fontsize=axis_label_fontsize)
    ax[1].tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax[1].tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax[1].set_xlim(min_signal,max_signal)
    ax[1].set_yscale('log')
    if save_figs:
        figname = '%s-countshist-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
        print(figname)
        fig.savefig(figname)
        pil_img = Image(filename=figname)
        display(pil_img)
        spectrum['figs']['counts_histograms'] = fig
    else:
        plt.show()

    # rainbow plot
    rainbow = np.array([wav2RGB(wave) for idx, wave in enumerate(waves)])
    imshow_height = 0.5*fig_width
    aspect_ratio = (max(waves)-min(waves))/spectrum['times'][-1]*imshow_height/fig_width
    extent = [min(waves),max(waves),0,spectrum['times'][-1]]
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,imshow_height))
    ax.imshow([waves],
              extent=extent,
              origin='lower',
              cmap=ListedColormap(rainbow))

    spectacular = np.copy(spectrum['avg_signal_filtered'])
    spectacular = spectacular/np.max(spectacular)

    illum_idx = np.argmin(np.abs(spectrum['bkg']['offset_timetags'][:,0][:spectrum['frames_per_rep']]-spectrum['excitation_duration_in_s']*1e6))
    spectrum['illum_idx'] = illum_idx
    steady = np.mean(spectrum['avg_signal_filtered'][:illum_idx],axis=0)
    spectrum['steady_spectrum'] = steady
    spectrum['steady_spectrum_std'] = np.std(spectrum['avg_signal_filtered'][:illum_idx],axis=0)/np.sqrt(illum_idx)

    vacuum = np.array([[[0,0,0,1-c] for c in b] for b in spectacular])
    ax.imshow(vacuum,
               extent=extent,
               origin='lower',
               aspect=aspect_ratio)
    ax.plot([spectrum['waves'][0],spectrum['waves'][-1]],
             [spectrum['excitation_duration_in_s']*1000]*2,
            'r--',alpha=0.85)
    ax.set_xlabel('$\lambda$/nm',fontsize=18)
    ax.set_ylabel('t / ms',fontsize=18)
    ax.tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax.tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax.plot(waves,steady/max(steady)*1,'w--')
    if save_figs:
        figname = '%s-rainbow-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
        print(figname)
        plt.tight_layout()
        fig.savefig(figname)
        pil_img = Image(filename=figname)
        display(pil_img)
        spectrum['figs']['rainbow'] = fig
    else:
        plt.show()

    # logplot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width, imshow_height))
    spectacular = np.abs(medfilt(spectrum['avg_signal'],3))
    ax.imshow(spectacular,
               extent=[min(waves),max(waves),0,spectrum['bkg']['offset_timetags'][spectrum['frames_per_rep']-1][-1]/1000.],
               aspect=aspect_ratio,
               origin='lower',
               cmap='gray',
               norm=LogNorm(vmin=100,vmax=1e5))
    ax.plot([spectrum['counts']['waves'][0],spectrum['counts']['waves'][-1]],
             [spectrum['excitation_duration_in_s']*1000]*2,
            'r--',alpha=0.85)
    ax.set_xlabel('$\lambda$/nm',fontsize=axis_label_fontsize)
    ax.tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax.set_ylabel('t / ms',fontsize=axis_label_fontsize)
    ax.tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax.plot(waves,steady/max(steady)*2,'b--')
    figname = '%s-logplot-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
    print(figname)
    plt.tight_layout()
    if save_figs:
        fig.savefig(figname)
        pil_img = Image(filename=figname)
        display(pil_img)
        spectrum['figs']['logscale'] = fig
    else:
        plt.show()

    # logscale spectrum
    spectrum['steady_spectrum_energy'] = spectrum['steady_spectrum']/(waves**2)
    spectrum['steady_spectrum_energy_std'] = spectrum['steady_spectrum_std']/(waves**2)
    fig, ax = plt.subplots(figsize=(fig_width,fig_width/3))
    ax.fill_between(spectrum['waves'],
                    spectrum['steady_spectrum']-2*spectrum['steady_spectrum_std'],
                    spectrum['steady_spectrum']+2*spectrum['steady_spectrum_std'],
                    color='red',alpha=0.4)
    ax.plot(spectrum['waves'],
                    spectrum['steady_spectrum'],'b-',ms=1)
    ax.set_xlim(spectrum['waves'][0],spectrum['waves'][-1])
    ax.set_xlabel('$\lambda$/nm',fontsize=axis_label_fontsize)
    ax.set_ylabel('Avg. Count Rate / kcps',fontsize=axis_label_fontsize)
    ax.tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax.tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax.set_yscale('log')
    plt.tight_layout()
    if save_figs:
        figname = '%s-logspec-nm-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
        print(figname)
        fig.savefig(figname)
        pil_img = Image(filename=figname)
        display(pil_img)
        spectrum['figs']['logspectrum-nm'] = fig
    else:
        plt.show()
    # logscale spectrum
    spectrum['steady_spectrum_energy'] = spectrum['steady_spectrum']/(waves**2)
    spectrum['steady_spectrum_energy_std'] = spectrum['steady_spectrum_std']/(waves**2)
    fig, ax = plt.subplots(figsize=(fig_width,fig_width/3))
    ax.fill_between(spectrum['energies'],
                    spectrum['steady_spectrum_energy']-2*spectrum['steady_spectrum_energy_std'],
                    spectrum['steady_spectrum_energy']+2*spectrum['steady_spectrum_energy_std'],
                    color='red',alpha=0.4)
    ax.plot(spectrum['energies'],
                    spectrum['steady_spectrum_energy'],'b-',ms=1)
    ax.set_xlim(spectrum['energies'][-1],spectrum['energies'][0])
    ax.set_xlabel('E/eV',fontsize=axis_label_fontsize)
    ax.set_ylabel('Avg. Count Rate / kcps',fontsize=axis_label_fontsize)
    ax.tick_params(axis='y',labelsize=tick_labels_fontsize)
    ax.tick_params(axis='x',labelsize=tick_labels_fontsize)
    ax.set_yscale('log')
    plt.tight_layout()
    if save_figs:
        figname = '%s-logspec-ev-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
        print(figname)
        fig.savefig(figname)
        pil_img = Image(filename=figname)
        display(pil_img)
        spectrum['figs']['logspectrum-ev'] = fig
    else:
        plt.show()
    if lifetime_regression:
        # wave-dep lifetime calcs
        def slice_and_fit(center_wave, pad_px):
            def lifetime_fit(t,tau,A,B):
                return A*np.exp(-(t)/tau)+B
            center_wave_idx = np.argmin(np.abs(spectrum['counts']['waves']-center_wave))
            cake_slice = medfilt(spectrum['avg_signal'],3)[:,center_wave_idx-pad_px:center_wave_idx+pad_px+1]
            totalo = np.abs(np.sum(cake_slice,axis=1))
            the_times = spectrum['times']

            good_times_idx = the_times>=(spectrum['excitation_duration_in_s']*1000)
            good_times = the_times[good_times_idx]
            good_times = good_times-good_times[0]
            good_counts = totalo[good_times_idx]

            not_null_counts_idx = (good_counts != 0)
            good_counts = good_counts[not_null_counts_idx]
            good_times = good_times[not_null_counts_idx]
            sigmas = np.sqrt(good_counts)

            opt_params, opt_cov = curve_fit(lifetime_fit,
                           good_times,
                           good_counts,
                           sigma=sigmas,
                           p0=np.array([1.,max(totalo),totalo[-10]]))
            good_fit = lifetime_fit(good_times,*opt_params)
            par_error =  np.sqrt(np.diag(opt_cov))
            return opt_params, par_error, good_fit, good_times, good_counts
        center_waves = np.linspace(min(waves),max(waves),int(len(waves)/3))
        lifetimes, lifeerrors = [], []
        pad_px = pad_size
        for center_wave in center_waves:
            try:
                fit = slice_and_fit(center_wave,pad_px)
                lifetime = fit[0][0]
                lifeerror = fit[1][0]
                lifetimes.append(lifetime)
                lifeerrors.append(lifeerror)
            except:
                lifetimes.append(np.nan)
                lifeerrors.append(np.nan)
        lifetimes = np.array(lifetimes)
        lifeerrors = np.array(lifeerrors)
        spectrum['lifetimes'] = {}
        spectrum['lifetimes']['lifetimes'] = lifetimes
        spectrum['lifetimes']['errors'] = lifeerrors
        lifetimes[lifeerrors>0.5] = np.nan
        lifeerrors[lifeerrors>0.5] = np.nan
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(fig_width,fig_width/13*3))
        ax.plot(center_waves,lifetimes,label='lifetime')
        ax.plot(waves,(steady/max(steady)),'k-',label='CW spectrum')
        # plt.plot(waves[waves>570],10*(steady[waves>570]/max(steady[waves<570])),'k-',label='CW spectrum X 10')
        ax.fill_between(center_waves,lifetimes-2*lifeerrors,lifetimes+2*lifeerrors,alpha=0.5)
        ax.set_ylim(0,1.5)
        ax.set_xlim(min(center_waves),max(center_waves))
        ax.set_xlabel('$\lambda$/nm',fontsize=axis_label_fontsize)
        ax.set_ylabel('$\\tau$/ms',fontsize=axis_label_fontsize)
        ax.tick_params(axis='y',labelsize=tick_labels_fontsize)
        ax.tick_params(axis='x',labelsize=tick_labels_fontsize)
        plt.legend()
        plt.tight_layout()
        if save_figs:
            figname = '%s-%d.jpg' % (spectrum['experiment_name'], int(time.time()))
            print(figname)
            fig.savefig(figname)
            pil_img = Image(filename=figname)
            display(pil_img)
            spectrum['figs']['lifetime'] = fig
        else:
            plt.show()
    return spectrum

def quick_loader_with_stats(snippet, spec):
    '''snippet is either bkg or counts'''
    spe = spec[snippet]['spe']
    frames = spec['frames_to_save']
    reps = spec['reps']
    sensor_width = spec['sensor_width']
    frames_per_rep = spec['frames_per_rep']
    with open(os.path.join(spe['dir'],spe['fname'])) as file:
        # load frames, and compute statistics
        file.seek(4100)
        dtype = [('',np.uint16) for i in range(sensor_width)] +[('',np.uint64),('',np.uint64),('',np.uint64)]
        data = np.fromfile(file, dtype, count = frames)
        counts = np.array([np.mean((data['f%d'%i]).reshape(reps,frames_per_rep),axis=0) for i in range(sensor_width)]).T
        counts_std = np.array([np.std((data['f%d'%i]).reshape(reps,frames_per_rep),axis=0) for i in range(sensor_width)]).T/np.sqrt(spec['reps'])
        timetags = np.array([data['f%d'%i] for i in range(sensor_width,sensor_width+2)]).T
        # fullframes = np.array([(data['f%d'%i]).reshape(reps,frames_per_rep) for i in range(sensor_width)]).T
        # load wavelength info from footer
        file.seek(678)
        footer_pos = np.fromfile(file,np.uint64,8)[0] #read_at(file, 678, 8, np.uint64)[0]
        file.seek(footer_pos)
        xmltext = file.read()
        parser = untangle.make_parser()
        sax_handler = untangle.Handler()
        parser.setContentHandler(sax_handler)
        parser.parse(StringIO(xmltext))
        loaded_footer = sax_handler.root
        wavelength_string = StringIO(loaded_footer.SpeFormat.Calibrations.WavelengthMapping.Wavelength.cdata)
        wavelength = np.loadtxt(wavelength_string, delimiter=',')
    return counts, timetags, wavelength, counts_std
