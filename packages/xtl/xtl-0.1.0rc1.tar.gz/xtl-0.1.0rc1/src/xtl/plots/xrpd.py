from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


origin_q13 = ['#515151', '#F14040', '#1A6FDF', '#37AD6B', '#B177DE', '#CC9900', '#00CBCC', '#7D4E4E', '#8E8E00',
              '#FB6501', '#6699CC', '#6FB802']


class XRPDProfilePlot:

    def __init__(self, x, yobs, ycalc=None, yback=None, erry=None, hkl=None, d_spacings=None, wavelength=None):
        self._x = x
        self._yobs = yobs
        self._ycalc = ycalc
        self._yback = yback
        self._erry = erry
        self._hkl = hkl
        self._d_spacings = d_spacings
        self._wavelength = wavelength

    def plot(self, subtract_background=True):
        x = self._x
        yo, yc, yb = self._yobs, self._ycalc, self._yback
        if subtract_background and yb is not None:
            yo = yo - yb
            if yc is not None:
                yc = yc - yb

        iobs, icalc, diff, hkls = None, None, None, None
        iobs = go.Scatter(x=x, y=yo, mode='lines',
                          line={'color': origin_q13[0], 'width': 1}, name='I<sub>obs</sub>')
        if yc is not None:
            icalc = go.Scatter(x=x, y=yc, mode='lines',
                               line={'color': origin_q13[1], 'width': 1}, name='I<sub>calc</sub>')
            diff = go.Scatter(x=x, y=yo-yc, mode='lines',
                              line={'color': origin_q13[2], 'width': 1}, name='I<sub>obs</sub> - I<sub>calc</sub>')
        if self._hkl is not None:
            hkls = go.Scatter(x=self._hkl[3], y=np.zeros_like(self._hkl[3]), mode='markers',
                              marker={'symbol': 'line-ns', 'size': 10, 'line': {'width': 1}}, name='hkl')

        last_subplot = 0
        if icalc is None:
            fig = make_subplots(rows=1, cols=1)
            fig.add_trace(iobs)
            last_subplot = 1
        elif hkls is None:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0,
                                row_heights=[8.15, 1.85])
            fig.add_traces(data=[iobs, icalc, diff], rows=[1, 1, 2])
            last_subplot = 2
        else:
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0,
                                row_heights=[8, 0.3, 1.7])
            fig.add_traces(data=[iobs, icalc, hkls, diff], rows=[1, 1, 2, 3])
            last_subplot = 3



    @classmethod
    def from_highscoreplus(cls, anchor_scan_data, peak_list_data):
        scan_file = Path(anchor_scan_data)
        peak_file = Path(peak_list_data)

        for _file, _type in ((scan_file, 'anchor scan'), (peak_file, 'peak')):
            if not _file.exists():
                raise FileNotFoundError(f'Could not find {_type} data file: {_file}')

        scan_data = pd.read_csv(scan_file, delimiter='\t')
        _x2theta, _xd, _yobs, _ycalc, _yback, _erry = None, None, None, None, None, None
        if 'Pos. [°2θ]' in scan_data.columns:
            _x2theta = scan_data['Pos. [°2θ]']
        if 'D spacings' in scan_data.columns:
            _xd = scan_data['D spacings']
        if 'Intensity [Counts]' in scan_data.columns:
            _yobs = scan_data['Intensity [Counts]']
        if 'Icalc [cts]' in scan_data.columns:
            _ycalc = scan_data['Icalc [cts]']
        if 'Iback [cts]' in scan_data.columns:
            _yback = scan_data['Iback [cts]']
        if 'ESD' in scan_data.columns:
            _erry = scan_data['ESD']

        peak_data = pd.read_csv(peak_file, delimiter='\t')
        _h, _k, _l, _xpeak_2theta, _xpeak_dspac = None, None, None, None, None
        if 'h' in peak_data.columns:
            _h = peak_data['h']
        if 'k' in peak_data.columns:
            _k = peak_data['k']
        if 'l' in peak_data.columns:
            _l = peak_data['l']
        if 'Pos. [°2θ]' in peak_data.columns:
            _xpeak_2theta = peak_data['Pos. [°2θ]']
        if 'd-spacing [Å]' in peak_data.columns:
            _xpeak_dspac = peak_data['d-spacing [Å]']

        _hkl = None
        if _h.any() and _k.any() and _l.any() and _xpeak_2theta.any():
            _hkl = pd.concat((_h, _k, _l, _xpeak_2theta), axis=1, names=['h', 'k', 'l', '2theta'])
            if _xpeak_dspac.any():
                _hkl = pd.concat((_hkl, _xpeak_dspac), axis=1, names=['h', 'k', 'l', '2theta', 'd-spacing'])
        if _hkl is None:
            print(f'Could not find hkls in {peak_file}')

        return cls(_x2theta, _yobs, _ycalc, _yback, _erry, _hkl, _xd)
